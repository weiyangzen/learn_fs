# sources/distributed-fs/ceph-client/drivers/infiniband/core/mad_rmpp.c

## Purpose
`mad_rmpp.c` implements Reliable Multi-Packet Protocol handling for kernel MAD agents. It segments outgoing RMPP data MADs, processes ACK windows, retries unacknowledged segments, reassembles inbound DATA segments, sends ACK/ABORT responses, and cleans up timed-out or completed receive transactions.

## Important APIs, types, and functions
- `struct mad_rmpp_recv` tracks one inbound RMPP transaction by agent, TID, source QP, SLID, class/version/method/base-version, AH, receive WC chain, current contiguous segment, ACK window, response window, delayed timeout/cleanup work, state, lock, and refcount.
- `ib_process_rmpp_recv_wc()` is the receive entry point from `mad.c`; it validates RMPP version and dispatches DATA, ACK, STOP, and ABORT packets.
- `ib_send_rmpp_mad()` starts active RMPP sends and returns whether normal MAD send handling should continue.
- `ib_process_rmpp_send_wc()` advances a segmented send after each send completion or tells `mad.c` to finish the public send completion.
- `ib_retry_rmpp()` rewinds to `last_ack` and resends from the next unacknowledged segment.
- `ib_cancel_rmpp_recvs()` cancels delayed work and tears down all receive transactions during agent unregister.
- Helpers such as `start_rmpp()`, `continue_rmpp()`, `complete_rmpp()`, `process_rmpp_ack()`, `abort_send()`, `ack_recv()`, `nack_recv()`, and `ack_ds_ack()` implement protocol mechanics.

## Control flow
Inbound DATA segment 1 with FIRST set creates a receive transaction, inserts it on the agent RMPP list, schedules a long timeout if more segments are expected, advances `newwin`, and sends an ACK. Later DATA segments look up the transaction, reject timed-out or out-of-window packets, insert the receive buffer in segment order, and update the contiguous segment cursor. When the LAST segment becomes contiguous, the code ACKs it, computes the final MAD length with IB or OPA payload sizing, marks the transaction complete, schedules cleanup, and returns a reassembled `ib_mad_recv_wc` to `mad.c`.

Inbound ACK packets validate status, segment number, and advertised window. They find the matching outbound send by the normal MAD response-matching logic, update `last_ack`, refresh retries, advance `newwin`, send additional segments when the current window permits, complete no-response sends after the final ACK, or reset the timeout to wait for a response. STOP and ABORT packets abort the matching send, preserving the remote RMPP status in the send WC vendor error.

Outbound active RMPP sends call `send_next_seg()`, which stamps ACTIVE, FIRST, LAST, segment number, and payload/new-window fields, then sends the segment with a short ACK timeout cap. Response sends initialize their window from a completed inbound receive's `repwin` when possible, allowing double-sided RMPP behavior.

## State and persistence
RMPP state is volatile and anchored to `ib_mad_agent_private->rmpp_list`. Receive transactions have three states: ACTIVE, TIMEOUT, and COMPLETE. A 40 second receive timeout aborts incomplete transfers with T2L status; completed transactions stay discoverable for 10 seconds so duplicate ACK and double-sided response handling can work. Each transaction has its own lock for segment/window state and shares the agent lock for list membership.

Outbound state lives in `ib_mad_send_wr_private`: `seg_num`, `last_ack`, `newwin`, `cur_seg`, `last_ack_seg`, retry counters, and timeout. RMPP does not persist data beyond the MAD send/receive lifetime.

## Dependencies and integration points
This file depends on `mad.c` for send posting, send completion, receive freeing, response matching, and timeout integration. It uses public MAD/RMPP headers, AH creation from WC information, RDMA AH destruction, and OPA capability checks for OPA RMPP payload length calculations. Client callbacks still occur through the MAD core after RMPP returns a completed receive WC or send WC.

## Risks
- Segment insertion and contiguous-cursor updates must tolerate duplicate, out-of-order, and old-window packets without leaking receive buffers.
- ACK processing can complete sends, send more segments, or generate ACKs for double-sided transfers; lock release points must avoid using stale send WRs.
- Timeout values are fixed approximations in this version, so slow fabrics can trigger aborts if tests assume packet-lifetime-derived timing.
- OPA and IB RMPP MAD sizes differ; payload length and padding calculations are easy to regress.
- Error paths that call both `nack_recv()` and `ib_free_recv_mad()` must not leave the transaction list with a freed receive WC.

## Test signals
- Exercise single-segment and multi-segment RMPP sends, including no-response sends that complete after final ACK.
- Inject duplicate first segments, duplicate ACKs, ACK window smaller than segment number, bad RMPP versions, bad status, out-of-window DATA, STOP, and ABORT packets.
- Validate timeout cleanup by unregistering an agent with active and completed RMPP receives.
- Test OPA base-version RMPP length calculation separately from classic 256-byte IB MADs.

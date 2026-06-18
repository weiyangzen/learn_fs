# sources/distributed-fs/ceph-client/drivers/infiniband/core/mad_rmpp.h

## Purpose
`mad_rmpp.h` is the private interface between the MAD core and the RMPP implementation. It keeps RMPP-specific return codes and function declarations out of the public RDMA MAD API while allowing `mad.c` to delegate segmented send/receive work.

## Important APIs, types, and functions
- The anonymous enum defines `IB_RMPP_RESULT_PROCESSED`, `IB_RMPP_RESULT_CONSUMED`, `IB_RMPP_RESULT_INTERNAL`, and `IB_RMPP_RESULT_UNHANDLED`. `mad.c` uses these values to decide whether to continue normal send completion, suppress completion because RMPP posted another segment, or call the internal RMPP send handler.
- `ib_send_rmpp_mad()` starts an outbound active DATA transfer.
- `ib_process_rmpp_recv_wc()` handles active inbound RMPP packets and returns either a completed receive WC or `NULL` when the packet was consumed.
- `ib_process_rmpp_send_wc()` advances outbound segmentation on send completion.
- `ib_rmpp_send_handler()` frees internally generated ACK/ABORT/STOP send buffers and their AHs.
- `ib_cancel_rmpp_recvs()` tears down inbound RMPP state on agent removal.
- `ib_retry_rmpp()` retries from the last acknowledged segment.

## Control flow
The header's contract is result-code driven. `mad.c` calls the send entry before normal send posting for active RMPP sends, calls the send-WC entry under the agent lock before public completion, and calls the receive-WC entry before invoking client receive callbacks. Return codes decide whether ownership remains with RMPP or returns to the regular MAD core.

## State and persistence
The header has no storage. It defines access to state held in `ib_mad_send_wr_private` and `ib_mad_agent_private` from `mad_priv.h`.

## Dependencies and integration points
It depends on the private MAD structs being visible before inclusion. It is included by both `mad.c` and `mad_rmpp.c` and should remain synchronized with the internal MAD state machine.

## Risks
- Changing return-code meanings without updating `mad.c` can double-post segments, double-complete sends, or leak internal send buffers.
- The prototypes intentionally expose private structs; type churn in `mad_priv.h` must be coordinated.

## Test signals
- Build tests catch signature drift.
- RMPP send/receive integration tests should assert each result-code path: unhandled normal MAD, consumed segment send, internal ACK/ABORT send, and processed completion.

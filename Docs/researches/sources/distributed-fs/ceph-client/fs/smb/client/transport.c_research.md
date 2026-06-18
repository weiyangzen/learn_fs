# sources/distributed-fs/ceph-client/fs/smb/client/transport.c

Read coverage: full file.

## Purpose
`transport.c` is the SMB client transport core. It sends request vectors over TCP or SMB Direct, manages MIDs and response waits, enforces SMB credit flow control, drives synchronous and asynchronous request lifecycles, handles compound request completion, chooses multichannel transports, and receives read response payloads into netfs I/O iterators.

## Important APIs, types, and functions
MID lifecycle helpers include `cifs_wake_up_task`, `__release_mid`, and `delete_mid`. Socket send helpers are `smb_send_kvec`, `smb_rqst_len`, `__smb_send_rqst`, and the wrapper `smb_send_rqst`, which adds compression or encryption transform headers. Credit management is implemented by `wait_for_free_credits`, `wait_for_free_request`, `wait_for_compound_request`, and `cifs_wait_mtu_credits`. Request APIs include `cifs_call_async`, `compound_send_recv`, and `cifs_send_recv`. Receive helpers include `cifs_sync_mid_result`, `wait_for_response`, `cifs_discard_remaining_data`, and `cifs_readv_receive`. `cifs_pick_channel` selects a session channel with the lowest observed in-flight load.

## Control flow
Sends start by acquiring credits, locking the server, setting up MIDs through dialect-specific `server->ops`, queuing them on `pending_mid_q`, saving send timestamps, and calling `smb_send_rqst`. The low-level TCP path writes an RFC1002 length marker, then all request kvecs and optional iter data, while signals are masked to avoid partial-SMB interruption. Partial sends trigger reconnect because subsequent bytes could be misparsed as the remainder of the previous PDU. The SMB Direct path delegates to `smbd_send`; compression delegates to `smb_compress`; encrypted requests build a transform request through `init_transform_rq`.

Synchronous compound calls set callbacks on every MID, send the chain in one socket-serialized sequence, wait for responses, cancel unfinished waits on interruption, validate each response with `check_receive`, and hand response buffers back to callers. Async calls set a callback/receive/handle tuple and return after a successful send. Read receive flow parses the read response header, handles session expiry and pending status, validates data offset and length, copies socket data into the target iterator or accounts RDMA memory registration data, discards trailing frame bytes, then dequeues the MID.

## State and persistence behavior
The file mutates server credit fields, `in_flight`, `max_in_flight`, reconnect instance, sequence numbers, pending MID queues, response buffers, `server->total_read`, and read subrequest byte counters. MID state transitions include submitted, response received, response ready, retry, malformed, shutdown, rc, and free. It updates statistics under `CONFIG_CIFS_STATS2`, including fastest/slowest command latency and slow response counters. No on-disk state is persisted, but network-visible sequencing and credit consumption are persistent protocol state.

## Dependencies and integration points
This code is tightly integrated with `cifsglob.h`, `cifsproto.h`, dialect-specific `server->ops`, SMB2 preauth hashing, SMB Direct, compression, transform/encryption, socket APIs, kernel wait queues, spinlocks, task work, and netfs read subrequests. Tracepoints from `trace.h` report slow responses, credit waits, insufficient credits, partial send reconnects, and malformed read frames.

## Risks and test signals
High-risk areas are partial send handling, credit starvation/deadlock, reconnect-instance races after credits are acquired, compound cancellation, buffer ownership when `resp_iov` takes `mid->resp_buf`, and malformed read response length/offset validation. Multichannel selection intentionally reads `in_flight` without `req_lock`, so tests should tolerate non-perfect load balancing. Test signals include xfstests over SMB2/SMB3 with signing/encryption/compression, forced reconnect during sends, signal interruption of synchronous requests, compound create/query/close flows, RDMA read coverage, credit exhaustion, and tracefs credit/partial-send events.

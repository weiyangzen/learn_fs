# sources/distributed-fs/ceph-client/fs/smb/client/smb1transport.c

## Purpose

This file implements the SMB1/CIFS transport-side request setup, response validation, synchronous send/receive wrappers, and special handling for multi-response Transaction2 replies. It sits between higher-level SMB1 operations in `cifssmb.c`/`smb1ops.c` and the generic CIFS transport engine in `transport.c`, providing SMB1-specific MID allocation, signing checks, response copying, and frame sanity checks.

## Important APIs, types, and functions

- `alloc_mid()` initializes a `struct mid_q_entry` from an SMB1 header: MID, PID, command, allocation timestamp, refcount, callback, creator task, and initial `MID_REQUEST_ALLOCATED` state.
- `allocate_mid()` gates request allocation against `cifs_ses::ses_status`, allowing only negotiate/session-setup while new and only logoff while exiting, then appends the MID to `server->pending_mid_q`.
- `cifs_setup_async_request()` and `cifs_setup_request()` prepare signed SMB1 requests. The synchronous path allocates and queues the MID; the async path allocates and signs but leaves queueing to the caller.
- `SendReceiveNoRsp()`, `SendReceive2()`, and `SendReceive()` are compatibility wrappers over `cifs_send_recv()`.
- `cifs_check_receive()` dumps and verifies received SMB1 responses, including signature validation when signing is enabled, then maps SMB errors.
- `check2ndT2()`, `coalesce_t2()`, and `cifs_check_trans2()` detect and merge fragmented Transaction2 responses.
- `checkSMB()` validates SMB1 wire frames against protocol signature, header/word-count/bcc sizes, RFC1001 length, calculated SMB size, and tolerated server quirks.

## Control flow

The common send path builds an `smb_rqst`, allocates a MID, signs the request through `cifs_sign_rqst()`, sends through `cifs_send_recv()`, and later checks the received response through `cifs_check_receive()` or the server operation table. `SendReceive()` additionally copies the response into the caller's output buffer and frees the transport-owned response buffer.

Multi-part Transaction2 handling is stateful: `check2ndT2()` identifies whether more data is expected; `cifs_check_trans2()` marks `mid->multiRsp`, captures the first large buffer if needed, and calls `coalesce_t2()` for later fragments. When the last fragment arrives, it sets `mid->multiEnd` and dequeues the MID.

## State and persistence behavior

The file updates in-memory transport/session state only. Important state includes `pending_mid_q`, `mid_count`, `mid->multiRsp`, `mid->multiEnd`, `mid->resp_buf`, `mid->large_buf`, `server->bigbuf`, and signing sequence numbers. It does not persist to disk. Memory ownership is explicit: response buffers are returned through `resp_iov` and released with `free_rsp_buf()`, while Transaction2 coalescing may transfer `server->bigbuf` ownership to `mid->resp_buf`.

## Dependencies and integration points

It depends on CIFS core types from `cifsglob.h`, request helpers from `cifsproto.h`, SMB1 declarations from `smb1proto.h`, shared SMB2 signing declarations, `smbdirect.h`, compression hooks, and trace/error helpers. It is wired into SMB1 through declarations in `smb1proto.h` and the SMB1 operation table (`smb1ops.c` uses `checkSMB`). Higher-level SMB1 commands call `SendReceive*()` throughout `cifssmb.c`.

## Risks and edge cases

Frame validation is security-sensitive because malformed lengths can otherwise cause out-of-bounds reads or writes. The Transaction2 coalescing path must keep `DataCount`, BCC, and PDU length synchronized and must reject oversized totals. Session state gating returns `-EAGAIN` for requests sent during setup/teardown, so callers must tolerate retry. Signature verification reconnects opportunistically only when signing is not required; required-signing failures propagate. `SendReceive()` copies into caller-provided `out_buf` without checking that the caller allocated enough for `resp_iov.iov_len`, so the contract relies on legacy callers passing an adequate buffer.

## Test signals

There is no direct KUnit file for this source in this subset. Useful validation signals are SMB1 mount smoke tests, signing-required mounts, request cancellation/reconnect tests, and SMB1 Transaction2 directory/query tests that force secondary responses. Fuzzing or packet-replay tests should target `checkSMB()` length combinations and `coalesce_t2()` count/offset arithmetic.

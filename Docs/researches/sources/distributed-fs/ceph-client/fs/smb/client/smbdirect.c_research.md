# sources/distributed-fs/ceph-client/fs/smb/client/smbdirect.c

## Purpose
`smbdirect.c` adapts the Linux SMBDirect socket API to the CIFS client. It creates, reconnects, destroys, sends, receives, registers memory, deregisters memory, and reports debug state for SMB over RDMA transports.

## Important APIs, Types, And Functions
Global tunables define initial SMBD credits, max send/receive sizes, fragmented receive size, keepalive interval, maximum FRMR depth, and the RDMA read/write threshold. Module parameters `smbd_logging_class` and `smbd_logging_level` control class-based logging.

Exported functions are `smbd_get_connection`, `smbd_get_parameters`, `smbd_reconnect`, `smbd_destroy`, `smbd_recv`, `smbd_send`, `smbd_register_mr`, `smbd_mr_fill_buffer_descriptor`, `smbd_deregister_mr`, and `smbd_debug_proc_show`. Internal helpers include `_smbd_get_connection`, `smbd_post_send_full_iter`, `smbd_logging_needed`, and `smbd_logging_vaprintf`.

## Control Flow
Connection setup builds `smbdirect_socket_parameters` from tunables, chooses port-specific transport restrictions, creates a kernel SMBDirect socket, installs logging callbacks, applies initial parameters and polling settings, rewrites the destination port, and connects synchronously. `smbd_get_connection` first tries port 5445 and falls back to port 445, then clamps `server->rdma_readwrite_threshold` to the negotiated maximum fragmented send size.

Send flow calculates the combined SMB payload length across `smb_rqst` objects, rejects payloads above negotiated maximum, builds a send batch, sends metadata kvecs and payload iterators in chunks that respect negotiated max-send size, flushes the batch, and waits for pending sends to drain. Receive flow delegates to `smbdirect_connection_recvmsg` after checking connection state.

## State And Persistence Behavior
The only local connection state is `struct smbd_connection`, which owns a `struct smbdirect_socket *`. `server->smbd_conn` is installed, destroyed, or replaced during reconnect. RDMA threshold state is persisted in `TCP_Server_Info`. Memory registration state is owned by `struct smbdirect_mr_io` objects and must be deregistered by IO completion paths.

## Dependencies And Integration Points
This file depends on `linux/smbdirect.h`, CIFS debug/proto helpers, `smb2proto.h`, and the `SMBDIRECT` namespace. It is called by CIFS connection setup/reconnect, low-level receive/send paths, `/proc` debug reporting, and SMB2 read/write RDMA offload in `smb2pdu.c`.

## Risks
The send path assumes upper layers never exceed negotiated fragmented send size and returns `-EINVAL` if they do. Connection setup mutates the destination sockaddr port in place. Batch flush and wait-zero-pending semantics are critical under error paths. MR exhaustion is a risk if callers fail to deregister promptly. Logging knobs can become noisy under class masks.

## Test Signals
Exercise connection fallback from 5445 to 445, disconnected send/recv returning retryable errors, large fragmented sends near negotiated limits, RDMA threshold clamping, read/write offload MR registration/deregistration, reconnect replacement of `server->smbd_conn`, and `/proc` debug output for RDMA and non-RDMA mounts.

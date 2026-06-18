# sources/cloud-native/nydus/storage/src/remote/connection.rs

## Purpose
Provides Unix-domain-socket listener and endpoint primitives for remote blob-manager control messages, including scatter/gather IO and file descriptor passing.

## Important APIs, Types, And Functions
`Error` classifies protocol, socket, fd, and handler failures and exposes `should_reconnect()`. `Listener` wraps `UnixListener` with optional unlink-on-create/drop, nonblocking mode, and accept handling. `Endpoint` wraps `UnixStream` and supports connect/close, `send_iovec(_all)`, `send_slice`, `send_header`, `send_message`, `send_message_with_payload`, `recv_data`, unsafe iovec receives, and typed header/body/payload receive helpers. `get_sub_iovs_offset()` maps a byte count into an iovec index and offset.

## Control Flow
Send helpers serialize headers and bodies by creating byte slices from `ByteValued`-style structs and loop through partial writes, attaching fds only on the first send attempt. Receive helpers use `recvmsg` through `ScmSocket`, convert received fds into owned `File`s, and loop until the requested iovec lengths are filled. Header/body helpers validate `MsgHeader` and message bodies before returning.

## State And Persistence
No durable persistence. `Listener` owns a socket path and removes it on drop when it created the path. `Endpoint` owns a Unix stream and can receive owned file descriptors that become `File` instances.

## Dependencies And Integration Points
Uses `dbs_uhttp::ScmSocket` for fd passing, libc `iovec`, `UnixListener`/`UnixStream`, `vm_memory::ByteValued`, and `remote::message` validators/constants. `remote/client.rs` uses `Endpoint` for request/reply communication with the remote blob manager.

## Risks
The file deliberately exposes unsafe receive APIs where callers must provide writable iovec memory. File descriptor passing over stream sockets requires receive calls to respect message boundaries or fds can be lost; the implementation documents this and tests several boundary cases. Extra fds beyond `MAX_ATTACHED_FD_ENTRIES` are silently discarded by design. `Listener::set_nonblocking(&self, block: bool)` passes its argument directly to `set_nonblocking`, so the parameter name is misleading.

## Test Signals
Tests cover listener creation/from-raw-fd, nonblocking accept without connections, data send/receive, fd passing under multiple boundary patterns and platform differences, extra-fd truncation behavior, and typed send/receive of headers and bodies. Source size reviewed: 1,049 lines.

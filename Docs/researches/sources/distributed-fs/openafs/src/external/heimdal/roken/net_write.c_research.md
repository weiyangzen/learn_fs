# sources/distributed-fs/openafs/src/external/heimdal/roken/net_write.c

## Purpose
Implements `net_write`, a companion to `net_read` that keeps writing until the requested buffer length has been sent or an error occurs.

## Important APIs, Types, And Functions
The exported function is `net_write(rk_socket_t fd, const void *buf, size_t nbytes)`. Unix builds use `write`; Windows builds use `send`, with optional fallback to `_write` under `SOCKET_IS_NOT_AN_FD`.

## Control Flow
The function maintains a remaining byte count and advances the buffer pointer after every successful write. Unix retries interrupted writes. Windows first tries socket I/O and switches permanently to `_write` when the handle appears not to be a WinSock socket. On any non-retryable negative result it returns that error; otherwise it returns `nbytes` after the full buffer is transmitted.

## State And Persistence
There is no persistent state. The side effect is network or descriptor output. The function does not frame data, flush streams, or close descriptors.

## Dependencies And Integration Points
The helper depends on roken's `rk_socket_t`, socket-error macros, and platform I/O headers. It is declared in `roken.h` for portable protocol code.

## Risks And Test Signals
The helper can block indefinitely on blocking descriptors. On Windows, the error retry branch checks `errno == EINTR` rather than `rk_SOCK_ERRNO`, which matters outside the `_write` fallback path. Tests should exercise partial writes, EINTR, closed peer errors, zero-byte writes, and fallback behavior with file descriptors on Windows.

# sources/distributed-fs/openafs/src/external/heimdal/roken/net_read.c

## Purpose
Implements `net_read`, a blocking helper that attempts to read exactly the requested byte count from a socket or file descriptor, returning early only on EOF or error.

## Important APIs, Types, And Functions
The exported function is `net_read(rk_socket_t fd, void *buf, size_t nbytes)`. Unix builds call `read`; Windows builds call `recv`, and under `SOCKET_IS_NOT_AN_FD` can fall back to `_read` when WinSock reports an uninitialized or non-socket handle.

## Control Flow
The function loops while bytes remain, advancing a character pointer by each successful read. Unix retries `EINTR`; Windows deliberately does not retry WinSock `WSAEINTR`, since that can mean a blocking call was cancelled. A zero-length read returns zero immediately, signaling peer close or EOF rather than returning a partial byte count.

## State And Persistence
There is no persistent state. The only side effect is filling the caller-provided buffer with consecutive bytes read from the descriptor.

## Dependencies And Integration Points
It depends on roken socket abstraction macros from `roken.h` and is declared there as a general utility for network protocol code that needs full-record reads.

## Risks And Test Signals
Callers must be prepared for all-or-zero/error behavior; a short read followed by EOF is reported as zero, not the number already copied. Blocking sockets can hang until all requested bytes arrive. Tests should cover EINTR retry on Unix, EOF mid-record, WinSock fallback paths, and exact-size reads over sockets and pipes.

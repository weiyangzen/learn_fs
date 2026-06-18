# sources/distributed-fs/beegfs/client_module/source/common/toolkit/SocketTk.h

## Purpose
Declares socket toolkit APIs and the small `PollState` abstraction used by BeeGFS socket code.

## Important APIs and types
Exports one-time init/uninit, `SocketTk_poll`, address parsing/formatting functions, and endpoint formatting. `PollState` wraps a `list_head`; inline helpers initialize it and append sockets with requested events while resetting `revents`. `Socket_formatAddrOrPeername` formats a supplied source address or falls back to `sock->peername` into the socket's temporary buffer.

## State, dependencies, integration
The header depends on BeeGFS `Socket`, `Time`, and Linux poll types. It integrates with standard and RDMA socket implementations and log formatting.

## Risks and test signals
`Socket_formatAddrOrPeername` uses a socket-owned temp buffer and explicitly is not concurrency-safe. Tests should cover repeated formatting on the same socket, adding multiple sockets to a poll state, and ensuring callers initialize `PollState` before use.

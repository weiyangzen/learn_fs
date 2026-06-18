# sources/distributed-fs/ceph-client/net/tipc/diag.c

## Purpose

`diag.c` implements the SOCK_DIAG handler for TIPC sockets. It lets userspace request AF_TIPC socket diagnostic dumps through `NETLINK_SOCK_DIAG`, producing per-socket information via the existing TIPC socket diag filler.

## Important APIs, Types, and Functions

`__tipc_diag_gen_cookie()` converts the generic socket diag cookie into a `u64` for TIPC reporting. `__tipc_add_sock_diag()` creates a netlink answer message and delegates body population to `tipc_sk_fill_sock_diag()`. `tipc_diag_dump()` walks sockets through `tipc_nl_sk_walk()`. `tipc_sock_diag_handler_dump()` validates request size and starts a netlink dump using `tipc_dump_start`, `tipc_diag_dump`, and `tipc_dump_done`. Module init/exit register and unregister `tipc_sock_diag_handler`.

## Control Flow

Userspace sends a `tipc_sock_diag_req`. The handler rejects undersized requests and supports only dump requests (`NLM_F_DUMP`). The generic netlink dump framework then repeatedly calls `tipc_diag_dump()`, which walks TIPC sockets and calls `__tipc_add_sock_diag()` for each matching socket. Each result is a multipart `SOCK_DIAG_BY_FAMILY` response.

## State and Persistence Behavior

The module maintains no persistent per-socket state. It registers one static `sock_diag_handler` for `AF_TIPC` and reads socket state while walking. The cookie is derived from the socket's saved diag cookie and is stable enough for diag consumers within normal socket lifetime constraints.

## Dependencies and Integration Points

The file depends on `core.h`, `socket.h`, Linux `sock_diag`, and `linux/tipc_sockets_diag.h`. It integrates with TIPC socket walking/filling helpers and the global SOCK_DIAG registry. The module metadata exposes a netlink alias for AF_TIPC diagnostic support.

## Risks and Edge Cases

The main risks are netlink sizing and dump iteration correctness. `nlmsg_put_answer()` or `tipc_sk_fill_sock_diag()` failures must return `-EMSGSIZE` or the underlying error so dump replay can continue correctly. Only dump mode is supported; point queries return `-EOPNOTSUPP`.

## Test Signals

Run `ss` or a SOCK_DIAG client against AF_TIPC sockets, including many sockets to force multipart dumps. Validate short request rejection, module load/unload registration, and group socket diagnostics when `group.c` contributes nested group attributes.

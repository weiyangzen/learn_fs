# sources/distributed-fs/ceph-client/net/tipc/net.h

## Purpose
`net.h` declares the TIPC network identity/lifecycle API and the netlink policy used to configure it. It is the small public contract for `net.c`.

## Important APIs, Types, And Functions
The header includes generic netlink definitions, exports `tipc_nl_net_policy[]`, and declares `tipc_net_init()`, `tipc_net_finalize_work()`, `tipc_net_stop()`, `tipc_nl_net_dump()`, `tipc_nl_net_set()`, `__tipc_nl_net_set()`, and `tipc_nl_net_addr_legacy_get()`.

## Control Flow
There is no executable flow in the header. Callers use `tipc_net_init()` to set node identity/address, `tipc_net_finalize_work()` as a workqueue callback for deferred address finalization, `tipc_net_stop()` for namespace shutdown, and the netlink functions as generic-netlink command handlers or compatibility-layer targets.

## State And Persistence
The header owns no storage. It exposes functions that mutate per-net `struct tipc_net` identity fields, legacy-address mode, and network-mode subsystem state.

## Dependencies And Integration Points
It is included by `net.c`, `node.c`, `netlink.c`, `netlink_compat.c`, and other TIPC modules that need lifecycle or configuration entry points. `__tipc_nl_net_set()` is intentionally exported for the legacy compatibility layer, while `tipc_nl_net_set()` wraps it in RTNL locking for normal netlink operation.

## Risks And Edge Cases
The split between locked and unlocked netlink setters is easy to misuse; callers of the double-underscore form must provide required serialization. Policy declarations must stay aligned with `netlink.c` and user-visible TIPC attributes. Network identity changes have broad side effects and should remain centralized in `net.c`.

## Test Signals
Compile coverage for all netlink handlers, lockdep checks around compatibility calls to `__tipc_nl_net_set()`, and netlink API tests for get/set/legacy status validate this header.

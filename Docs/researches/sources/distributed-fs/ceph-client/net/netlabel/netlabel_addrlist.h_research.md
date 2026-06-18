<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlabel/netlabel_addrlist.h -->
# sources/distributed-fs/ceph-client/net/netlabel/netlabel_addrlist.h

## Purpose
`netlabel_addrlist.h` declares NetLabel address-list structures, iteration macros, function prototypes, and audit stubs for IPv4 and optional IPv6 address lists.

## Important APIs, Types, and Functions
The core types are `struct netlbl_af4list` with `__be32 addr`, `__be32 mask`, `valid`, and `list`, and `struct netlbl_af6list` with `struct in6_addr addr`, `mask`, `valid`, and `list`. Macros include `netlbl_af4list_foreach()`, `netlbl_af4list_foreach_rcu()`, `netlbl_af4list_foreach_safe()`, and IPv6 equivalents, backed by `__af4list_valid()`, `__af4list_valid_rcu()`, `__af6list_valid()`, and `__af6list_valid_rcu()`.

## Control Flow, State, and Persistence
The inline helpers advance list iteration past entries whose `valid` flag has been cleared before RCU deletion completes. The macros provide normal, RCU, and safe traversal forms. Data persists in caller-owned list nodes; the header does not allocate or free memory.

## Dependencies and Integration Points
It depends on list and RCU primitives, IPv6 type definitions, and audit types. Function declarations connect users to `netlabel_addrlist.c`; audit functions compile to no-op stubs when `CONFIG_AUDIT` is disabled, and IPv6 declarations are conditional on `CONFIG_IPV6`.

## Risks and Test Signals
Risks include using non-RCU iteration under RCU-only protection, dereferencing the list head through `container_of()` if macros are misused, stale invalid entries, and missing audit/IPv6 functions under configuration changes. Tests should compile with IPv6 and audit enabled/disabled, exercise all traversal macros with invalid entries, verify prototypes match implementations, and run list removal scenarios under lockdep/RCU debug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlabel/netlabel_addrlist.h -->

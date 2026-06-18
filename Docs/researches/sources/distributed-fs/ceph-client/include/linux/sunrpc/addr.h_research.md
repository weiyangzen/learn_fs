# sources/distributed-fs/ceph-client/include/linux/sunrpc/addr.h

Purpose: provides SUNRPC sockaddr presentation conversion declarations plus inline helpers for comparing, copying, and manipulating IPv4/IPv6 RPC peer addresses.

Important APIs and types: external conversion APIs are `rpc_ntop()`, `rpc_pton()`, `rpc_sockaddr2uaddr()`, and `rpc_uaddr2sockaddr()`. Inline helpers include `rpc_get_port()`, `rpc_set_port()`, `rpc_cmp_addr4()`, `rpc_cmp_addr6()`, `rpc_cmp_addr()`, `rpc_cmp_addr_port()`, `rpc_copy_addr()`, and `rpc_get_scope_id()`. Constants define IPv6 universal-address scope delimiters and scope ID string size.

Control flow: callers convert between socket addresses and RPC universal address strings, then use inline helpers to compare address-only or address-plus-port identity. IPv6 comparison accounts for link-local scope IDs when IPv6 is enabled.

State and persistence: no state is stored; helpers operate on caller-supplied `sockaddr` buffers.

Dependencies and integration points: depends on socket, IPv4/IPv6 address types, `struct net`, and optional IPv6 support. It is used by RPC client/server transport setup, rpcbind registration, and multipath address matching.

Risks and test signals: risks include ignoring ports when ports matter, missing IPv6 scope IDs, copying into undersized buffers, and IPv6-disabled fallbacks returning false. Test with IPv4, global IPv6, link-local IPv6, rpcbind universal address parsing, and namespace-aware parsing.

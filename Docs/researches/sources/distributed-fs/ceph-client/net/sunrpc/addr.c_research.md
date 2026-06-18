# sources/distributed-fs/ceph-client/net/sunrpc/addr.c

Purpose: Converts SUNRPC socket addresses between kernel `sockaddr` structures, presentation IP strings, and rpcbind/NFS universal address strings.

Important APIs/types/functions: Exported functions are `rpc_ntop()`, `rpc_pton()`, and `rpc_uaddr2sockaddr()`; `rpc_sockaddr2uaddr()` is also globally visible in this file. IPv4 helpers use `%pI4` and `in4_pton`. IPv6 helpers handle compressed formatting, v4-mapped addresses, optional link-local scope IDs, and `in6_pton`. Universal address helpers append or parse RPCBIND port bytes as `.hibyte.lobyte`.

Control flow: `rpc_ntop()` switches by address family and formats IPv4 or IPv6, including scope ID only for link-local IPv6 with a nonzero scope. `rpc_pton()` selects IPv6 when the input contains `:`; otherwise IPv4. IPv6 parse validates scope delimiters and resolves device names in the provided net namespace or numeric scope IDs. `rpc_sockaddr2uaddr()` formats address plus port bytes, excluding IPv6 scope IDs. `rpc_uaddr2sockaddr()` copies and terminates the supplied string, parses trailing two dot-separated port bytes, parses the remaining address, and writes the network-order port into the resulting sockaddr.

State and persistence behavior: Stateless conversion helpers. Temporary buffers are stack allocated except `rpc_sockaddr2uaddr()`, which returns a caller-owned `kstrdup()` allocation.

Dependencies and integration points: Depends on IPv4/IPv6 parser helpers, netdevice lookup for IPv6 scopes, SUNRPC rpcbind limits, and exported GPL symbols used by SUNRPC transport/rpcbind code.

Risks and test signals: Risks include buffer truncation returning zero, ambiguous colon-based IPv6 detection, scope ID parsing with namespaces, universal address malformed port bytes, and IPv6-disabled builds returning zero for IPv6. Test IPv4, IPv6 compressed, any, loopback, v4-mapped, link-local with numeric and device scopes, max-length universal addresses, malformed ports, small output buffers, and IPv6-disabled configurations.

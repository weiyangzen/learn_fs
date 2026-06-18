# sources/distributed-fs/glusterfs/rpc/rpc-transport/socket/src/name.c

## Purpose

`name.c` resolves, binds, and formats local/remote socket addresses for the GlusterFS socket RPC transport. It handles IPv4, IPv6, SDP-over-INET compatibility, and Unix-domain sockets for both client and server paths. The file was read as a complete 887-line source.

## Important APIs, Types, and Functions

Public entry points are `client_bind`, `socket_client_get_remote_sockaddr`, `socket_server_get_local_sockaddr`, and `get_transport_identifiers`. Important internal helpers include `_assign_port`, `af_inet_bind_to_port_lt_ceiling`, `af_unix_client_bind`, `client_fill_address_family`, `gf_resolve_ip6`, `af_inet_client_get_remote_sockaddr`, `af_unix_client_get_remote_sockaddr`, `af_unix_server_get_local_sockaddr`, `af_inet_server_get_local_sockaddr`, `server_fill_address_family`, and `fill_inet6_inet_identifiers`.

## Control Flow

Client remote resolution starts in `socket_client_get_remote_sockaddr`: it determines address family from `transport.address-family`, `remote-host`, or `transport.socket.connect-path`, then either resolves inet addresses with `af_inet_client_get_remote_sockaddr` or copies a Unix connect path. Inet resolution reads `remote-host` and optional `remote-port`, infers AF_INET/AF_INET6 for literal addresses, then calls `gf_resolve_ip6`, which caches `getaddrinfo` results and returns one address per call while rotating through the result list. `client_bind` then binds a socket locally, trying privileged or insecure port ceilings for inet sockets and optional `transport.socket.bind-path` for Unix sockets.

Server address setup starts in `socket_server_get_local_sockaddr`: it determines family using `server_fill_address_family`, then either builds a Unix listen path from `transport.socket.listen-path` or an inet listener from `transport.socket.listen-port` and optional `transport.socket.bind-address`. Inet server setup defaults to any-address for AF_INET/AF_INET6 when no bind address is given, otherwise uses `getaddrinfo` with `AI_PASSIVE`, preferring IPv6 results when available. `get_transport_identifiers` formats local and peer addresses into stable `host:service` strings, with IPv4-mapped IPv6 addresses normalized to IPv4 for readability.

## State and Persistence Behavior

The file stores no global state. It mutates caller-owned transport fields: `this->dnscache` holds cached `struct addrinfo` results, `this->myinfo` and `this->peerinfo` receive sockaddr lengths and textual identifiers, and bind behavior depends on `this->options` and `this->bind_insecure`. Unix socket path state is copied into caller-provided sockaddr buffers. DNS cache memory is allocated through Gluster allocation helpers and freed/replaced when exhausted or on errors.

## Dependencies and Integration Points

It depends on POSIX sockets, `getaddrinfo`, `getnameinfo`, `inet_pton`, Gluster dict/data helpers, reserved-port tracking (`gf_process_reserved_ports`, `BIT_VALUE`, `BIT_CLEAR`), logging/message IDs, socket-private types from `socket.h`, and transport types from `rpc-transport.h`. It is used by the socket transport implementation when connecting, listening, binding, and labeling connections.

## Risks and Edge Cases

Privileged bind loops can be expensive and must correctly skip Gluster-reserved ports; when all secure ports are exhausted the code falls back to an insecure ceiling to avoid brick-port collisions. Several Unix path checks use the 108-byte `sun_path` limit; off-by-one mistakes can truncate or reject paths. DNS resolution is blocking and the file has a TODO for nonblocking DNS. `gf_resolve_ip6` frees and recreates the cache after cycling through results, so callers should expect different destination addresses across reconnects. IPv4-mapped IPv6 normalization relies on direct `s6_addr32`/`s6_addr16` access with Solaris conditionals. Identifier formatting uses `sprintf` into caller-owned buffers, so buffer sizing must be guaranteed by transport structs.

## Test Signals

Tests should cover address-family inference for remote-host versus Unix connect-path, invalid/missing options, literal IPv4/IPv6 hosts, DNS rotation across multiple `addrinfo` results, client secure and insecure bind fallback, reserved-port skipping, Unix path length boundaries, server any-address defaults, bind-address resolution, IPv4-mapped IPv6 identifier formatting, SDP family restoration, and error logging for unsupported address families.

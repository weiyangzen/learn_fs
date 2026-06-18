# sources/distributed-fs/openafs/src/external/heimdal/roken/getaddinfo.c

Purpose: fallback `getaddrinfo()` implementation for IPv4 and optional IPv6 platforms.

Important APIs/types/functions: `get_port_protocol_socktype()` resolves services and socket/protocol hints. `add_one()`, `const_v4()`, and `const_v6()` build `addrinfo` nodes. `get_null()` returns wildcard or loopback addresses. `get_number()` parses numeric hosts. `add_hostent()` and `get_nodes()` resolve names through hostent APIs. Public `getaddrinfo()` orchestrates validation and lookup.

Control flow: public entry validates node/service presence and supported families, resolves service to port/protocol/socktype, tries numeric node parsing, optionally refuses nonnumeric hosts under `AI_NUMERICHOST`, otherwise resolves hostnames, or returns passive/loopback entries for null node.

State and persistence behavior: allocates a linked `addrinfo` list with heap-owned address and optional canonical name. Caller releases it with `freeaddrinfo()`. No global state except resolver/library state used by hostent and service lookups.

Dependencies and integration points: uses `getservbyname()`, `getprotobynumber()`, `inet_pton()`, `getipnodebyname()`, `hostent_find_fqdn()`, and IPv6 feature macros. Provides portability for OpenAFS/Heimdal networking code.

Risks: fallback semantics are simpler than modern libc, especially `AI_ADDRCONFIG`, multiple protocols, canonical name handling, and thread safety of resolver APIs. Some error paths may leak a canonical name if later address additions fail. Numeric service parsing uses `strtol()` with limited validation.

Test signals: null node passive/non-passive, numeric IPv4/IPv6, hostname resolution, service names for tcp/udp, `AI_CANONNAME`, `AI_NUMERICHOST`, unsupported family, and cleanup on partial failures.

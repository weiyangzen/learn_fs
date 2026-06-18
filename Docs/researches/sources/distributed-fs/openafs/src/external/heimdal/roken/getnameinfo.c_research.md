# sources/distributed-fs/openafs/src/external/heimdal/roken/getnameinfo.c

Purpose: fallback `getnameinfo()` implementation for formatting socket addresses into host and service names.

Important APIs/types/functions: internal `doit()` handles one address family. Public `getnameinfo()` dispatches `AF_INET` and optional `AF_INET6`.

Control flow: for host output, numeric mode uses `inet_ntop()`, otherwise attempts reverse lookup with `gethostbyaddr()`, applies `NI_NOFQDN`, and falls back to numeric unless `NI_NAMEREQD` is set. For service output, numeric mode prints the port, otherwise `getservbyport()` is tried with tcp or udp based on `NI_DGRAM`.

State and persistence behavior: writes into caller-provided host/service buffers. No heap state.

Dependencies and integration points: used by networking code on platforms missing native `getnameinfo`; depends on resolver functions, service database, `inet_ntop()`, and `hostent_find_fqdn()`.

Risks: does not verify `salen` against family-specific sockaddr sizes. Resolver APIs may be non-thread-safe. Buffer truncation is delegated to `strlcpy()`/`snprintf()` rather than reported as `EAI_OVERFLOW`.

Test signals: numeric and reverse host paths, `NI_NAMEREQD`, `NI_NOFQDN`, numeric and named services, `NI_DGRAM`, IPv6 build coverage, and unsupported family errors.

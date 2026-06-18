# sources/distributed-fs/ceph-client/fs/smb/client/dns_resolve.h

Purpose: declares the CIFS DNS resolver interface and provides a UNC-specific wrapper used by DFS and reconnect code.

Important APIs and functions: declares `dns_resolve_name` and defines inline `dns_resolve_unc`.

Control flow: `dns_resolve_unc` validates that a UNC-like string is at least three characters, extracts the hostname with `extract_unc_hostname`, rejects empty hostnames, and calls `dns_resolve_name` with the optional DNS domain and output socket address.

State and persistence behavior: the header owns no state. It passes caller-owned UNC strings and socket-address storage through to the resolver implementation.

Dependencies and integration points: includes Linux network declarations plus CIFS global/prototype helpers. Used by `dfs.c`, `dfs_cache.c`, and `connect.c` anywhere a UNC path or target must become an address for mount, target matching, or reconnect.

Risks: the wrapper assumes UNC parsing rules from `extract_unc_hostname`; malformed paths return `-EINVAL`. Callers must provide writable `sockaddr` storage large enough for IPv4 or IPv6 results. It does not set SMB ports, so callers such as DFS mount setup must apply ports separately.

Test signals: malformed UNC rejection, empty hostname rejection, slash and backslash UNC variants, IPv4/IPv6 literal UNC hosts, domain-suffixed NetBIOS UNC hosts, and callers setting the port after successful resolution.

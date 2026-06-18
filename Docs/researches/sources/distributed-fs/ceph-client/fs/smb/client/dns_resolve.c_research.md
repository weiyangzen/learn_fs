# sources/distributed-fs/ceph-client/fs/smb/client/dns_resolve.c

Purpose: provides CIFS DFS hostname-to-IP resolution through the kernel DNS resolver. It accepts UNC hostnames or DFS target hostnames, treats literal IPv4/IPv6 addresses as already resolved, optionally expands NetBIOS names with a DNS domain, and returns a populated socket address.

Important APIs and functions: the public function is `dns_resolve_name`. The internal helper `resolve_name` performs the `dns_query` upcall and converts the returned textual IP address with `cifs_convert_address`.

Control flow: `dns_resolve_name` validates inputs, tries `cifs_convert_address` directly, then if a DNS domain is present and the name is NetBIOS-style it allocates `name.domain` and resolves that first. If FQDN resolution fails or is not attempted, it resolves the original name. `resolve_name` calls `dns_query` in the current network namespace, logs failures or results, converts the returned string into `sockaddr`, frees the resolver string, and maps conversion failure to `-EHOSTUNREACH`.

State and persistence behavior: no persistent module state is kept here. The only allocated state is the temporary FQDN string and DNS resolver result string. Resolution runs in `current->nsproxy->net_ns`, so namespace selection follows the caller context.

Dependencies and integration points: depends on `linux/dns_resolver.h`, CIFS address conversion, NetBIOS name detection, debug logging, and network namespace context. It is called by DFS mount parsing, DFS target/server matching, and reconnect hostname refresh in `connect.c`.

Risks: DNS resolver upcalls can be unavailable or misconfigured, especially for DFS automounts. Domain suffixing is only attempted for NetBIOS names, so behavior differs between short and FQDN-like names. The returned IP string must be parseable by CIFS address conversion. Because current task namespace is used, callers must invoke it from the desired network namespace.

Test signals: literal IPv4 and IPv6 inputs skipping upcall, NetBIOS name plus domain resolving as FQDN first, fallback to original name, resolver failure mapping, conversion failure mapping to `-EHOSTUNREACH`, and DFS reconnect/mount paths in non-initial network namespaces.

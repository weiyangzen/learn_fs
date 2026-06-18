# sources/distributed-fs/ceph-client/include/linux/sunrpc/svcauth.h

Purpose: declares server-side SUNRPC authentication credentials, auth domains, flavor operations, Unix/GSS mapping helpers, and hash helpers.

Important APIs and types: `struct svc_cred` stores uid/gid/group info, pseudoflavor, raw/principal/target principal strings, and GSS mechanism reference. `init_svc_cred()` and `free_svc_cred()` initialize and release those fields. `struct auth_domain` is a refcounted, hashed, RCU-freed domain with name and flavor ops. `enum svc_auth_status` covers garbage, valid, negative, ok, drop, close, denied, pending, and complete. `struct auth_ops` accepts/releases requests, releases domains, sets clients, and returns pseudoflavors.

Control flow: server receive code calls flavor-specific `accept()`, possibly maps a client domain through caches, authorizes, dispatches, then calls `release()` to sign/encrypt or cleanup. Local client credentials can be mapped into service credentials for backchannel/local cases.

State and persistence: auth domains, Unix/GID caches, credential principal strings, and GSS mechanism refs are runtime state, often refreshed by upcall caches.

Dependencies and integration points: integrates string, cache, GSS API, RPC client, hashing, credentials, and `svc_xprt` auth cache. It supports NFS export/client identity authorization.

Risks and test signals: risks include group_info leaks, GSS mechanism ref leaks, domain RCU lifetime bugs, hash collision behavior, pending cache upcalls, and wrong status-to-RPC-error mapping. Test AUTH_NULL/UNIX/GSS, cache expiry, domain lookup races, local backchannel mapping, and KASAN/RCU debug.

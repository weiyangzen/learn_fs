# sources/distributed-fs/ceph-client/net/sunrpc/svcauth_unix.c

## Purpose
`svcauth_unix.c` implements server-side AUTH_NULL, AUTH_SYS/AUTH_UNIX, and AUTH_TLS handling, plus the caches that map client IP addresses to UNIX auth domains and UIDs to expanded group lists. AUTH_NULL is treated like AUTH_UNIX mapped to anonymous credentials but still goes through the same client-domain IP checks for non-NULL procedures.

## Important APIs, Types, And Functions
Important APIs include `unix_domain_find()`, `svcauth_unix_purge()`, `svcauth_unix_info_release()`, `unix_gid_cache_create()`, `unix_gid_cache_destroy()`, `svcauth_unix_set_client()`, `ip_map_cache_create()`, and `ip_map_cache_destroy()`. Exported auth ops are `svcauth_null`, `svcauth_tls`, and `svcauth_unix`. Important structures are `unix_domain`, `ip_map`, and `unix_gid`, each backed by SUNRPC cache or auth-domain lifetimes.

## Control Flow
IP cache entries are requested from userspace as class/address and updated with an expiry and optional domain name. GID cache entries are requested by UID and updated with expiry plus a sorted group list. `svcauth_unix_set_client()` converts the remote address to IPv6 form, skips domain mapping for NULL procedure, looks up or uses the xprt cached IP map, calls `cache_check()`, assigns `rq_client`, then optionally replaces the request's group list with the expanded UID cache result. `svcauth_null_accept()` validates empty credential/verifier and creates anonymous empty groups. `svcauth_tls_accept()` validates AUTH_TLS on NULL procedure and either emits a STARTTLS verifier and queues handshake work or returns a NULL verifier. `svcauth_unix_accept()` parses machine name, uid, gid, supplementary groups, verifier, and reply verifier.

## State And Persistence
Per-net state stores `ip_map_cache` and `unix_gid_cache`. Transport state may cache one validated IP map under `XPT_CACHE_AUTH`. Auth domains persist in the global domain table until their kref drops, then free by RCU. Request credentials hold uid, gid, group_info, flavor, auth domain, and auth status until flavor release.

## Dependencies And Integration Points
The file depends on SUNRPC cache upcall/downcall infrastructure, pipefs cache files, `auth_domain` management from `svcauth.c`, service transport auth-cache lifetime from `svc_xprt.c`, network namespace state, sockaddr parsing/printing helpers, user namespace UID/GID conversion, group_info management, TLS-capable transport handshake ops, and NFS/NFSD export authorization through auth domains.

## Risks And Edge Cases
Cache miss handling can return DROP, CLOSE, DENIED, or OK, and callers must preserve request deferral state. Cached xprt IP maps must be invalidated when expired. IPv4 addresses are represented as v4-mapped IPv6 addresses, while IPv6 scope IDs are ignored. AUTH_SYS accepts invalid `-1` uid/gid values for backwards compatibility, leaving anonymous mapping to upper layers. GID cache updates allow up to 8192 groups, but wire AUTH_SYS still limits supplied groups to `UNX_NGROUPS`. AUTH_TLS is valid only on NULL procedure and depends on transport handshake support.

## Test Signals
Useful tests include AUTH_NULL, AUTH_SYS, and AUTH_TLS request parsing; malformed verifier and oversized machine/group lists; IP cache positive, negative, expired, and purge behavior; xprt auth-cache reuse and release; UID-to-GID cache upcall timeout and update; IPv4/v6 address mapping; STARTTLS verifier and handshake enqueue; and request deferral/close/deny behavior under cache miss or userspace timeout.

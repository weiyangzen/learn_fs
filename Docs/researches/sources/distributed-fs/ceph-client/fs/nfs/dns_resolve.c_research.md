# sources/distributed-fs/ceph-client/fs/nfs/dns_resolve.c

## Purpose
`dns_resolve.c` resolves NFS hostnames to socket addresses for NFSv4 referrals and related client paths. It has two implementations: a simple kernel-DNS path using `dns_query`, and a legacy SUNRPC cache/upcall path that asks user space through rpc_pipefs and caches positive or negative hostname results per network namespace.

## Important APIs, types, and functions
The public API is `nfs_dns_resolve_name`, with lifecycle hooks `nfs_dns_resolver_init`, `nfs_dns_resolver_destroy`, `nfs_dns_resolver_cache_init`, and `nfs_dns_resolver_cache_destroy` when kernel DNS is not enabled.

The cache implementation uses `struct nfs_dns_ent`, embedding `struct cache_head` plus hostname, resolved `sockaddr_storage`, address length, and RCU free state. Cache operations include `nfs_dns_ent_init`, `nfs_dns_ent_update`, `nfs_dns_ent_put`, `nfs_dns_hash`, `nfs_dns_match`, `nfs_dns_request`, `nfs_dns_upcall`, `nfs_dns_parse`, and `nfs_dns_show`.

## Control flow
With `CONFIG_NFS_USE_KERNEL_DNS`, `nfs_dns_resolve_name` directly calls `dns_query`, then parses the returned textual address with `rpc_pton`. Query failures map to `-ESRCH`, and the allocated string is freed.

Without kernel DNS, initialization registers per-net operations and an rpc_pipefs notifier. Each net namespace gets a `cache_detail` cloned from `nfs_dns_resolve_template` and registered with NFS cache infrastructure. A resolve call builds a transient key from the hostname, calls `do_cache_lookup_wait`, and either copies the cached address into the caller buffer or returns `-EOVERFLOW`/`-ESRCH`.

Cache misses trigger `nfs_dns_upcall`, which sets `CACHE_PENDING`, tries the NFS cache upcall helper, and falls back to a SUNRPC cache pipe upcall timeout. User-space replies are parsed by `nfs_dns_parse` as address, hostname, and TTL. Zero-length parsed addresses become negative cache entries; nonzero TTL sets expiry relative to boot time.

## State and persistence behavior
All state is runtime cache state. Entries are keyed by hostname and expire by TTL or cache flush time. Positive entries store a binary socket address; negative entries store only hostname plus the `CACHE_NEGATIVE` flag. Entries are reference-counted by SUNRPC cache code and freed by RCU callback after the final put.

Per-net state lives in `struct nfs_net::nfs_dns_resolve`. rpc_pipefs mount and unmount events register or unregister the cache detail with the pipefs superblock so user-space upcall endpoints are available only while pipefs is mounted.

## Dependencies and integration points
The direct path depends on `linux/dns_resolver.h`, `dns_query`, and SUNRPC address parsers. The upcall path depends on SUNRPC cache APIs, rpc_pipefs notifier APIs, NFS cache helper code, network namespaces, and `nfs4_fs.h`/`netns.h` for NFSv4 client integration.

## Risks
Resolver behavior differs by configuration. Kernel-DNS mode has no local cache lifecycle here, while upcall mode depends on rpc_pipefs availability and user-space responders. Parser risk includes malformed cache lines, TTL zero, hostname length limits, IPv6 scope formatting, negative-cache semantics, and caller buffer overflow. Cache lookup must not return expired, flushed, pending, or negative entries as usable addresses.

## Test signals
Cover kernel-DNS success/failure, IPv4 and IPv6 parsing, caller buffer too small, rpc_pipefs mount/unmount registration, user-space upcall timeout, positive and negative cache replies, TTL expiry, cache flush, malformed parse inputs, per-net namespace create/destroy, and concurrent lookups for the same pending hostname.

# sources/distributed-fs/ceph-client/fs/nfs/dns_resolve.h

## Purpose
`dns_resolve.h` declares the NFS DNS resolver interface and hides configuration-dependent resolver lifecycle behavior. It lets callers use `nfs_dns_resolve_name` regardless of whether hostname resolution is implemented by kernel DNS or by the SUNRPC cache/upcall mechanism.

## Important APIs, types, and functions
The header defines `NFS_DNS_HOSTNAME_MAXLEN` as 128 bytes. It declares `nfs_dns_resolve_name(struct net *net, char *name, size_t namelen, struct sockaddr_storage *sa, size_t salen)`.

When `CONFIG_NFS_USE_KERNEL_DNS` is enabled, resolver init/destroy and per-net cache init/destroy are static inline no-ops returning success. Otherwise, those lifecycle functions are declared for the cache implementation in `dns_resolve.c`.

## Control flow
Callers include the header, call global resolver initialization during NFS client/module setup, call per-network-namespace cache setup where needed, and resolve names through `nfs_dns_resolve_name`. The inline no-op branch avoids registering rpc_pipefs cache machinery when kernel DNS is the resolver backend.

## State and persistence behavior
The header has no state. It defines the build-time contract for whether resolver state is external to this subsystem or owned by the SUNRPC cache path in `dns_resolve.c`.

## Dependencies and integration points
The declarations depend on `struct net` and `struct sockaddr_storage` being visible to includers. The header is included by the resolver implementation and by NFS client code that initializes, tears down, or uses hostname resolution.

## Risks
The main risk is configuration skew: callers must not assume cache lifecycle side effects exist in kernel-DNS builds. Hostname length validation is only a constant here; actual parser and caller code must enforce it consistently.

## Test signals
Build both `CONFIG_NFS_USE_KERNEL_DNS=y` and `n`, verify lifecycle calls link and are idempotent in both modes, and test maximum-length hostname handling through the implementation.

# sources/distributed-fs/ceph-client/fs/nfsd/netns.h

## Purpose
`netns.h` defines `struct nfsd_net`, the per-network-namespace state container for NFSD. It centralizes export caches, idmapping caches, NFSv4 client/session/lock/delegation state, duplicate reply cache state, counters, server lifetime references, copy state, version settings, LOCALIO tracking, and callback infrastructure.

## Important APIs, types, and functions
Important definitions include client/session hash sizing constants, the NFSD stats counter enum, `struct nfsd_net`, `nfsd_netns_ready()`, `nfsd_support_version()`, `nfsd_net_id`, `nfsd_net_try_get()`, `nfsd_net_put()`, `nfsd_copy_write_verifier()`, and `nfsd_reset_write_verifier()`.

## Control flow
The header has no direct execution, but it defines fields used across NFSD startup, shutdown, request dispatch, NFSv4 state management, reply-cache lookup, export lookup, filecache disposal, and LOCALIO invalidation. Most users obtain it with `net_generic(net, nfsd_net_id)`.

## State and persistence
`struct nfsd_net` is dense runtime state. It includes SUNRPC caches, idmapper caches, NFSv4 grace/lease timing, client tracking structures, client/session hash tables, laundromat work, locks, reclaim tracking, service pointer/refcounts/completions, write verifier seqlock and bytes, version bitmaps, duplicate reply cache tables and shrinker, stats counters, server-to-server copy mounts, namespace server name, filecache disposal list, siphash keys, client-count limits, courtesy-client shrinker work, LOCALIO client list, filehandle key, and callback state. Persistence across restart is mediated by client tracking backends, not by this header itself.

## Dependencies and integration points
It depends on net namespaces, lock manager types, NFSv4 constants, percpu counters/refcounts, siphash, and SUNRPC stats. It is included by almost every NFSD subsystem, making it the central integration point for per-net isolation.

## Risks and test signals
Risks include lock-order mistakes among `client_mutex`, `client_lock`, `deleg_lock`, `blocked_locks_lock`, and copy/localio locks; partial initialization leaving `nfsd_netns_ready()` misleading; per-net teardown while references remain; DRC stats updated with weak locking; write verifier races; and feature fields compiled conditionally. Test signals include namespace create/destroy loops, NFSv4 grace/reclaim tests, DRC stress and shrinker paths, server thread start/stop, write verifier reset after writeback error, LOCALIO invalidation, server-to-server copy shutdown, and all supported NFS version toggles per namespace.

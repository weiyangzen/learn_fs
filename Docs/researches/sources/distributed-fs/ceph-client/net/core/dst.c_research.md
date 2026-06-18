# sources/distributed-fs/ceph-client/net/core/dst.c

Purpose: Protocol-independent destination cache core. It initializes, allocates, releases, destroys, and blackholes `struct dst_entry` objects, manages destination metrics copy-on-write, and allocates metadata destinations used by tunnels and XFRM.

Important APIs, types, and functions: Exports include `dst_discard_out()`, `dst_default_metrics`, `dst_init()`, `dst_alloc()`, `dst_dev_put()`, `dst_release()`, `dst_release_immediate()`, `dst_cow_metrics_generic()`, `__dst_destroy_metrics_generic()`, blackhole helpers, `metadata_dst_alloc()`, `metadata_dst_free()`, `metadata_dst_alloc_percpu()`, and `metadata_dst_free_percpu()`. Static `dst_blackhole_ops` supplies no-op or discard behavior for metadata and blackhole destinations.

Control flow and state: `dst_init()` takes a netdevice reference, installs default read-only metrics, default discard input/output, obsolete state, optional XFRM/lwt metadata, `rcuref`, uncached route list state, flags, and destination operation counters. `dst_alloc()` optionally invokes protocol GC before allocating from the protocol cache. `dst_release()` drops the rcuref, resets embedded metadata dst caches when needed, decrements dst counters, and destroys through RCU; `dst_release_immediate()` does synchronous destruction. Destruction calls protocol-specific destroy hooks, drops netdevice and lwt refs, frees metadata or slab storage, then releases XFRM child dsts.

Dependencies and integration points: The file depends on netdevice references, `dst_ops`, lightweight tunnels, XFRM, route metrics, RCU, slab caches, and optional `CONFIG_DST_CACHE`. Metadata destinations integrate with tunnel info (`METADATA_IP_TUNNEL`) and XFRM (`METADATA_XFRM`).

Risks: Destination lifetime is heavily concurrent. A stale dst must be marked dead and redirected to `blackhole_netdev` before device removal using `dst_dev_put()`. Metrics COW uses `cmpxchg()` and refcounted metrics; errors can leak or double-free metrics. Metadata dsts are allocated as flexible objects and use `DST_NOCOUNT`, so freeing must match metadata type. Synchronous release is unsafe where RCU readers may still observe the dst.

Test signals: Route allocation/release under device unregister, blackhole MTU behavior, metadata tunnel dst allocation/free with embedded dst_cache reset, XFRM metadata dst release, metrics COW races under parallel writers, protocol GC threshold behavior, and KASAN/RCU debug during route teardown are relevant validation points.

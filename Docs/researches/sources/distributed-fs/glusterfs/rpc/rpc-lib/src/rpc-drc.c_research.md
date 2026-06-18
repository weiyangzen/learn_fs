## sources/distributed-fs/glusterfs/rpc/rpc-lib/src/rpc-drc.c

Purpose: implements the RPC service duplicate request cache (DRC), primarily for GNFS builds. It caches replies for non-idempotent requests so duplicate RPCs can receive the same response rather than re-executing the operation.

Important APIs and functions: public functions include `rpcsvc_need_drc`, `rpcsvc_drc_lookup`, `rpcsvc_send_cached_reply`, `rpcsvc_cache_reply`, `rpcsvc_cache_request`, `rpcsvc_drc_priv`, `rpcsvc_drc_init`, `rpcsvc_drc_deinit`, and `rpcsvc_drc_reconfigure`. Internal helpers manage cached operation destruction, client lookup/allocation, address comparison, rb-tree comparison, cache insertion, LRU vacancy, and transport event notifications under `BUILD_GNFS`.

Control flow: if DRC is enabled and an actor is marked `DRC_NON_IDEMPOTENT`, incoming requests get associated with a per-client cache. Lookup searches a client's rb tree by XID/program/version/procedure. New in-flight operations are inserted as `DRC_OP_IN_TRANSIT`; after processing, `rpcsvc_cache_reply` copies the reply iovecs and iobref and marks the op cached. Duplicate requests can be answered through `rpcsvc_send_cached_reply`. When global cache size is reached, a fraction of non-in-transit entries are evicted from the tail of the global list.

State and persistence: DRC state is in-memory only: global cache size, LRU factor, counters, per-client rb trees, cached iovecs/iobrefs, and client refs. It does not survive process restart.

Dependencies and integration: depends on `rpcsvc`, `rpc-transport`, libavl/rbtree, Gluster locks/statedump/mem pools, and transport peer addresses. DRC initialization is compiled out for non-GNFS builds.

Risks: duplicate detection uses XID plus program/procedure/version and peer address, so XID wrap or address reuse can affect correctness. In-transit entries are not evicted, so a stuck workload can pressure cache capacity. `rpcsvc_drc_deinit` destroys the mempool without explicitly walking clients/cache in visible code, which depends on surrounding lifecycle assumptions. Lock coverage differs between GNFS notify paths and lookup/cache paths, so concurrency deserves scrutiny.

Test signals: duplicate non-idempotent RPC replay tests, in-transit duplicate behavior, cache eviction tests, reconfigure on/off/resize tests, statedump output, and GNFS-only build coverage.

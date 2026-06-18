# subset-b-008162 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_obj.c -->
# sources/object-store/daos/src/vos/vos_obj.c

## Purpose
`vos_obj.c` implements VOS object mutation, key/value iteration, object/key punch propagation, corruption marking, anchor conversion, and iterator operation tables for dkey, akey, single-value, and extent-value traversal. It sits above the object index/cache layer and below public VOS APIs and generic iterator orchestration.

## Important APIs, Types, And Functions
Key entry points include `vos_obj_punch`, `vos_obj_key2anchor`, `vos_obj_delete`, `vos_obj_delete_ent`, `vos_obj_del_key`, `vos_obj_mark_corruption`, `vos_obj_iter_prep`, nested iterator preparation/fetch helpers, and operation tables `vos_obj_dkey_iter_ops`, `vos_obj_akey_iter_ops`, `vos_obj_sv_iter_ops`, and `vos_obj_ev_iter_ops`. Internal helpers split by tree level: `key_punch`, `obj_punch`, `key_ilog_prepare`, `key_iter_fetch`, `singv_iter_*`, and `recx_iter_*`. The code depends on `struct vos_obj_iter`, `struct vos_krec_df`, `struct vos_rec_bundle`, ilog fetch state, evtree filters, and btree handles.

## Control Flow
Punch begins by validating dkey/akey constraints, allocating a timestamp set, acquiring the object, starting a VOS transaction, incarnating or finding the durable object, and then either punching the object ilog or walking into dkey/akey subtrees. `key_punch` records object/dkey/akey ilog punches and uses `vos_propagate_check` to collapse empty child trees upward. Iteration prepares the requested tree by holding the object, initializing the object tree, opening child btrees or evtree iterators, probing by anchor, checking ilog visibility, and filling `vos_iter_entry_t`. Nested iterators borrow parent context and avoid releasing parent-held objects unless they own the top-level dkey iterator.

## State And Persistence
Persistent state lives in object ilogs, key ilogs, btree roots, evtree roots, known-key offsets, corruption flags, and `vo_max_write`. Updates are transactional through `umem_tx_*` and VOS transaction wrappers; failed mutation paths evict object cache entries when necessary. Timestamp sets record read/write dependencies so uncertain creates, underpunches, and overlapping DTX activity return restart/in-progress errors rather than silently exposing ambiguous state.

## Dependencies And Integration Points
This file integrates with `vos_obj_cache.c` for object references, `vos_obj_index.c` for object ilog/persistent object records, `vos_tree.c`-style key helpers, evtree, dbtree, VOS timestamp conflict detection, DTX commit helpers, media read/corruption marking, and generic VOS iteration. Scrubbing uses `VOS_ITER_PROC_OP_MARK_CORRUPT`, aggregation uses punch and aggregate process hooks, and query/fetch code depends on iterator output fields such as `ie_biov`, `ie_recx`, and checksums.

## Risks
The main risks are iterator lifetime mistakes around fake akeys and nested borrowed objects, stale anchor handling after aggregation, failure to propagate punches after child trees become empty, and subtle transaction restart requirements when timestamp uncertainty exists. The `obj_local`/cache transition and object eviction on punch/delete also require care because stale cached `obj_df` pointers would expose invalid persistent state. Single-value corruption marking mutates durable record address flags and must only run at a validated iterator position.

## Test Signals
Useful tests should cover object/dkey/akey punch with propagation, conditional punch nonexist behavior, underpunch restart behavior, nested iteration over normal and no-akey objects, reverse/forward extent iteration, fake akey anchors, aggregation delete/invisible return codes, corruption marking for SV and EV records, and races with discard/aggregation object flags. Existing comments point to overlapping extent scrub/query behavior as an important regression signal.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_obj.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_obj.h -->
# sources/object-store/daos/src/vos/vos_obj.h

## Purpose
`vos_obj.h` declares the internal object cache and object-index API used by VOS object I/O, iteration, aggregation, discard, and metadata management. It defines the central DRAM `struct vos_object` wrapper around a durable object record.

## Important APIs, Types, And Functions
`struct vos_object` contains the LRU link, cached ilog fetch state, object ID, open dkey tree/iterator handles, sync epoch, durable `vos_obj_df` pointer, container back-reference, md-on-ssd pin handle, evictable bucket IDs, mutex/condition variables, zombie/discard/aggregate flags, and bucket loading/allocation state. Flag bits include `VOS_OBJ_VISIBLE`, `VOS_OBJ_CREATE`, `VOS_OBJ_DISCARD`, and `VOS_OBJ_AGGREGATE`. Declared APIs include `vos_obj_hold`, `vos_obj_release`, cache creation/destruction/eviction, `vos_oi_find`, `vos_oi_alloc`, `vos_oi_find_alloc`, `vos_oi_punch`, `vos_oi_delete`, `vos_obj_incarnate`, and `vos_obj_check_discard`.

## Control Flow
Callers usually hold or acquire an object from the LRU cache, optionally incarnate it in a transaction, perform tree/ilog work, and release it with flags that clear discard or aggregation ownership. The header documents that `vos_obj_hold` runs outside local transactions while `vos_obj_incarnate` is used inside a transaction to create negative cache entries or validate updates.

## State And Persistence
The header separates transient cache state from persistent object state. `obj_df` points into PMEM/BMEM metadata, while `obj_sync_epoch`, ilog fetch state, pin handles, and bucket state are runtime caches. Evictable md-on-ssd pools add explicit bucket allocation and pinning to object lifetime.

## Dependencies And Integration Points
The header depends on DAOS btree/LRU APIs, VOS layout definitions, ilog handling, timestamp sets, containers, and pool internals. It is consumed by object cache, object index, object iteration/update logic, aggregation, discard, and tests that inspect object-index sanity.

## Risks
Because this header defines ownership contracts, misuse can cause leaked container references, stale durable pointers, unbalanced LRU references, or concurrent discard/aggregation conflicts. The bitfield state around bucket allocation/loading is especially sensitive to missing condition broadcasts.

## Test Signals
Tests should validate cache create/destroy, negative-to-durable object incarnation, release flag clearing, visible/non-visible hold semantics, delete/evict behavior, and md-on-ssd bucket pin/unpin behavior.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_obj.h -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_obj_cache.c -->
# sources/object-store/daos/src/vos/vos_obj_cache.c

## Purpose
`vos_obj_cache.c` implements the DRAM LRU cache for VOS objects, including allocation/free callbacks, object lookup, negative cache entries, md-on-ssd bucket pinning, object acquisition/release, discard/aggregation conflict checks, and multi-object pin handles.

## Important APIs, Types, And Functions
The local LRU key is `(struct vos_container *, daos_unit_oid_t)`. LRU callbacks allocate `struct vos_object`, compare keys, hash records, print keys, and free objects. Public/internal entry points include `vos_obj_cache_create`, `vos_obj_cache_destroy`, `vos_obj_cache_evict`, `vos_obj_hold`, `vos_obj_acquire`, `vos_obj_incarnate`, `vos_obj_release`, `vos_obj_evict`, `vos_obj_evict_by_oid`, `vos_obj_check_discard`, `vos_bkt_array_*`, `vos_pin_objects`, and `vos_unpin_objects`.

## Control Flow
`obj_get` holds or creates an LRU reference unless the pool is dying. `vos_obj_hold` is the legacy hold path for fetch/iteration: it may use a thread-local `obj_local` when an uncached object is loaded without create, later moving it into LRU via `cache_object`. For update/punch, `vos_obj_acquire` always creates a cache entry, then optional `vos_obj_incarnate` inside the transaction finds or allocates the durable OI record and updates ilogs. Release unpins md-on-ssd cache ranges if the LRU reference is the last user, clears discard/aggregation flags, and drops or evicts the reference.

## State And Persistence
The cache owns transient container refs, object tree handles, ilog fetch caches, local sync epoch, zombie/discard/aggregate flags, and md-on-ssd pin handles. Durable persistence occurs only through OI calls and transaction updates to fields such as phase-2 bucket IDs. Bucket allocation is coordinated outside active umem transactions and synchronized with Argobots mutex/condition variables.

## Dependencies And Integration Points
This module integrates with DAOS LRU, VOS containers/pools, object index functions, ilog timestamp tracking, umem cache pin/unpin, telemetry gauges/counters, and VOS transaction/DTX state. Aggregation and discard query `vos_obj_check_discard` before mutating an object, while scrub/query/fetch paths depend on hold/release semantics.

## Risks
High-risk areas are negative cache conversion, thread-local object cleanup, md-on-ssd bucket allocation races, unpin timing relative to LRU last-user checks, and object eviction while other references exist. `check_discard` intentionally serializes discard and aggregation broadly; changing it can introduce races between update, discard, EC aggregation, and VOS aggregation.

## Test Signals
Tests should cover cache hits/misses, negative entries, create vs non-create holds, object zombie retry, shutdown behavior, discard/aggregation conflict return codes, evict-by-oid idempotence, bucket array sorting/subset behavior, pinning multiple objects with duplicate buckets, and pin/unpin cleanup on failures.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_obj_cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_obj_index.c -->
# sources/object-store/daos/src/vos/vos_obj_index.c

## Purpose
`vos_obj_index.c` implements the persistent object index table: a btree keyed by `daos_unit_oid_t` whose records are durable object records (`vos_obj_df` or phase-2 `vos_obj_p2_df`). It also provides object-level iteration, aggregation, punch cleanup, layout-version upgrade support, and bucket-iteration skipping.

## Important APIs, Types, And Functions
Important functions include object-index btree callbacks `oi_rec_alloc`, `oi_rec_free`, `oi_rec_fetch`, `oi_node_alloc`, lookup/update APIs `vos_oi_exist`, `vos_oi_find`, `vos_oi_alloc`, `vos_oi_find_alloc`, `vos_oi_punch`, `vos_oi_delete`, `vos_oi_upgrade_layout_ver`, object iterator operations, `oi_iter_check_punch`, `oi_iter_aggregate`, `vos_bkt_iter_skip`, and `vos_obj_tab_register`. `struct vos_oi_iter` wraps generic iterator state with a dbtree handle, epoch range, container ref, ilog fetch state, punch epoch, bucket iterator, and flags.

## Control Flow
Allocation creates a durable object record, initializes its ilog, sets the object ID, and may force DTX sync for newly created objects. Lookup fetches the btree record and adds ilog timestamp dependencies. Punch updates the object ilog through `vos_ilog_punch`. Iteration prepares a dbtree iterator on the container object table, probes by anchor, filters entries through callback and ilog visibility checks, and fills `vos_iter_entry_t` with object metadata and child type. Aggregation checks discard/aggregation conflicts, aggregates the object ilog, and deletes empty object records from the btree.

## State And Persistence
Persistent state includes object IDs, object ilogs, dkey tree roots, sync/max-write metadata, and optional evictable bucket IDs. Record free destroys ilogs, evicts timestamp cache state, and places objects on the GC heap; during layout upgrade it can delete only the old index entry while preserving shared ilog/tree state. Deletions and aggregation run inside umem transactions.

## Dependencies And Integration Points
The module depends on dbtree class registration, VOS ilog and timestamp APIs, GC, object cache eviction, aggregation/discard conflict checks, container handles, VEA/bucket iteration for md-on-ssd, and generic iterator dispatch. Pool layout versioning and upgrade code relies on the ability to duplicate an object record under a new OID layout version without reallocating trees.

## Risks
Risks include corrupting shared ilog/tree state during layout upgrades, failing to evict cached objects before deleting durable records, mishandling uncertain creates during iteration, and incorrectly skipping bucket ranges in evictable pools. `oi_rec_free` must keep GC and ilog destruction semantics aligned with whether only the index entry is being removed.

## Test Signals
Tests should verify object find/alloc/delete idempotence, object ilog punch and aggregate cleanup, iterator filtering and anchor progress, layout-version upgrade sharing, timestamp conflict behavior, bucket skip bitmaps, and class registration/overhead consistency.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_obj_index.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_overhead.c -->
# sources/object-store/daos/src/vos/vos_overhead.c

## Purpose
`vos_overhead.c` exposes metadata sizing helpers for VOS pools, containers, SCM cutoff, and tree overhead estimation. It is a bridge from durable layout/tree classes to metadata sizing tools.

## Important APIs, Types, And Functions
The file exports `vos_pool_get_msize`, `vos_container_get_msize`, `vos_pool_get_scm_cutoff`, and `vos_tree_get_overhead`. `vos_tree_get_overhead` maps `enum VOS_TREE_CLASS` values to dbtree or evtree classes/orders: container, object, dkey, akey, single value, array, and VEA.

## Control Flow
The overhead call zeroes the output structure, dispatches arrays to `evt_overhead_get`, maps other tree classes to btree class/order pairs, and calls `dbtree_overhead_get`. Unsupported classes assert.

## State And Persistence
There is no mutable state. The return values are derived from durable format structure sizes and tree configuration constants, so changes in layout structs or tree orders flow into overhead estimates.

## Dependencies And Integration Points
It depends on VOS layout/internal constants, dbtree overhead APIs, evtree overhead APIs, and VEA tree order definitions. `vos_size.c` consumes these helpers to generate YAML used by metadata overhead estimation.

## Risks
The main risk is stale mappings when new tree classes, layout versions, or btree orders are introduced. A wrong order/class pairing causes capacity estimates to drift from runtime allocation behavior.

## Test Signals
Run the VOS size generator and compare expected tree classes, non-zero node/record sizes, and SCM cutoff. Tests should fail if a new `VOS_TREE_CLASS` is not mapped.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_overhead.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_pool.c -->
# sources/object-store/daos/src/vos/vos_pool.c

## Purpose
`vos_pool.c` implements VOS pool lifecycle and metadata storage integration: pool create/open/close/destroy, PMEM/BMEM/BIO metadata context setup, WAL operations, checkpointing, pool hash/ref management, telemetry, VEA loading, GC integration, pool query/control, and feature checks.

## Important APIs, Types, And Functions
Major exports include `vos_store_ops`, `vos_pool_create_ex`, `vos_pool_create`, `vos_pool_kill`, `vos_pool_destroy_ex`, `vos_pool_open_metrics`, `vos_pool_open`, `vos_pool_upgrade`, `vos_pool_close`, `vos_pool_query`, `vos_pool_query_space`, `vos_pool_space_sys_set`, `vos_pool_ctl`, `vos_pool_checkpoint_*`, `vos_pool_biov2addr`, and compatibility flag helpers. Internal helpers cover metadata read/write/load/flush, waitqueues, WAL reserve/commit/replay/id compare, pool allocation/hash lookup, BIO blob formatting/unmap, and pool open post-processing.

## Control Flow
Pool creation validates inputs and versions, installs an opening placeholder in the UUID hash, creates an umem pool with optional BIO metadata context, initializes the root durable pool object, container table, GC state, pool extension, and optional VEA blob. Open first reuses existing handles when allowed, otherwise inserts an opening placeholder, checks BIO health, opens umem/BIO state, validates magic/version/UUID, opens the container btree, loads VEA, initializes dedup and GC, and optionally initializes checkpoint state. Close decrements opened counts, removes hash/GC refs on the final close, and frees resources when the hash link ref is dropped.

## State And Persistence
Persistent pool state includes `vos_pool_df`, `vos_pool_ext_df`, container table root, VEA metadata, pool UUID, durable version, size fields, compatibility flags, and emergency buffer. Runtime state includes pool hash links, open counts, mutex/cond for concurrent opens, umem instance, BIO contexts, VEA info, GC refs, metrics, checkpoint callbacks/context, and feature bits. WAL commits update umem cache commit IDs, and checkpointing flushes dirty metadata then advances BIO WAL checkpoint IDs.

## Dependencies And Integration Points
This file integrates with umempobj, BIO metadata/data contexts, SPDK blob/VEA, DAOS telemetry, GC, dedup, checker reporting, RAS events, VOS space accounting, pool handle hashing, and xstream-local BIO context discovery. Store ops are called by the umem layer for metadata paging, WAL, and checkpoint flushes.

## Risks
High-risk paths include error unwinding across umem and BIO context creation/open, WAL commit fatal-error handling, checkpoint callback races while `store->vos_priv` is unset, concurrent open serialization, deferred pool destroy while GC still holds refs, feature upgrade transactionality, and metadata read/load queue-depth synchronization. Non-NVMe, sysdb, external-checkpoint, RDB, and recreate flags all change behavior and need coverage.

## Test Signals
Tests should cover create/open/close/destroy across PMEM-only and BIO-backed pools, invalid magic/version/UUID checker paths, concurrent opens, exclusive/small flags, WAL reserve/commit/replay metric updates, checkpoint no-op and active paths, pool upgrade feature bits, VEA load/unmap integration, deferred destroy with open handles, and `vos_pool_ctl` parameter validation.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_pool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_pool_scrub.c -->
# sources/object-store/daos/src/vos/vos_pool_scrub.c

## Purpose
`vos_pool_scrub.c` implements checksum scrubbing for all containers in a VOS pool. It schedules scrub passes based on pool properties, waits for containers to have checksum state loaded, iterates object values, recomputes checksums chunk-by-chunk, marks corrupt records, emits telemetry/RAS signals, and can drain a target after too many corruptions.

## Important APIs, Types, And Functions
The main entry point is `vos_scrub_pool`. Supporting functions include `sc_should_start`, `sc_ensure_containers_are_loaded`, `sc_scrub_cont`, `obj_iter_scrub_pre_cb`, `sc_verify_obj_value`, `sc_verify_recx`, `sc_verify_sv`, `sc_handle_corruption`, `sc_mark_corrupt`, `sc_pool_drain`, and `get_ms_between_periods`. State is carried in `struct scrub_ctx`, including pool properties, metrics, current object/key/value coordinates, checksum to verify, VOS iterator handle, scheduler callbacks, and container callbacks.

## Control Flow
`vos_scrub_pool` exits early if the pool handle is invalid or scrub should not start. When starting, it ensures containers are loaded, records metrics, iterates container UUIDs, opens each container through callbacks, and runs object iteration with `obj_iter_scrub_pre_cb`. The object callback skips already-seen positions across yields, sets up IOD and checksum context for single values or recxs, reads media into a temporary buffer, verifies checksums, yields/sleeps between chunk calculations, and handles corruption before continuing.

## State And Persistence
Most state is runtime telemetry and iterator progress in `scrub_ctx`. Persistent effects occur when corruption is marked via `vos_iter_process(..., VOS_ITER_PROC_OP_MARK_CORRUPT, ...)`, which updates durable record address flags in the iterator implementation. RAS events and BIO checksum error logging provide external signals; metrics count scrub passes, bytes, checksum calculations, corruptions, duration, and idle/busy time.

## Dependencies And Integration Points
The module integrates with DAOS checksum APIs, server checksum setup, VOS pool/container/object iterators, media reads, BIO NVMe error logging, RAS, DAOS telemetry, pool property scrub mode/frequency/threshold, and scheduler sleep/yield callbacks. It relies on container lookup/put callbacks supplied by the server layer.

## Risks
Risks include validating an iterator position after yielding before marking corruption, correctly handling deleted containers/values, avoiding infinite waits for unloaded containers, respecting pool/container stopping conditions, and preserving fairness in timed/lazy modes. Memory allocation for data buffers and checksum buffers is per-value/chunk and must unwind cleanly. Corruption threshold handling returns shutdown after attempting drain.

## Test Signals
Tests should cover disabled/off scrub, lazy mode idle gating, timed spacing from `get_ms_between_periods`, unloaded container waiting, container deletion during scrub, existing corrupted records on first pass, SV and recx checksum mismatch marking, NVMe vs SCM behavior, corruption threshold drain, stop flags, and overlapping extent checksum visibility limitations noted by the FIXME.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_pool_scrub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_query.c -->
# sources/object-store/daos/src/vos/vos_query.c

## Purpose
`vos_query.c` implements object key queries for minimum/maximum dkey, akey, recx, and max-write epoch. It traverses object, dkey, akey, and evtree state under timestamp/ilog visibility constraints, with special handling for erasure-coded parity extents.

## Important APIs, Types, And Functions
The main API is `vos_obj_query_key`. `struct open_query` carries the held object, timestamp set, epoch bounds, punch record, ilog info, tree roots/handles, anchors, EC stripe/cell sizing, flags, and pool/container handles. Helpers include `check_key`, `find_key`, `query_normal_recx`, `query_ec_recx`, `find_answer`, `open_and_query_key`, and overlap adjustment helpers.

## Control Flow
The public query validates flags, allocates an `open_query`, creates timestamp tracking, holds a visible object, and optionally returns `vo_max_write`. For key queries it opens the dkey tree, finds the next/previous visible integer key when requested, then opens the akey tree or flat dkey value tree, and finally queries recx data from evtree. If a selected dkey/akey has no valid descendant, the code restores timestamp snapshots and continues to the next candidate.

## State And Persistence
The query is read-only but mutates runtime timestamp sets and ilog fetch state. It updates effective epoch ranges and punch records as it descends so child visibility is constrained by parent punches. It closes any open btree/evtree handles before release and records read dependencies so callers can restart on uncertainty.

## Dependencies And Integration Points
This module depends on object cache holds, VOS ilog/timestamp APIs, dbtree iteration, evtree visibility filters, DAOS object type helpers for integer-key validation, checksum/media address structures, DTX in-progress detection, and EC layout constants such as `DAOS_EC_PARITY_BIT`.

## Risks
Risks include incorrect timestamp restore when skipping invalid descendants, EC parity/data extent comparison errors, off-by-one overlap trimming, assuming integer dkey/akey types, and returning stale answers under uncertain DTX state. EC mode maps parity extents to equivalent data ranges, so stripe/cell size inputs must be valid.

## Test Signals
Tests should cover max/min dkey, akey, and recx, max-write-only query, non-integer key rejection, flat dkey objects, holes and punched entries, DTX in-progress restart paths, descendant skip loops, EC parity-only/data-only/overlap cases, and cleanup of open handles on every error path.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_query.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_size.c -->
# sources/object-store/daos/src/vos/vos_size.c

## Purpose
`vos_size.c` generates YAML describing VOS metadata structure and tree overhead sizes for use by `vos_size.py` and related capacity-estimation tooling. It initializes VOS locally, asks runtime tree classes for overhead, and prints aligned records plus checksum sizes.

## Important APIs, Types, And Functions
The primary function is `get_vos_structure_sizes_yaml`. Helper macros enumerate container, object, dkey, akey, integer-key variants, single-value, array, and VEA overhead classes. `print_dynamic` and `print_record` format tree overhead data, while `get_daos_csummers` initializes all DAOS hash algorithms and records checksum lengths.

## Control Flow
The generator clears the output buffer, initializes DAOS debug and VOS self state, calls `vos_tree_get_overhead` for each tree type, writes root/container/SCM cutoff values, emits dynamic node references and tree records, emits checksum sizes, handles string-buffer errors, and tears VOS/debug state down.

## State And Persistence
There is no durable VOS state change intended. Runtime initialization may create or access local VOS self state at the supplied path, and all output is accumulated in a `d_string_buffer_t`.

## Dependencies And Integration Points
The file depends on `vos_overhead.c`, VOS self init/fini, DAOS debug setup, DAOS checksum algorithms, and string-buffer helpers. It is tooling-facing rather than data-path-facing, but its output should track real VOS tree allocation behavior.

## Risks
Risk comes from failing to initialize VOS self state, checksum algorithm initialization failures, buffer allocation/write errors, and drift between `FOREACH_TYPE` and supported tree classes. Alignment to 32 bytes is baked into reporting and should remain consistent with allocator expectations.

## Test Signals
Tests should assert that YAML generation succeeds for a valid VOS path, includes all expected tree keys and checksum algorithms, handles initialization failure cleanly, and changes when underlying tree overhead constants change.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_size.c -->

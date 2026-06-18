# Research: subset-b-008161

Grouped research for DAOS VOS incarnation-log, IO, iterator, internal, and durable-layout files. Each section preserves the exact source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_ilog.c -->
# sources/object-store/daos/src/vos/vos_ilog.c

## Purpose
`vos_ilog.c` adapts the generic DAOS incarnation-log implementation to VOS semantics. It translates ilog entry transaction ids through VOS DTX state, parses creation and punch history into `struct vos_ilog_info`, and exposes update, punch, aggregation, discard, corruption, and timestamp-cache helpers used by object, dkey, and akey paths.

## Important APIs and Functions
Key public entry points are `vos_ilog_fetch_`, `vos_ilog_update_`, `vos_ilog_punch_`, `vos_ilog_set_flags_`, `vos_ilog_check_`, `vos_ilog_aggregate`, `vos_ilog_is_punched`, and the fetch lifecycle helpers. Callback glue in `vos_ilog_desc_cbs_init` binds `ilog` to `vos_dtx_check_availability`, `vos_dtx_register_record`, and `vos_dtx_deregister_record`. `vos_parse_ilog` is the central parser: it walks fetched ilog entries in reverse, handles committed, uncommitted, removed, and in-progress entries, tracks parent or passed-in punches, and derives `ii_create`, `ii_prior_punch`, `ii_prior_any_punch`, `ii_next_punch`, `ii_uncertain_create`, `ii_empty`, and `ii_full_scan`.

## Control Flow
Fetch opens with `ilog_fetch`, initializes `vos_ilog_info`, imports parent punch state when nested under an object or dkey, then parses entries against the requested epoch range and uncertainty bound. Update first fetches the log for conditional or conflict checks, rejects insert/update conditions when visibility does not match, opens the ilog, then calls `ilog_update` with the current DTX operation sequence as minor epoch. Punch is similar, but can no-op for non-leaf non-conditional punches, can reject conditional punches on nonexistent entities, and writes a punch entry only at the leaf. Aggregation calls generic `ilog_aggregate` and then refetches to expose the post-aggregation view.

## State and Persistence
The durable state is `struct ilog_df` stored in object/key records. DTX coupling is persistent through local DTX ids recorded in ilog entries. Minor epochs order sub-operations within an epoch; replay punches use a slightly lower minor epoch so later same-epoch updates can remain visible. Corrupted ilogs are blocked for normal access by `vos_ilog_failout` but remain available to discard, mark, kill, and check intents. Timestamp helpers map ilog roots into the VOS timestamp cache for conflict detection.

## Dependencies and Integration
This file depends on `vos_internal.h`, generic `ilog`, VOS DTX tables, timestamp sets, and epoch/punch helpers. It is called by object/key code and by `vos_io.c` when checking or changing object, dkey, and akey incarnations. Aggregation and discard use `vos_ilog_aggregate` and `vos_ilog_is_punched` to decide if logs and their owning records can be removed.

## Risks and Test Signals
Important risks are incorrect parent punch propagation, treating uncommitted entries as visible, mishandling uncertainty bounds, and corrupting DTX record registration on ilog add/delete. Tests should exercise conditional insert/update/punch, same-epoch minor ordering, DTX in-progress and aborted states, replay punches, parent punch coverage across object/dkey/akey levels, aggregation discard of committed and uncommitted entries, and corrupted-ilog failout behavior.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_ilog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_ilog.h -->
# sources/object-store/daos/src/vos/vos_ilog.h

## Purpose
`vos_ilog.h` declares the VOS wrapper contract around generic incarnation logs. It defines conditional operation modes, punch records, parsed ilog state, tracing wrappers, timestamp-cache hooks, and failout policy for corrupted ilogs.

## Important APIs and Types
`enum` values `VOS_ILOG_COND_NONE`, `PUNCH`, `UPDATE`, `INSERT`, and `FETCH` describe conditional existence semantics. `ILOG_FLAGS_CORRUPTED` reserves ilog magic flag space for data-loss handling. `struct vos_punch_record` stores major and minor punch epochs. `struct vos_ilog_info` owns fetched `ilog_entries` plus parsed state for visible creation, committed and uncommitted punches, next punch, uncertainty, empty-log state, and full-range coverage. Public APIs mirror the implementation: fetch/init/move/finish, update, punch, check, set flags, aggregate, is-punched, descriptor callback setup, timestamp add/mark/evict/last-update, and `vos_ilog_failout`.

## Control Flow Contract
Callers initialize `vos_ilog_info`, fetch at an epoch with optional parent or external punch context, check visibility with `vos_ilog_check`, and finish the info object. Update and punch APIs perform a fetch internally before modifying the log so conditional checks and uncertainty handling are centralized. When `ILOG_TRACE` is enabled, macro wrappers preserve the API shape while logging inputs, outputs, parsed creation and punch fields, and returned epoch ranges.

## State and Persistence
The header does not define the durable ilog layout itself; that is `struct ilog_df` from `ilog.h`. It defines VOS interpretation of that durable state. `vos_ilog_info` is transient and must not be copied wholesale unless the entry list ownership is handled; `vos_ilog_copy_info` intentionally copies only parsed fields after `ii_entries`. The timestamp functions associate ilog roots with VOS read/write timestamp entries for conflict detection and cache eviction.

## Dependencies and Integration
The header includes DAOS common definitions, generic `ilog`, and `vos_ts`. It forward-declares `struct vos_container` so object and IO code can use ilog APIs without needing implementation details. `vos_internal.h` includes this header and supplies key helpers such as `vos_epc_punched` and DTX state. `vos_io.c` and object iterator code rely on `struct vos_ilog_info` to carry parent visibility down object, dkey, and akey levels.

## Risks and Test Signals
API risks include confusing `visible_only` versus punched visibility in `vos_ilog_check`, copying `ii_entries` incorrectly, and bypassing corrupted-log failout for normal intents. Tests should verify all conditional modes, the tracing macros under compile-time enablement, timestamp add/mark/evict behavior for valid and null timestamp sets, and that corrupted ilogs are accessible only for the explicit maintenance intents named in `vos_ilog_failout`.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_ilog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_internal.h -->
# sources/object-store/daos/src/vos/vos_internal.h

## Purpose
`vos_internal.h` is the main private interface for the VOS implementation. It connects durable layout types to runtime pool/container/object state, DTX state, iterator contracts, record layout helpers, media allocation, timestamp conflict checks, aggregation flags, cache pinning, and cross-module prototypes.

## Important APIs and Types
The header defines tree orders, block constants, DTX local-id values, aggregation credit limits, metrics structures, and runtime `struct vos_pool`, `struct vos_container`, `struct vos_dtx_act_ent`, and `struct vos_dtx_cmt_ent`. It declares tree classes (`VOS_BTR_DKEY`, `AKEY`, `SINGV`, object/container/DTX/ilog tables), record helpers (`vos_rec_bundle`, `vos_svt_key`, `vos_krec_size`, `vos_irec_msize`, checksum accessors), iterator abstractions (`struct vos_iterator`, `struct vos_iter_info`, `struct vos_iter_ops`, `struct vos_obj_iter`), and reservation/publish functions implemented in `vos_io.c`.

## Control Flow and Integration
Most VOS C files include this header to share handles and conventions. Public handles are cookie-cast to `vos_pool`, `vos_container`, or `vos_iterator`. IO code uses it to create record bundles, reserve SCM/NVMe space, choose media, publish reservations, and update aggregation flags. Iterator code uses `vos_iter_ops`, nested tree fetch information, anchors, and flags. DTX code uses the active/committed entry wrappers and helper predicates. Object/key code uses tree preparation, release, punch, delete, and corruption marking prototypes.

## State and Persistence
The runtime structures point at durable `vos_pool_df`, `vos_cont_df`, `vos_obj_df`, `vos_krec_df`, and `vos_irec_df` records defined in `vos_layout.h`. `vos_pool` owns umem, feature flags, container tree handle, VEA state, dedup hash, metrics, GC state, checkpoint context, and reservation thresholds. `vos_container` owns object btree handle, DTX tables and lists, stable epoch boundaries, GC/aggregation/discard runtime state, timestamp index, allocation hints, and DTX reindex cursors. Inline helpers encode persistent DTX states and solo-DTX semantics by using reserved local-id bits.

## Dependencies
Dependencies include GURT list/hash, DAOS btree/LRU/common/server APIs, BIO, VOS public types, TLS, durable layout, ilog wrappers, and object cache declarations. The header also exposes integration points for GC, space accounting, checksum recalculation, WAL flushing, NVMe target health, md-on-SSD phase2 bucket pinning, and layout upgrade.

## Risks and Test Signals
Because this header centralizes private contracts, risks include ABI/layout drift between durable and runtime structures, misuse of handle cookie casts, stale DTX local-id interpretation, feature-bit collisions with btree/evtree flags, and media decisions that disagree with reservation or record metadata. Test signals should cover DTX committed/aborted/prepared interpretation including solo transactions, aggregation timestamp packing for HLC and non-HLC epochs, SCM versus NVMe media selection, gang single-value sizing, iterator state transitions, cache pinning with current DTX temporarily cleared, and md-on-SSD bucket allocation paths.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_io.c -->
# sources/object-store/daos/src/vos/vos_io.c

## Purpose
`vos_io.c` implements VOS object fetch and update. It builds per-operation IO context, performs timestamp and ilog existence checks, reserves SCM/NVMe space, reads and writes single values and extents, handles deduplication and checksum metadata, publishes or cancels reservations through backend transactions, and exposes inline helper APIs used by rebuild, RDB, tests, and DAOS IO paths.

## Important APIs and Functions
Public entry points include `vos_fetch_begin`, `vos_fetch_end`, `vos_update_begin`, `vos_update_end`, `vos_obj_update_ex`, `vos_obj_update`, `vos_obj_fetch_ex`, `vos_obj_fetch`, `vos_obj_array_remove`, `vos_get_io_size`, `vos_ioh2desc`, `vos_iod_sgl_at`, checksum and recx-list accessors, `vos_set_io_csum`, `vos_dedup_verify_init`, and `vos_dedup_verify`. Internal pillars are `vos_ioc_create`, `dkey_fetch`, `akey_fetch`, `fetch_value`, `akey_fetch_single`, `akey_fetch_recx`, `dkey_update_begin`, `akey_update_begin`, `dkey_update`, `akey_update`, `update_value`, `akey_update_single`, `akey_update_recx`, reservation helpers, and aggregation markers.

## Control Flow
Fetch begins with target health check and IO context allocation, installs the DTX handle, records container read timestamps, holds the object visible at the requested epoch and uncertainty bound, checks object/dkey/akey ilogs, then fetches single-value btree records or evtree extents. Missing objects/keys can still add negative-read timestamps for conflict detection. Update begin validates duplicate akeys, allocates timestamp sets and BIO descriptors, holds space, optionally acquires evictable objects, and reserves all needed SCM/NVMe extents before data copy. Update end opens the backend transaction, commits CoS DTXs when needed, incarnates the object ilog, updates dkey and akey ilogs, writes values or extent entries, checks timestamp conflicts, records DTX object involvement, marks aggregation flags, publishes reservations, updates dedup entries, releases held space, and destroys the context.

## State and Persistence
Persistent changes include object incarnations, dkey/akey ilogs, single-value btree entries, evtree extent entries, checksum bytes, pool map versions, DTX ids, object `vo_max_write`, and VEA/umem allocations. `struct vos_io_context` is transient but owns reserved SCM actions, NVMe extents, BIO descriptors, dedup staging, timestamp sets, ilog parse state, held space counters, checksum lists, shadow recx state, and output recx lists. Dedup currently indexes SCM payloads by checksum in an in-memory pool hash and can replace a false-positive dedup hit with a fresh SCM allocation during verify.

## Dependencies and Integration
The file integrates VOS object/key tree helpers, generic dbtree and evtree APIs, BIO buffer and block allocator APIs, VEA reservations, checksum library, timestamp conflict sets, DTX lifecycle helpers, WAL/media health checks, and pool/container space accounting. The begin/end split lets upper layers perform RDMA or copy operations between reservation and commit. Aggregation optimization bits are updated through btree/evtree feature fields so later aggregation can find work.

## Risks and Test Signals
High-risk areas are begin/end error unwinding, reservation publishing versus cancellation, duplicate akey rejection, conditional update/insert semantics, uncertainty restarts, DTX in-progress loops, dedup verification false positives, csum-only versus recx-list fetch exclusivity, EC shadow fetch hole handling, gang single-value allocation, md-on-SSD evictable object lifetime, and target health failure after IO. Tests should cover size-only fetch, checksum fetch, recx-list fetch, fetch of holes and corrupt records, SV and EV update/punch/remove, SCM and NVMe media paths, dedup hit/miss/verify-fail, transaction abort cleanup, aggregation marking, and layout upgrade wrapper behavior.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_iterator.c -->
# sources/object-store/daos/src/vos/vos_iterator.c

## Purpose
`vos_iterator.c` implements the generic iterator front end for VOS containers, objects, dkeys, akeys, single values, recx entries, and DTX records. It dispatches to per-type iterator operation tables, manages nested iterators, anchors, recursive traversal, timestamp read sets, scheduler-yield revalidation, and callback action semantics.

## Important APIs and Functions
Public APIs are `vos_iter_type2name`, `vos_iter_prepare`, `vos_iter_finish`, `vos_iter_validate`, `vos_iter_probe_ex`, `vos_iter_probe`, `vos_iter_next`, `vos_iter_fetch`, `vos_iter_copy`, `vos_iter_process`, `vos_iter_empty`, `vos_iterate_key`, `vos_iterate_obj`, and `vos_iterate`. Internal helpers include `nested_prepare`, `is_sysdb_pool`, `iter_decref`, `vos_iter_ts_set_update`, `vos_iter_validate_internal`, `type2anchor`, `reset_anchors`, `set_reprobe`, `need_reprobe`, `advance_stage`, and `vos_iterate_internal`.

## Control Flow
`vos_iter_prepare` validates handles, chooses the dictionary entry for the iterator type, allocates an appropriate timestamp set for transactional reads, installs the active DTX handle, and calls the type-specific prepare op. Nested preparation first fetches child tree information from the parent cursor and then calls child `iop_nested_prepare`, incrementing the parent refcount. Probe, next, fetch, copy, process, and empty all verify iterator state and delegate to type-specific ops.

Recursive iteration is a staged state machine: probe, fetch current entry, optional pre callback, optional recursion into the child type, optional post callback, and next. Callback actions can skip, delete, yield, restart, abort, or exit. Anchors and reprobe flags preserve progress after deletion or yield. Scheduler sequence changes trigger yield detection and may revalidate parent iterator chains before continuing.

## State and Persistence
Iterator state is transient. `struct vos_iterator` stores type, ops, parent, DTX handle, timestamp set, flags, state, anchors, and refcount. Anchors persist caller-visible traversal position across calls. No durable state is written by the generic iterator front end itself, but `iop_process` callbacks may delete or aggregate entries through type-specific implementations. Timestamp sets are updated on successful iteration in transactional contexts.

## Dependencies and Integration
The file depends on the iterator operation tables declared in `vos_internal.h` and implemented by object/container/DTX iterator modules. It integrates with DTX TLS via `vos_dth_get/set`, VOS scheduler sequence checks, public `vos_iter_param_t`, `vos_iter_entry_t`, and `vos_iter_anchors`, md-on-SSD evictable bucket iteration, and key-tree iteration via `VOS_IT_KEY_TREE`.

## Risks and Test Signals
Risks include stale anchors after deletion, missing reprobe after yield, parent iterator use-after-free, incorrect timestamp conflict updates, nested iterator preparation before probing the parent, and recursive traversal resuming at the wrong level after revalidation. Tests should cover standalone and nested iterators, all supported iterator types, recursive object-to-record walks, pre/post callback actions, deletion during iteration, scheduler-yield revalidation, transactional read timestamp restart behavior, `vos_iterate_key` on open tree handles, and md-on-SSD bucket iteration with skipped buckets.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_iterator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_layout.h -->
# sources/object-store/daos/src/vos/vos_layout.h

## Purpose
`vos_layout.h` defines the durable VOS pool, container, DTX, object, key, and value formats. These structures are persisted in the backing umem/PMEM metadata and are the layout contract that runtime code in VOS opens, validates, upgrades, and mutates.

## Important APIs and Types
The file defines `VOS_POOL_LAYOUT`, durable pool version constants, release feature masks, GC bin/bag/bucket records, `struct vos_pool_ext_df`, `struct vos_pool_df`, DTX durable entries (`vos_dtx_cmt_ent_df`, `vos_dtx_act_ent_df`, `vos_dtx_blob_df`), IO stream ids, container extensions (`vos_cont_ext_df`), `struct vos_cont_df`, key record flags, `struct vos_krec_df`, `struct vos_irec_df`, `struct vos_obj_df`, and md-on-SSD phase2 `struct vos_obj_p2_df`.

## Control Flow and Usage
The header is not executable control flow, but it constrains pool/container open, object/key tree operations, DTX indexing, IO update/fetch, aggregation, GC, and layout compatibility checks. Runtime code reads pool durable format version and feature gates before using newer fields such as aggregation optimization, checksum/container extension data, dynamic roots, flat dkeys, embedded first values, and gang single values.

## State and Persistence
Pool state includes magic/version, compatibility flags, extension offset, pool uuid, SCM/NVMe sizes, container count, dedup placeholder, container btree root, VEA free-space state, and GC bins. Container state includes uuid, object count, timestamp index, used bytes, highest aggregated epoch, object tree root, extension offset, DTX blob heads/tails, VEA hints, GC bins, and newest aggregated DTX epoch. Object/key/value state includes object id, sync and max-write epochs, known key offsets, ilogs, dkey btree root, key payload and checksum bytes, SV metadata, DTX local ids, minor epochs, payload size, EC global size, and external BIO addresses.

## Dependencies and Integration
The layout depends on DAOS btree roots, evtree roots, VOS public types, BIO addresses, VEA structures, DTX server types, and generic ilog durable roots. `vos_internal.h` wraps these durable records in runtime objects and provides accessors that compute payload, checksum, key, and data offsets. IO and iterator code assume the bitmap flags identify whether a key owns a btree, evtree, dkey role, or no-akey flat value.

## Risks and Test Signals
The largest risks are durable format incompatibility, feature use against older pools, structure padding drift, incorrect flexible-array sizing, DTX blob head/tail assumptions, GC bucket limit mismatch, and value-address interpretation across SCM, NVMe, holes, gang addresses, and md-on-SSD phase2 object buckets. Tests should include layout version compatibility, pool feature gates, DTX blob append/reindex, container extension validity bits, key/value checksum offset calculations, gang SV storage, flat-dkey records, GC bag/bin persistence, and assertions guarding contiguous DTX head/tail fields and object phase2 sizing.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_layout.h -->

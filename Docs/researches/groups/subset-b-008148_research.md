# subset-b-008148 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/container/srv_epoch.c -->
# sources/object-store/daos/src/container/srv_epoch.c

## Purpose
Implements container epoch and snapshot service operations on the pool/container service leader. It owns the RDB-backed snapshot list, snapshot object-index-table (OIT) OID metadata, and the service-side paths for create/list/destroy snapshot RPCs. It also coordinates target notification before committing snapshot metadata so target VOS/OIT state is prepared consistently.

## Important APIs and functions
- `ds_cont_epoch_aggregate()` validates write capability and normalizes an aggregate epoch, but target aggregation is effectively a placeholder in the paired target file.
- `ds_cont_snap_create()` checks write permission, calls `snap_create_bcast()`, returns the selected snapshot epoch, and stores it in the idempotence operation value.
- `ds_cont_snap_list()` returns snapshot count and optionally bulk-transfers snapshot epochs.
- `ds_cont_snap_destroy()` deletes a snapshot key, removes any OIT-OID key for that epoch, and decrements `ds_cont_prop_nsnapshots`.
- `ds_cont_get_snapshots()` is an internal leader-side helper for other xstreams/modules.
- `ds_cont_update_snap_iv()` refreshes snapshot IV state from RDB and publishes it through `cont_iv_snapshots_update()`.
- `ds_cont_snap_oit_create()`, `ds_cont_snap_oit_destroy()`, and `ds_cont_snap_oit_oid_get()` manage the snapshot-to-OIT-object mapping.

## Control flow
Snapshot creation parses epoch/options from the RPC, checks container write capability, and uses `snap_oit_create()` to broadcast `CONT_TGT_SNAPSHOT_NOTIFY` to targets. That target notification can create OIT content and can replace the requested epoch with current HLC for create options. Only after successful target notification does `snap_create_bcast()` update `cont->c_snaps` and increment `nsnapshots` in the container property KVS. Listing uses `read_snap_list()`, which iterates `cont->c_snaps`, grows a heap buffer, and returns the total count even when the caller's bulk buffer is smaller. If a bulk handle is supplied, `xfer_snap_list()` creates a local bulk handle and performs `CRT_BULK_PUT` to the client.

## State and persistence
Persistent state lives in RDB paths carried by `struct cont`: `c_snaps` stores snapshot epochs as integer keys with a nonempty dummy value, `c_prop` stores `nsnapshots`, and `c_oit_oids` stores `epoch -> daos_obj_id_t` for OIT snapshots when container global version supports it. Snapshot IV is derived, not authoritative; it is refreshed after RDB changes and consumed by targets for aggregation boundaries.

## Dependencies and integration points
Depends on RDB transactions, container layout keys from `srv_layout.h`, security checks from `daos_srv/security.h`, CaRT RPC helpers from `rpc.h`, target broadcast via `ds_cont_bcast_create()`, pool map placement for OIT generation, and IV update helpers from `container_iv.c`. The OIT path integrates with `srv_oi_table.c` on targets.

## Risks
`ds_cont_epoch_aggregate()` currently does little beyond validation, so callers may assume more aggregation work than is present. Snapshot create performs target-side OIT work before RDB snapshot insertion; failures after target work but before RDB commit need idempotence/retry behavior to be correct. `ds_cont_snap_destroy()` decrements `nsnapshots` without underflow guard after the existence lookup. Bulk listing returns total snapshot count while transferring only up to provided capacity, which callers must interpret correctly. `ds_cont_update_snap_iv()` logs and ignores IV failures, so aggregation may temporarily run with stale snapshot boundaries.

## Test signals
Useful tests should cover permission denial, invalid epochs, bounded and unbounded snapshot listing, bulk transfer truncation/count semantics, OIT OID lookup for old/new container versions, RDB failure paths, and IV refresh after create/destroy. Integration tests should verify target notification failure prevents RDB snapshot insertion.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/container/srv_epoch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/container/srv_internal.h -->
# sources/object-store/daos/src/container/srv_internal.h

## Purpose
Provides private container-server declarations shared across the container service implementation. It binds together service RDB state, target-side caches, IV payload formats, metrics, epoch tracking, and cross-file function prototypes.

## Important APIs and types
- `struct cont_pool_metrics` declares per-pool container operation counters.
- `struct dsm_tls` is module TLS, containing the per-xstream `ds_cont_child` cache and open handle hash.
- `struct cont_svc` is the leader service descriptor: pool UUID/id, RDB service, lock, root/UUID/container/handle RDB paths, owning pool, and leader EC/stable epoch tracking request/list/mutex.
- `struct cont` wraps one service-side container and its RDB subpaths: property KVS, snapshots, user attrs, handle index, and OIT OID map.
- `struct cont_iv_snapshot`, `cont_iv_capa`, `cont_iv_prop`, `cont_iv_track_eph`, `cont_iv_entry`, and `cont_iv_key` define flattened IV payloads.
- Function prototypes expose service operations (`ds_cont_snap_create`, `ds_cont_prop_set`), target collectives (`ds_cont_tgt_open`, `ds_cont_tgt_destroy`), IV helpers, OID IV reservation, metrics, and OIT gathering.

## Control flow and integration
This header is the central dependency layer: service files such as `srv_epoch.c` consume `struct cont` and RDB path members, while target files such as `srv_target.c` consume TLS and IV prototypes. Container IV updates flow through declared functions like `cont_iv_prop_update()`, `cont_iv_snapshots_update()`, and `cont_iv_track_eph_update()`. Target operations declared here are invoked by service-side RPC handlers and by pool/rebuild code outside this subset.

## State and persistence behavior
The header describes both persistent RDB state (`cont_svc` and `cont` paths) and volatile per-xstream state (`dsm_tls`, target caches, handle hash). `cont_iv_prop` is a wire/cache representation of persistent properties, including checksum, redundancy, roots, status, and ACL. Epoch-tracking structures (`rank_eph`, `cont_track_eph_leader`, `cont_iv_track_eph`) bridge target-reported volatile progress to service decisions and RDB-backed EC aggregation epochs.

## Dependencies
Includes DAOS LRU, security, engine, RDB, replicated service, server container, telemetry, and the persistent layout header. It deliberately forward declares pool and container-handle types to avoid broader include coupling.

## Risks
This file is ABI-sensitive inside the module: IV payload structure changes must remain coordinated with container IV serialization and versioning. `cont_iv_prop` has `struct daos_acl` as a flexible final member, so allocation/size calculations must account for ACL length. Many functions are declared here but implemented elsewhere; mismatched assumptions about lock ownership, xstream affinity, or reference ownership can cause subtle bugs.

## Test signals
Compile coverage is important because this header cross-links many modules. Functional tests should indirectly validate IV round trips, target open/close lifecycle, property updates, snapshot refresh, OID allocation, metrics allocation count, and leader/target epoch reporting.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/container/srv_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/container/srv_layout.c -->
# sources/object-store/daos/src/container/srv_layout.c

## Purpose
Defines the RDB string keys and default container property sets described by `srv_layout.h`. It also initializes and finalizes dynamically allocated default ACL entries used by container creation.

## Important APIs and data
- `RDB_STRING_KEY(ds_cont_prop_, ...)` and `RDB_STRING_KEY(ds_cont_attr_, user)` instantiate global `d_iov_t` keys for root/container property KVS entries.
- `cont_prop_entries_default_v0` is the older default property set with checksum and server verification enabled and RF3/rank redundancy defaults.
- `cont_prop_entries_default` is the current default property set with checksum/server verification off, RF0/default redundancy, and extra EC/PDA/global/scrubber/object/perf-domain fields.
- `cont_prop_default_v0` and `cont_prop_default` wrap those arrays as `daos_prop_t`.
- `ds_cont_prop_default_init()` allocates default DAOS container ACLs for both property sets.
- `ds_cont_prop_default_fini()` frees those ACL pointers.

## Control flow
Most of the file is static initialization. At module startup, `ds_cont_prop_default_init()` finds the ACL entries by type and fills `dpe_val_ptr` using `ds_sec_alloc_default_daos_cont_acl()`. If allocation of the current ACL fails after v0 allocation succeeded, it frees the v0 allocation before returning `-DER_NOMEM`. At shutdown, `ds_cont_prop_default_fini()` looks up both ACL entries and frees their value pointers.

## State and persistence behavior
The global `d_iov_t` key objects are used as stable RDB keys throughout the container service. The default property arrays are in-process templates copied/consulted by creation and migration logic; they are not persistent by themselves. `dummy_roots` avoids per-use allocation for the default roots property and is expected to be overwritten by middleware when real roots are set.

## Dependencies and integration
Depends on `daos_srv/rdb.h` for key macros and `daos_srv/security.h` for default ACL allocation. Service files use these globals for RDB lookup/update, and property conversion code depends on the default property coverage matching `DAOS_PROP_CO_*` ranges and version expectations.

## Risks
The default arrays must stay aligned with `CONT_PROP_NUM_V0`, `CONT_PROP_NUM`, and DAOS property enum ranges. Adding a property in `srv_layout.h` without adding defaults or conversion support can produce missing values in older code paths. The ACL pointers are mutable global state; double init/fini or partial initialization bugs can leak or double-free.

## Test signals
Tests should verify init/fini under allocation failure, default property counts, current versus v0 defaults, and that all optional container property types expected by creation/query have defaults. RDB layout compatibility tests should verify key names remain stable.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/container/srv_layout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/container/srv_layout.h -->
# sources/object-store/daos/src/container/srv_layout.h

## Purpose
Documents and declares the persistent RDB layout for container metadata in the combined pool/container service database. It is the schema contract for root KVS keys, container handle records, container property keys, snapshot metadata, user attributes, and OIT OID mappings.

## Important APIs and types
- Root keys: `ds_cont_prop_cuuids`, `ds_cont_prop_conts`, `ds_cont_prop_cont_handles`.
- `struct container_hdl` is the persistent representation of a container open handle: pool handle UUID, container UUID, handle capabilities/flags/security capabilities.
- Property keys include label, layout, checksum, dedup, redundancy, ACL, owner, snapshot counters/KVS, health status, handles, roots, EC/PDA/perf-domain/global/object versions, scrubber setting, metadata times, handle count, OIT OID map, and EC aggregation epoch.
- `container_flags_t` and `CONTAINER_F_DESTROYING` define persistent service flags.
- `struct co_md_times` stores open and metadata-modify times.
- `cont_prop_default` and `cont_prop_default_v0` are exported default property templates.
- `ds_cont_prop_default_init()` and `ds_cont_prop_default_fini()` manage dynamic defaults.

## Control flow and persistence
This header is declarative but controls how other code traverses RDB: root KVS maps labels to UUIDs, UUIDs to per-container property KVSs, and handle UUIDs to `container_hdl` records. Per-container KVSs hold property values and sub-KVSs for snapshots, user attrs, handle indexes, and snapshot OIT OIDs. RDB layout versioning is tied to the pool global version rather than a standalone container layout version.

## Dependencies and integration
Included by service and target internals, especially `srv_layout.c`, `srv_epoch.c`, and container service creation/query code. The comments explicitly warn that root-key names share a root RDB namespace with pool service layout, so new container root keys must not collide with pool keys.

## Risks
Schema key names are compatibility-sensitive; renaming breaks persisted pools. Some comments mention historical repurposing, such as `ghce` from a zero uint64 to `container_flags_t`, so readers must preserve backward compatibility. The `CONT_PROP_NUM` formula depends on property enum ranges and can silently become wrong if DAOS property enums change unexpectedly.

## Test signals
Schema tests should validate RDB key presence, backward compatibility for older containers, default property initialization, snapshot and OIT sub-KVS creation, and upgrade paths for v0/current property sets.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/container/srv_layout.h -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/container/srv_metrics.c -->
# sources/object-store/daos/src/container/srv_metrics.c

## Purpose
Allocates and frees container-server telemetry counters for successful container operations. It is intentionally small and scoped to pool-level container metrics.

## Important APIs
- `ds_cont_metrics_alloc(const char *path, int tgt_id)` allocates `struct cont_pool_metrics` and adds counters under the supplied telemetry path.
- `ds_cont_metrics_count()` reports the number of telemetry node pointers in `struct cont_pool_metrics`.
- `ds_cont_metrics_free(void *data)` frees the allocated metrics structure.

## Control flow
Allocation asserts `tgt_id < 0`, making these global/pool metrics rather than per-target metrics. It allocates the metrics struct, then attempts to register counters for open, close, query, create, and destroy operations using `d_tm_add_metric()`. Individual metric registration failures are logged as warnings but do not abort allocation; callers receive the metrics struct even if some node pointers remain unset.

## State and persistence behavior
The file manages volatile telemetry node pointers only. It has no persistent state and does not increment counters itself; other container service paths are expected to use the returned `cont_pool_metrics` fields.

## Dependencies and integration
Depends on `srv_internal.h` for `struct cont_pool_metrics` and on `gurt/telemetry_producer.h` for producer APIs. It is integrated through the server module metrics allocation hooks declared in `srv_internal.h`.

## Risks
Because partial metric registration succeeds, consumers must tolerate NULL metric nodes. `ds_cont_metrics_count()` assumes the structure contains only `struct d_tm_node_t *` fields; adding a non-pointer field without changing this helper would break count semantics. The function only frees the struct, relying on telemetry infrastructure ownership for metric nodes.

## Test signals
Tests should cover successful metric creation paths, simulated `d_tm_add_metric()` failures, the count helper after structure changes, and callers that increment counters when some nodes are NULL.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/container/srv_metrics.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/container/srv_oi_table.c -->
# sources/object-store/daos/src/container/srv_oi_table.c

## Purpose
Builds a snapshot object index table (OIT) by enumerating VOS object IDs in a target container at a snapshot epoch and writing those IDs into a special DAOS object. This supports snapshot/OIT operations initiated by `srv_epoch.c`.

## Important APIs and types
- `OID_SEND_MAX` limits batched OID updates per bucket to 128.
- `struct oit_bucket` stores a heap array of OIDs and a count for one OIT bucket.
- `struct oit_scan_args` carries local pool/container/object handles, target OIT object ID, previous OID suppression state, bucket count, IOD/SGL scratch arrays, and per-bucket arrays.
- `cont_child_gather_oids()` is the exported target-side entry point declared in `srv_internal.h`.

## Control flow
`cont_child_gather_oids()` allocates scan state and one OID array per possible bucket, fetches pool service ranks from IV, opens a client-side pool handle, opens the container using the same container handle UUID as snapshot creation, reads the container global version, and opens the OIT object for update. It iterates VOS objects over the exact snapshot epoch with `VOS_IT_FOR_MIGRATION`. `cont_iter_obj_cb()` ignores OIT objects, suppresses adjacent duplicate public OIDs caused by shard variants, hashes OIDs into buckets, and flushes full buckets with `cont_send_oit_bucket()`. After iteration, all nonempty buckets are flushed.

## State and persistence behavior
The source container state is VOS object metadata at one epoch. The generated OIT is persisted as DAOS object updates: each bucket is a dkey and each object ID is an akey with the snapshot epoch as the value. For old container global versions, all OIDs use one bucket; newer versions can use `DAOS_OIT_BUCKET_MAX`.

## Dependencies and integration
Depends on VOS iteration, DAOS client-side pool/container/object APIs (`dsc_pool_open`, `dsc_cont_open`, `dsc_obj_open`, `dsc_obj_update`), pool IV service rank fetch, object ID helpers, and OIT key macros. It is invoked from `srv_target.c` during `CONT_TGT_SNAPSHOT_NOTIFY` when snapshot options request OIT work.

## Risks
The code comments note that updates use epoch 0 rather than the snapshot epoch for OIT object writes, which can cause overwrites/space inefficiency across targets. Duplicate suppression assumes same public OIDs are adjacent in VOS iteration. The final flush loop overwrites `rc` on each bucket and does not break on first failure, so an earlier flush error can be hidden by a later success. OID arrays are large and heap-managed; allocation failure must clean up partially initialized buckets.

## Test signals
Tests should cover empty containers, duplicate shard OIDs, old versus new global versions, bucket hashing and full-bucket flushing, OIT object exclusion, VOS iteration failures, DAOS update failures in mid/final flushes, and cleanup of all handles/rank lists/bucket arrays.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/container/srv_oi_table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/container/srv_target.c -->
# sources/object-store/daos/src/container/srv_target.c

## Purpose
Implements target-side container lifecycle, open-handle management, VOS and EC aggregation scheduling, snapshot notifications, OID allocation, target query/destroy/open/close collectives, property updates, and EC/stable epoch reporting. It is the main bridge between service-level container RPCs and per-xstream VOS container state.

## Important APIs and functions
- Aggregation: `cont_aggregate_interval()`, `cont_child_aggregate()`, `cont_vos_aggregate_cb()`, `cont_agg_ult()`, `cont_ec_agg_ult()`, `cont_start_agg()`, `cont_stop_agg()`, and `agg_rate_ctl()`.
- Target container cache: `ds_cont_child_cache_create()`, `cont_child_lookup()`, `cont_child_start()`, `cont_child_stop()`, `ds_cont_child_lookup()`, `ds_cont_child_open_create()`, `ds_cont_child_start_all()`, `ds_cont_child_stop_all()`.
- Handles: `ds_cont_hdl_hash_create()`, `ds_cont_hdl_lookup()`, `ds_cont_hdl_get/put()`, `ds_cont_local_open()`, `ds_cont_local_close()`, `ds_cont_tgt_open()`, `ds_cont_tgt_close()`.
- RPC handlers/aggregators: destroy, query, snapshot notify, epoch aggregate, and OID allocation handlers.
- Snapshot/OIT: `ds_cont_tgt_snapshots_update()`, `ds_cont_tgt_snapshots_refresh()`, `cont_snap_notify_one()`.
- Epoch tracking: `cont_tgt_track_eph_init/fini()`, `ds_cont_eph_report()`, `ds_cont_tgt_refresh_track_eph()` declaration partner, and `ds_cont_ec_timestamp_update()`.

## Control flow
Opening a target container goes through a pool thread collective. Each xstream either finds an existing `ds_cont_child` or creates a VOS container under the pool recovery read lock, starts aggregation ULTs unless the pool is restricted, registers DTX state, and inserts a `ds_cont_hdl` into TLS hash. First real open initializes DTX CoS, starts asynchronous DTX resync, and initializes checksum/dedup/compression/encryption properties from container IV. Closing removes the handle before yielding, decrements `sc_open`, and closes DTX state when the last handle closes. Destroy marks `sc_destroying`, force-closes handles, stops DTX reindex/scrub/rebuild/aggregation paths, evicts the LRU entry, destroys the VOS container, and wakes GC.

Aggregation loops periodically check pool map/stopping/rebuild/reclaim state, lazy/busy/space-pressure conditions, checksum/dedup/compression/encryption restrictions, snapshot IV readiness, and EC boundaries. `cont_child_aggregate()` computes an epoch range from HLC minus aggregation gap, last HAE, snapshot boundaries, EC aggregation boundaries, and snapshot deletion resets; it then invokes either VOS aggregation or EC object aggregation across ranges.

Snapshot notifications gather OIT OIDs when requested and cap aggregation during snapshot creation. Snapshot IV updates replace `sc_snapshots`, reset aggregation lower bound on deletion, and set `sc_aggregation_max`. Query collectives open VOS containers and reduce minimum HAE across xstreams. OID allocation reserves ranges through OID IV and returns the base OID. EC/stable epoch tracking stores pointers from each target into a per-pool system-xstream list and periodically publishes minimum nonfailed target epochs through container IV.

## State and persistence behavior
Persistent target state is mainly VOS containers and their object/DTX metadata. Volatile state includes TLS container cache entries, open handle hashes, scheduler requests, snapshot arrays, aggregation boundaries, checksum contexts, property mirrors, and epoch tracking arrays. Destroy deletes VOS persistence and invalidates container IV. OID allocation changes authoritative allocation state through IV backing logic, not local fields.

## Dependencies and integration points
Depends on VOS, DTX, DAOS scheduler, pool child/pool service, pool map/rebuild state, IV, checksum/dedup helpers, EC object aggregation, security capabilities, CaRT RPCs, and container RPC definitions. It is invoked by service leader code, pool startup/rebuild/destroy paths, object layer aggregation, checker failure injection, and snapshot/OIT code.

## Risks
This file is concurrency-sensitive: LRU refs, open-handle refs, `sc_destroying/sc_stopping`, DTX resync, scrub/rebuild waits, and aggregation ULT shutdown all interact. `ds_cont_tgt_query_handler()` asserts collective success and maps nonzero `rc` to `tqo_rc = 1`, which can hide details in release builds. `cont_child_aggregate()` copies snapshot arrays without a visible lock in this file, relying on update discipline. EC aggregation is disabled during rebuild and rate-limited by scheduler state, so stale boundaries can block VOS aggregation. Some target epoch aggregation RPC code is a placeholder (`cont_epoch_aggregate_one()` returns 0).

## Test signals
Existing engine/container integration should be supplemented with tests for repeated open with conflicting flags, first-open DTX/csummer failure cleanup, close after target down/downout, destroy races with rebuild/recovery, snapshot IV update/delete behavior, aggregation upper-bound calculation across snapshots/EC boundaries, OID IV failures, query reduction, property status PM-version ordering, and epoch reporting with failed targets.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/container/srv_target.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/engine/check_engine.pb-c.c -->
# sources/object-store/daos/src/engine/check_engine.pb-c.c

## Purpose
Generated protobuf-c implementation for `check_engine.proto`. It provides initialization, packing, unpacking, freeing, field descriptors, and message descriptors for checker dRPC request/response messages exchanged between the DAOS engine and control plane.

## Important APIs and descriptors
The generated functions cover `Shared__CheckReportReq`, `Shared__CheckReportResp`, `Shared__CheckListPoolReq`, `Shared__CheckListPoolResp__OnePool`, `Shared__CheckListPoolResp`, `Shared__CheckRegPoolReq`, `Shared__CheckRegPoolResp`, `Shared__CheckDeregPoolReq`, and `Shared__CheckDeregPoolResp`. Each nontrivial message gets `__init`, `__get_packed_size`, `__pack`, `__pack_to_buffer`, `__unpack`, and `__free_unpacked` functions. The file exports descriptors such as `shared__check_reg_pool_req__descriptor` and nested field descriptor tables.

## Control flow
Every init function assigns a static `*_INIT` value. Pack/size functions assert the message descriptor pointer matches the expected descriptor and delegate to protobuf-c. Unpack delegates to `protobuf_c_message_unpack()` with the corresponding descriptor. Free functions ignore NULL, assert descriptor identity, and delegate to `protobuf_c_message_free_unpacked()`. The bottom half defines field descriptor arrays, name indexes, number ranges, and `ProtobufCMessageDescriptor` instances used by protobuf-c reflection.

## State and persistence behavior
There is no mutable DAOS state. The only state is static descriptor metadata compiled into the binary. Serialized bytes produced by these helpers are the wire format consumed by dRPC checker methods.

## Dependencies and integration
Includes `check_engine.pb-c.h`, which includes `chk/chk.pb-c.h` for the nested `Chk__CheckReport` report payload. `drpc_chk.c` directly uses these helpers to encode list/register/deregister/report upcalls and decode control-plane responses.

## Risks
This file must match the generated header and the `.proto` schema used by the control plane. Manual edits would be overwritten and can create ABI/wire incompatibility. Descriptor assertions catch wrong message types in debug builds, but release behavior depends on protobuf-c. Repeated rank arrays are marked packed in the generated descriptor; peers must use compatible protobuf definitions.

## Test signals
Regeneration tests should verify generated files are up to date with `check_engine.proto`. Runtime tests should pack/unpack each checker message, including empty list requests, repeated service rank arrays, nested report payloads, and nonzero DAOS status fields.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/engine/check_engine.pb-c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/engine/check_engine.pb-c.h -->
# sources/object-store/daos/src/engine/check_engine.pb-c.h

## Purpose
Generated protobuf-c header for checker engine/control-plane messages. It declares C structs, init macros, serialization APIs, closure typedefs, and descriptors for `check_engine.proto`.

## Important APIs and types
- Request/response structs for checker report, list pool, register pool, and deregister pool methods.
- `Shared__CheckListPoolResp__OnePool` contains pool UUID, label, and repeated service replica ranks.
- `Shared__CheckRegPoolReq` carries sequence, pool UUID, label, and service replicas.
- `Shared__CheckDeregPoolReq` carries sequence and UUID.
- `SHARED__...__INIT` macros initialize embedded `ProtobufCMessage` descriptors and defaults.
- Public functions provide protobuf-c init, size, pack, pack-to-buffer, unpack, and free-unpacked operations.
- Descriptor externs expose reflection metadata to protobuf-c and users.

## Control flow and integration
This header is consumed by `check_engine.pb-c.c` and by engine checker upcall code in `drpc_chk.c`. Callers initialize stack messages with macros, set pointers/counts for dynamic fields, ask for packed size, allocate a buffer, pack into it, and pass it over dRPC. Responses are unpacked with an allocator and freed with the matching `free_unpacked` function.

## State and persistence behavior
The header defines wire-format structures only. It does not own memory except through conventions: string pointers and repeated arrays must remain valid while packing; unpacked messages are owned by protobuf-c allocator and released by `free_unpacked`.

## Dependencies
Requires protobuf-c headers at a compatible version and includes `chk/chk.pb-c.h` for `Chk__CheckReport`. The version guards enforce generator/runtime compatibility.

## Risks
Because this is generated code, hand edits are fragile. Callers must correctly set `n_svcreps` when assigning `svcreps`, must not free borrowed fields before packing, and must not use unpacked strings after `free_unpacked`. Schema drift with control-plane code will break dRPC checker interoperability.

## Test signals
Build tests should catch protobuf-c version mismatch and descriptor symbol availability. Serialization tests should exercise all init macros, empty and nonempty repeated fields, nested `Chk__CheckReport`, and response status propagation.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/engine/check_engine.pb-c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/engine/drpc_chk.c -->
# sources/object-store/daos/src/engine/drpc_chk.c

## Purpose
Implements checker-related dRPC client upcalls from the engine to the control plane. It lets checker code list known pools, register or refresh pool metadata, deregister pools, and report checker findings.

## Important APIs
- `ds_chk_free_pool_list()` frees `struct chk_list_pool` arrays returned by listpool.
- `ds_chk_listpool_upcall()` calls `DRPC_METHOD_CHK_LIST_POOL` and converts protobuf pool entries to DAOS checker structures.
- `ds_chk_regpool_upcall()` calls `DRPC_METHOD_CHK_REG_POOL` with sequence, UUID string, label, and service replicas.
- `ds_chk_deregpool_upcall()` calls `DRPC_METHOD_CHK_DEREG_POOL`.
- `ds_chk_report_upcall()` sends a `Chk__CheckReport` payload through `DRPC_METHOD_CHK_REPORT`.

## Control flow
Each upcall initializes a generated protobuf request, computes packed size, allocates a request buffer, packs, calls `dss_drpc_call(DRPC_MODULE_SRV, method, ...)`, checks dRPC transport status, unpacks the protobuf response with `PROTO_ALLOCATOR_INIT`, checks allocator OOM/NULL response, extracts DAOS status, then frees response/request resources. Listpool additionally allocates an array of checker pool records, parses UUID strings, duplicates labels, converts repeated `uint32_t` service replicas to `d_rank_list_t`, and transfers ownership to the caller on success.

## State and persistence behavior
No local persistent state. The functions translate between local checker state and management-service state held by daos_server/control plane. Returned pool lists are heap state owned by the caller and freed with `ds_chk_free_pool_list()`.

## Dependencies and integration
Depends on checker server headers, dRPC module IDs/method IDs, `dss_drpc_call()` from `drpc_client.c`, generated checker protobuf bindings, UUID parsing/formatting, rank-list conversion helpers, and DAOS fail injection (`DAOS_CHK_LEADER_FAIL_REGPOOL`).

## Risks
The code treats pack return values as `int rc` in places even though protobuf-c pack returns `size_t`; negative checks are ineffective for unsigned return semantics. Listpool cleanup uses `respb->n_pools` when freeing partially initialized local arrays, so `ds_chk_free_pool_list()` must tolerate NULL fields. A dRPC success status can still carry a protobuf-level DAOS error, and callers need to handle positive list count versus negative error return from `ds_chk_listpool_upcall()`.

## Test signals
Tests should mock `dss_drpc_call()` for transport failure, non-success dRPC status, unpack OOM/NULL, response status errors, malformed UUIDs, allocation failure during label/rank conversion, fail-injection register errors, and successful ownership transfer/free of pool lists.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/engine/drpc_chk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/engine/drpc_client.c -->
# sources/object-store/daos/src/engine/drpc_client.c

## Purpose
Implements the engine-side dRPC client used to call daos_server/control-plane methods over the server UNIX-domain socket. It also provides management helpers for readiness notification, pool service lookup, pool lookup by label, and pool listing.

## Important APIs
- `drpc_init()` and `drpc_fini()` create/free the `daos_server.sock` path under `dss_socket_dir`.
- `dss_drpc_call()` is the generic dRPC invocation helper.
- `drpc_notify_ready()` sends engine URI, incarnation, dRPC listener socket path, instance index, target count, context count, and check mode.
- `ds_get_pool_svc_ranks()`, `ds_pool_find_bylabel()`, and `ds_get_pool_list()` call server management dRPC methods and convert protobuf responses into DAOS UUID/rank/list structures.

## Control flow
`dss_drpc_call()` builds a stack argument and either invokes `dss_drpc_thread()` inline for no-response/no-scheduler calls or creates a pthread to avoid blocking the current xstream. Scheduled calls obtain an anonymous scheduler request and poll `pthread_tryjoin_np()` with exponential backoff sleeps, then return the thread's DAOS return code. The worker thread opens a private dRPC connection to avoid shared-context concurrency problems, creates a `Drpc__Call`, borrows the caller request buffer as the body, invokes `drpc_call()`, frees/no-returns the response depending on flags, clears borrowed body pointers, closes the connection, and returns.

## State and persistence behavior
Only static state is `dss_drpc_path`. Calls are stateless and use private transient dRPC connections. Returned pool service ranks, labels, and pool lists are heap allocations owned by callers. Readiness notification borrows `drpc_listener_socket_path` from the listener.

## Dependencies and integration
Depends on DAOS engine globals (`dss_socket_dir`, `dss_instance_idx`, `dss_tgt_nr`, context counts), protobuf bindings in `srv.pb-c.h`, dRPC module IDs, scheduler request APIs, pthreads, backoff helpers, UUID/rank conversion helpers, and `drpc_internal.h`. RAS and checker code reuse `dss_drpc_call()`.

## Risks
If `pthread_create()` fails, the code returns without `sched_req_put()`, which appears to leak the scheduler request. The stack argument passed to the pthread is safe only because the caller waits until join; the assert after `pthread_tryjoin_np()` is the safety boundary. No-response calls run inline and can block the current ULT/xstream. Response parsing must treat dRPC status and protobuf response status separately. `drpc_fini()` asserts path initialization.

## Test signals
Existing `drpc_client_tests.c` is the natural test suite. Coverage should include inline/no-response calls, scheduled pthread path, connection/call/pack failures, non-success dRPC statuses, malformed protobuf responses, rank list conversion, pool-list overflow and cleanup, readiness check-mode fields, and the scheduler-request leak path on pthread creation failure.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/engine/drpc_client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/engine/drpc_handler.c -->
# sources/object-store/daos/src/engine/drpc_handler.c

## Purpose
Implements the dRPC handler registry used by the engine dRPC listener to dispatch incoming `Drpc__Call` messages by module ID.

## Important APIs
- `drpc_hdlr_init()` allocates `registry_table` with `NUM_DRPC_MODULES` slots.
- `drpc_hdlr_fini()` frees the registry.
- `drpc_hdlr_register()` validates initialization, module range, non-NULL handler, and duplicate registration.
- `drpc_hdlr_register_all()` registers a sentinel-terminated handler list and returns the last non-success status while continuing.
- `drpc_hdlr_get_handler()` validates and returns a module handler.
- `drpc_hdlr_unregister()` and `drpc_hdlr_unregister_all()` clear registrations.
- `drpc_hdlr_process_msg()` dispatches a request to its registered handler and sets `UNKNOWN_MODULE` when missing.

## Control flow
The registry is a global array indexed directly by module ID. Registration fails for invalid IDs, NULL handlers, uninitialized table, or already-used slots. Bulk registration/unregistration walks `struct dss_drpc_handler` entries until `handler == NULL`. Dispatch asserts request/response are non-NULL, looks up the handler, sets response status for unknown module, and otherwise calls the module handler.

## State and persistence behavior
State is process-local and volatile. There is no locking in this file, so expected usage is module initialization/teardown rather than concurrent dynamic registration while dispatching.

## Dependencies and integration
Depends on `daos/drpc_modules.h` for module count and `drpc_handler.h` for handler types. `drpc_listener.c` installs `drpc_hdlr_process_msg` as the listener callback, and `drpc_progress.c` eventually invokes that callback in handler ULTs.

## Risks
No synchronization protects `registry_table`. `drpc_hdlr_fini()` does not NULL the pointer after free, so accidental post-fini calls can pass the uninitialized check if memory still appears non-NULL. Bulk registration can partially succeed and leave earlier handlers installed when a later one fails, requiring callers to unregister on error if atomicity is desired.

## Test signals
Existing `drpc_handler_tests.c` should cover init/fini, invalid module IDs, NULL handlers, duplicate registration, missing modules, bulk registration partial failure, unregister behavior, and dispatch status for unknown modules.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/engine/drpc_handler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/engine/drpc_handler.h -->
# sources/object-store/daos/src/engine/drpc_handler.h

## Purpose
Declares the public internal interface for the dRPC handler registry. It documents how module-specific dRPC handlers are registered and how listener code dispatches incoming calls.

## Important APIs
The header declares initialization/finalization, single and bulk registration, lookup, single and bulk unregistration, and `drpc_hdlr_process_msg()`. It also documents that each handler is responsible for parsing `Drpc__Call`, acting on it, and filling a response even for errors.

## Control flow and integration
Consumers initialize the registry during engine startup, register handler arrays from modules, and pass incoming calls to `drpc_hdlr_process_msg()`. The listener/progress layer does not know module-specific behavior; it only creates responses and calls this dispatcher.

## State and persistence behavior
The header does not define state, but the implementation uses a process-local registry. No persistent state is associated with handler registration.

## Dependencies
Includes `daos/drpc.h` for protobuf dRPC call/response types and `daos_srv/daos_engine.h` for `struct dss_drpc_handler` and `drpc_handler_t` definitions.

## Risks
The contract that handlers always produce a response is important; a buggy handler can leave response status/body inconsistent. The API does not expose locking or ownership semantics, implying startup/shutdown-only mutation.

## Test signals
Compile tests ensure module handler arrays match the declared type. Unit tests should validate the documented error codes and that dispatch handles missing modules without crashing.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/engine/drpc_handler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/engine/drpc_internal.h -->
# sources/object-store/daos/src/engine/drpc_internal.h

## Purpose
Collects private dRPC declarations shared by the engine listener, progress loop, client, and RAS code. It defines the listener socket path, progress/session/call context structures, lifecycle APIs, generic client init/fini, and readiness notification hook.

## Important APIs and types
- `drpc_listener_socket_path` is the engine listener UNIX socket path advertised to daos_server.
- `struct drpc_progress_context` holds the listener context and a linked list of session contexts.
- `struct drpc_call_ctx` bundles a session, incoming call, and response for asynchronous handler ULT execution.
- `struct drpc_list` links active dRPC sessions.
- `drpc_progress_context_create/close()` manage listener/session context lifetime.
- `drpc_progress()` polls listener and sessions.
- `drpc_listener_init/fini()` start/stop the listener ULT.
- `drpc_init/fini()` manage the client path to daos_server.
- `drpc_notify_ready()` tells daos_server the engine is ready.

## Control flow and integration
`drpc_listener_init()` creates a socket path and progress context, `drpc_progress()` accepts sessions and spawns handler ULTs, and `drpc_listener_fini()` stops and closes the context. Client-side code initializes its separate server socket path with `drpc_init()` and uses `dss_drpc_call()` declared elsewhere. RAS uses the client path and generated event protobufs.

## State and persistence behavior
All state is process-local and socket/file-descriptor based. There is no persistent storage; the socket path is a runtime artifact under `dss_socket_dir`.

## Dependencies
Includes dRPC API, GURT list, and RAS server header. It is included by all engine dRPC implementation files in this subset.

## Risks
The structures expose raw `struct drpc *` pointers with ownership comments saying they are pointers, not copies. Correct ref-counting and close ordering are therefore critical. Listener socket path is global and must be initialized before readiness notification and freed after listener shutdown.

## Test signals
Existing listener/progress/client tests cover most declared behavior. Additional tests should verify startup/fini ordering, null/invalid progress contexts, and readiness notification after listener path generation.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/engine/drpc_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/engine/drpc_listener.c -->
# sources/object-store/daos/src/engine/drpc_listener.c

## Purpose
Starts, runs, and tears down the engine's dRPC listener ULT. The listener exposes a per-engine UNIX-domain socket used by local daos_server/control-plane clients to send dRPC calls into the engine.

## Important APIs and functions
- `drpc_listener_init()` generates socket path, initializes status mutex, and starts the listener ULT.
- `drpc_listener_fini()` stops the listener, joins/frees the ULT, frees the mutex, and frees the socket path.
- `drpc_listener_run()` loops on `drpc_progress()` until stopped.
- `setup_listener_ctx()` unlinks any stale socket path, calls `drpc_listen()`, and wraps it in a progress context.
- `generate_socket_path()` formats `dss_socket_dir/daos_engine_<pid>.sock`.

## Control flow
Initialization creates `status.running_mutex`, calls `setup_listener_ctx()`, and creates a ULT on `DSS_XS_DRPC`. The ULT marks itself running and repeatedly calls `drpc_progress(ctx, 1000)`, logging all errors except timeout, then yields. Finalization sets running false, joins the thread, frees Argobots resources, and frees `drpc_listener_socket_path`. The progress context closes listener/session dRPC contexts from inside the listener ULT when the loop exits.

## State and persistence behavior
Runtime state is the static `status` struct and global socket path. The socket file is unlinked before listen setup to clear stale entries; no DAOS persistent state is touched.

## Dependencies and integration
Depends on Argobots, engine ULT creation, `drpc_hdlr_process_msg()` as the callback, `drpc_progress_context_create/close()`, and `dss_socket_dir`. `drpc_client.c` includes the listener path in readiness notification.

## Risks
If `ABT_mutex_create()` fails after socket path allocation, the path is not freed in `drpc_listener_init()`. `drpc_listener_fini()` assumes init/start succeeded enough for `status.thread` and mutex to be valid. Unlinking the socket path before listen is practical but can remove a live socket if path generation collides, though PID-based naming should avoid that.

## Test signals
Existing listener tests should validate socket setup, ULT start/stop, progress error handling, stale socket unlink behavior, mutex/thread cleanup, and readiness path visibility. Failure-injection tests should cover listen/progress-context/ULT creation failures.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/engine/drpc_listener.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/engine/drpc_progress.c -->
# sources/object-store/daos/src/engine/drpc_progress.c

## Purpose
Implements the polling/progress loop for the engine dRPC listener. It multiplexes the listener socket and active session sockets, accepts new connections, receives calls, creates responses, dispatches handlers in ULTs, and cleans up failed/disconnected sessions.

## Important APIs and functions
- `drpc_progress_context_create()` validates a listener and initializes the session list.
- `drpc_progress_context_close()` closes all sessions, closes the listener, and frees context memory.
- `drpc_progress()` is the exported poll/progress entry point.
- Internal helpers map poll events to activity, convert progress contexts to poll arrays, accept listener connections, create/free call contexts, spawn handler ULTs, and process session/listener activity.

## Control flow
`drpc_progress()` validates the context, builds an array of `unixcomm_poll` entries for every session plus the listener, calls `poll()`, and if activity exists, processes sessions first and listener second. Session `POLLIN` calls `handle_incoming_call()`, which receives a `Drpc__Call`, creates a response even for protocol errors, sends failed-unmarshal responses inline, or creates a `drpc_call_ctx` and hands ownership to a handler ULT on `DSS_XS_SYS`. Handler ULTs call `session->handler`, send the response, then free call, response, and session ref. Session errors/hangups destroy the session node. Listener `POLLIN` accepts a new session and adds it to the list.

## State and persistence behavior
All state is volatile: file descriptors inside `struct drpc`, linked session nodes, and in-flight call contexts. The function closes sessions on failures to prevent dead descriptors lingering.

## Dependencies and integration
Depends on POSIX `poll`, dRPC context/session APIs, Argobots yield through session callbacks, DAOS ULT creation, GURT lists, and the listener-installed handler callback. It is driven by `drpc_listener.c` and exercised by the engine dRPC tests.

## Risks
The poll array is a variable-length stack array in `unixcomm_poll()` sized by active session count; very high session counts could pressure stack. `get_open_drpc_session_count()` uses `drpc_is_valid_listener()` for sessions, which is semantically surprising but likely matches dRPC listener/session representation. Processing sessions before the listener means new accepts can be delayed by heavy session churn. If ULT creation fails after adding a session ref, `free_call_ctx()` must correctly drop that ref.

## Test signals
`drpc_progress_tests.c` has strong coverage: invalid contexts, timeout and poll failures, accept failure, valid/bad calls, session cleanup on recv failure/no data/POLLERR/POLLHUP/ULT failure, listener POLLERR/POLLHUP, and context close variants. Additional stress tests could cover many simultaneous sessions and back-to-back calls.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/engine/drpc_progress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/engine/drpc_ras.c -->
# sources/object-store/daos/src/engine/drpc_ras.c

## Purpose
Builds, logs, and sends DAOS RAS events from the engine to daos_server/control plane over dRPC. It handles generic RAS events, formatted messages, pool service replica update events, SWIM rank-dead events, and self-termination events.

## Important APIs and functions
- `ds_notify_ras_event()` raises a generic event with optional string extended info and default rank.
- `ds_notify_ras_eventf()` formats a message into the fixed RAS field size and delegates.
- `ds_notify_pool_svc_update()` sends a pool-service update event with typed extended info and waits for response.
- `ds_notify_swim_rank_dead()` and `ds_notify_rank_self_terminated()` send predefined state/info events.
- Internal `init_event()`, `log_event()`, `send_event()`, and `raise_ras()` assemble, log, serialize, send, and free event data.

## Control flow
`init_event()` fills mandatory fields: ISO8601-like local timestamp with timezone, event id/type/severity, process id, xstream/thread id, hostname, and message. It then fills optional rank/incarnation/job/pool/container/object/control-operation fields, formatting UUIDs and object IDs as strings. `raise_ras()` logs the event locally, calls `send_event()`, and reports dRPC errors. `send_event()` packs `Shared__ClusterEventReq`, calls `dss_drpc_call(DRPC_MODULE_SRV, DRPC_METHOD_SRV_CLUSTER_EVENT, ...)`, optionally waits/checks response status, and frees allocated event strings.

## State and persistence behavior
No persistent local state. Events are transient protobuf messages sent to control-plane state/logging systems. The local engine log receives a human-readable event string at severity-dependent log level.

## Dependencies and integration
Depends on generated `event.pb-c.h`, server dRPC client, RAS string conversion helpers, engine globals (`dss_hostname`, module info), CRT rank queries, rank-list conversion for pool service info, and server protobuf definitions. Consumers throughout the engine call these notification APIs.

## Risks
There appears to be double-free potential: `send_event()` calls `free_event(evt)` before returning, and `raise_ras()` calls `free_event(evt)` again. If `D_FREE` nulls its argument macro-safe this may be benign, but the pointer fields are not visibly reset in `free_event()`. `init_event()` does not check allocation failures for pool/container/object string fields after `D_ASPRINTF()`. Formatted messages are truncated with a `$` marker but remain null-terminated only because `vsnprintf` wrote the buffer. Fire-and-forget events use `DSS_DRPC_NO_RESP`, so delivery failures may be limited to transport errors.

## Test signals
Tests should cover mandatory-field validation, hostname/module-info failure, default rank fallback, UUID/object formatting, formatted truncation, dRPC transport and response failures, pool service extended info conversion, no-response versus wait-for-response modes, and memory ownership/free behavior in success and failure paths.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/engine/drpc_ras.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/engine/event.pb-c.c -->
# sources/object-store/daos/src/engine/event.pb-c.c

## Purpose
Generated protobuf-c implementation for RAS event messages from `event.proto`. It provides serialization APIs and descriptors for engine/control-plane RAS event traffic.

## Important APIs and descriptors
Generated functions cover `Shared__RASEvent__EngineStateEventInfo`, `Shared__RASEvent__PoolSvcEventInfo`, `Shared__RASEvent`, `Shared__ClusterEventReq`, and `Shared__ClusterEventResp`. The main event descriptor has 19 fields, including id, message, timestamp, type, severity, hostname, rank, incarnation, hardware/process/thread/job/pool/container/object/control-operation fields, and a oneof extended info (`str_info`, `engine_state_info`, `pool_svc_info`).

## Control flow
Init functions assign static init templates. Size/pack/pack-to-buffer/unpack/free helpers assert descriptor identity and delegate to protobuf-c. Descriptor tables define field names, field numbers, labels, types, struct offsets, default strings, oneof case offsets, nested descriptors, name indexes, and number ranges. Cluster event request/response descriptors wrap a sequence number plus event or status.

## State and persistence behavior
No mutable DAOS state. Static descriptors encode the protobuf wire schema used by `drpc_ras.c` and the control plane. Serialized events become dRPC payloads and then external RAS/control-plane records.

## Dependencies and integration
Includes `event.pb-c.h` and protobuf-c. `drpc_ras.c` uses `shared__cluster_event_req__get_packed_size()` and `shared__cluster_event_req__pack()` to send events; typed event info descriptors support pool service and engine state events.

## Risks
Generated files must stay synchronized with `event.proto` and remote consumers. Oneof fields depend on setting `extended_info_case` correctly; forgetting it can silently omit extended data. Manual edits are unsafe. Field number changes are wire incompatible.

## Test signals
Tests should pack/unpack generic string-info events, pool service events with repeated ranks, engine state events, empty optional fields, and cluster responses with nonzero status. Regeneration checks should detect drift from `event.proto`.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/engine/event.pb-c.c -->

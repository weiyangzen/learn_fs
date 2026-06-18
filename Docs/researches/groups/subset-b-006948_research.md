# Research: subset-b-006948

Grouped source-tree-aligned research for the Ceph OSD files in work item `subset-b-006948`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/objclass.cc -->
# sources/distributed-fs/ceph/src/osd/objclass.cc

## Purpose

`objclass.cc` implements the classic OSD-side object class helper ABI. Object class methods receive an opaque `cls_method_context_t`; this file casts it back to `PrimaryLogPG::OpContext **`, builds one or more `OSDOp` records, and dispatches them through `PrimaryLogPG::do_osd_ops()`. It is the bridge that lets dynamically loaded class code read, write, stat, mutate xattrs, manipulate omap, inspect request/cluster metadata, and start class gather operations without knowing `PrimaryLogPG` internals.

## Important APIs and Functions

The C-style helpers include `cls_call`, `cls_getxattr`, `cls_setxattr`, `cls_read`, and `cls_get_request_origin`. The C++ helpers add object lifecycle and IO APIs such as `cls_cxx_create`, `cls_cxx_remove`, `cls_cxx_stat`, `cls_cxx_stat2`, `cls_cxx_read2`, `cls_cxx_write2`, `cls_cxx_write_full`, `cls_cxx_replace`, `cls_cxx_truncate`, and `cls_cxx_write_zero`. Attribute and omap helpers include `cls_cxx_getxattr`, `cls_cxx_getxattrs`, `cls_cxx_setxattr`, `cls_cxx_map_get_all_vals`, `cls_cxx_map_get_keys`, `cls_cxx_map_get_vals`, `cls_cxx_map_read_header`, `cls_cxx_map_get_val`, `cls_cxx_map_get_vals_by_keys`, `cls_cxx_map_set_val`, `cls_cxx_map_set_vals`, `cls_cxx_map_clear`, `cls_cxx_map_write_header`, `cls_cxx_map_remove_range`, and `cls_cxx_map_remove_key`. Cluster/object metadata helpers expose version, subop number, features, OSD release constraints, config, object info, snapset sequence, manifest reference count, allocation size, and pool stripe width. `cls_cxx_chunk_write_and_set` composes a write with a `cas.chunk_set` class call, and `cls_cxx_gather`/`cls_cxx_get_gathered_data` manage multi-object class gather state through `GatherFinisher`. `cls_log` provides object-class logging.

## Control Flow

Most helpers allocate a local `std::vector<OSDOp>`, fill the operation opcode and union fields, encode request payload into `OSDOp::indata`, and invoke `(*pctx)->pg->do_osd_ops(*pctx, ops)`. Return handling is consistent: negative values propagate; successful reads either `malloc` and copy to C buffers or move `bufferlist` output into caller-owned objects. Decoding helpers catch `ceph::buffer::error` and convert malformed OSD replies to `-EIO`. Gather setup stores a finisher in `OpContext::op_finishers` keyed by the current subop number, initializes a result map for all source objects, then asks `PrimaryLogPG::start_cls_gather()` to run the distributed class call.

## State and Persistence Behavior

The file itself owns no durable state. Persistence is delegated to generated OSD operations, so object data, xattrs, omap state, snapshots, rollbacks, and deletes follow normal PG transaction semantics. Temporary state is limited to in-flight `OSDOp` vectors and `GatherFinisher::src_obj_buffs`, which lives in the op context until the relevant suboperation completes. `cls_current_version()` and object info accessors read projected PG/object state from the current operation context rather than querying storage directly.

## Dependencies and Integration Points

This file depends on `objclass/objclass.h` for the exported ABI, `PrimaryLogPG` for execution, `ClassHandler` for logging context, Ceph buffer encoding/decoding, config access, and OSD operation constants. It is reached by dynamically loaded object classes and feeds back into the same OSD op execution path used by clients. The helper functions must stay wire-compatible with method payload encodings expected by `do_osd_ops()` and by omap/xattr/class op handlers.

## Risks and Test Signals

Key risks are ABI drift, incorrect opcode payload layout, missed length validation, malloc ownership mistakes in C helpers, and unexpected side effects from class helpers that compose multiple OSD ops. `cls_get_client_features()` assumes a live connection on the request. Omap helpers rely on decode shape stability. Gather logic asserts finisher insertion and couples tightly to `current_osd_subop_num`. Good test signals include object-class integration tests for read/write/xattr/omap/stat/rollback paths, negative decode tests, class method chaining via `cls_call`, gather completion behavior, and log-level gating for `cls_log`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/objclass.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/object_state.h -->
# sources/distributed-fs/ceph/src/osd/object_state.h

## Purpose

`object_state.h` defines the small in-memory state carriers used by OSD object context code. `ObjectState` holds projected `object_info_t` plus an `exists` bit. `RWState` implements the per-object read/write/exclusive lock state machine used to serialize client IO, recovery, snap trimming, and other object-scoped operations.

## Important APIs and Types

`ObjectState` has constructors from `object_info_t`, moved `object_info_t`, and `hobject_t`; an object constructed only from an object id starts as non-existent. `RWState::State` has `RWNONE`, `RWREAD`, `RWWRITE`, and `RWEXCL`. `RWState` exposes `get_read_lock()`, `get_write_lock(bool greedy=false)`, `get_excl_lock()`, `take_write_lock()`, `put_read()`, `put_write()`, `put_excl()`, waiter counters, `empty()`, `get_snaptrimmer_write()`, and `get_recovery_read()`. The stream operator renders state name, active count, and waiter count.

## Control Flow

Read locks are admitted only when there are no waiters, preventing starvation. Multiple readers can share `RWREAD`; multiple writers can share `RWWRITE`, which reflects Ceph's ability to pipeline compatible writes under higher-level ordering. Exclusive locks require `RWNONE`. Non-greedy writes also refuse admission if waiters exist or a recovery read marker is set; greedy and `take_write_lock()` paths bypass part of the fairness policy. `dec()` decrements the active count and resets state to `RWNONE` when the count reaches zero.

## State and Persistence Behavior

All state is volatile and object-context-local. `count`, `waiters`, `state`, `recovery_read_marker`, and `snaptrimmer_write_marker` coordinate in-memory scheduling only; they are not encoded or persisted. The markers remember that recovery or snap trimming should be requeued once the lock drains.

## Dependencies and Integration Points

The header depends on `osd_types.h` for `object_info_t`, `hobject_t`, and Ceph assertions. It is included by `osd_internal_types.h`, which embeds `RWState` into `ObjectContext`. `PrimaryLogPG` chooses lock types based on operation classification and calls through `ObjectContext`/`ObcLockManager` to acquire and release them.

## Risks and Test Signals

The risk surface is concurrency semantics: starvation policy, count/state invariants, marker clearing, and multi-writer assumptions. `ceph_assert` and `ceph_abort_msg` catch impossible unlocks or state values in debug/crash paths, but production correctness depends on every caller releasing the matching lock type. Useful tests exercise read sharing, read/write/exclusive exclusion, waiter blocking, greedy writes, recovery marker requeue, snaptrimmer marker requeue, and stream formatting used in diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/object_state.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/object_state_fmt.h -->
# sources/distributed-fs/ceph/src/osd/object_state_fmt.h

## Purpose

`object_state_fmt.h` supplies a `fmt` formatter specialization for `ObjectState`, letting fmt-based logging and diagnostics render object existence plus the embedded `object_info_t`.

## Important APIs and Types

The only public item is `template <> struct fmt::formatter<ObjectState>`. `parse()` accepts no custom format syntax and returns the beginning iterator. `format()` writes `exists <bool> oi <object_info_t>` through `fmt::format_to()`.

## Control Flow

Formatting is direct: callers using `fmt::format("{}", object_state)` enter the specialization, which delegates object-info rendering to the formatter support pulled in by `osd/osd_types_fmt.h`. For fmt 9 and newer the file includes `<fmt/ostream.h>`, allowing ostream-backed formatting where needed by dependent types.

## State and Persistence Behavior

There is no mutable or persistent state. The formatter only reads `ObjectState::exists` and `ObjectState::oi`.

## Dependencies and Integration Points

The header includes `osd/object_state.h` and `osd/osd_types_fmt.h`; it therefore tracks both the state struct and object info formatting contract. It integrates with any OSD code using fmtlib instead of ostream operators for structured diagnostics.

## Risks and Test Signals

The main risks are compile-time formatter drift when fmt versions change or when `object_info_t` formatting changes. Since parse accepts no specifiers, callers cannot request alternate layouts. Test signals are compile coverage under the repository's supported fmt versions and log/diagnostic tests that include `ObjectState` in fmt strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/object_state_fmt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/osd_internal_types.h -->
# sources/distributed-fs/ceph/src/osd/osd_internal_types.h

## Purpose

`osd_internal_types.h` defines core in-memory OSD object coordination types. It ties projected object state, snapset state, watcher maps, xattr cache, per-object locks, blocked-copy state, and lock-manager release behavior into the `ObjectContext` abstraction used heavily by `PrimaryLogPG` and backend code.

## Important APIs and Types

`SnapSetContext` stores an object id, `SnapSet`, reference count, registration bit, and existence bit. `ObjectContext` contains `ObjectState obs`, optional `SnapSetContext *ssc`, a destructor callback, watcher map keyed by `(cookie, entity_name_t)`, attribute cache, `RWState`, waiter queue, block flags, and methods for acquiring/releasing read, write, exclusive, recovery, and snaptrimmer locks. `ObcLockManager` owns a map from `hobject_t` to `{ObjectContextRef, RWState::State}` and releases all held locks in `put_locks()`.

## Control Flow

Object lock acquisition first tries the embedded `RWState`. If the lock is unavailable, `ObjectContext` appends the `OpRequestRef` to `waiters` when provided and increments `rwstate.waiters`. Unlock paths call `put_read()`, `put_write()`, or `put_excl()` and splice waiters into a caller-provided requeue list when the state drains. `put_lock_type()` also converts recovery and snaptrimmer markers into requeue booleans after the lock becomes empty. `ObcLockManager` records successfully acquired locks and later iterates them to release locks, collect per-object waiters, and clear its map.

## State and Persistence Behavior

All types here describe volatile projected state, not on-disk layout. `ObjectState::obs` mirrors projected object metadata before writes are committed. `SnapSetContext` mirrors snapset metadata and reference/registration status. Watcher and attr-cache maps are memory caches around durable object metadata. `blocked` and `requeue_scrub_on_unblock` coordinate in-progress copy-from and scrub scheduling. The `ObjectContext` destructor asserts no active locks remain and completes an optional callback, allowing `PrimaryLogPG` cache cleanup to observe destruction.

## Dependencies and Integration Points

The file depends on `osd_types.h`, `OpRequest.h`, `object_state.h`, and `Watch.h`. `PrimaryLogPG` creates, caches, locks, unlocks, blocks, and destroys `ObjectContext` instances across request processing, recovery, copy-from, cache tiering, snap trimming, and watcher management. `ReplicatedBackend`, EC code, scrubber paths, and watch code pass `ObjectContextRef` around as the in-memory handle for object-local coordination.

## Risks and Test Signals

Risks are lock leaks, waiter loss, stale projected state, raw `SnapSetContext *` lifetime errors, watcher/cache inconsistency, and missed requeue markers causing recovery or snaptrim stalls. `ObcLockManager`'s destructor assert is a useful guard but makes early returns dangerous unless `put_locks()` is reliably called. Test signals include operation ordering tests in `PrimaryLogPG`, copy-from block/unblock behavior, watcher timeout/blocklist tests, recovery and snaptrim requeue tests, and stress tests with simultaneous client IO and recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/osd_internal_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/osd_op_util.cc -->
# sources/distributed-fs/ceph/src/osd/osd_op_util.cc

## Purpose

`osd_op_util.cc` implements `OpInfo`, the OSD request classifier. It converts `MOSDOp` flags and contained `OSDOp` opcodes into RMW/capability/cache/promotion flags that later drive authorization, ordering, cache-tier behavior, EC read behavior, and operation scheduling.

## Important APIs and Functions

Accessor methods expose derived properties: `may_read()`, `may_write()`, `may_cache()`, `rwordered()`, `includes_pg_op()`, `need_read_cap()`, `need_write_cap()`, `need_promote()`, `need_skip_handle_cache()`, `need_skip_promote()`, `allows_returnvec()`, `ec_direct_read()`, `ec_sync_read()`, `may_read_data()`, and `may_read_data_for_ec()`. Setter methods OR individual `CEPH_OSD_RMW_FLAG_*` bits. The main APIs are `set_from_op(const MOSDOp *, const OSDMap&)` and `set_from_op(const std::vector<OSDOp>&, const pg_t&, const OSDMap&)`. The stream operator renders class method info.

## Control Flow

`set_from_op(MOSDOp*)` clears existing flags, imports request-level `RWORDERED` and `RETURNVEC`, then delegates to vector classification. The vector classifier loops over each `OSDOp`, marks write/read/cache/PG-op modes using `ceph_osd_op_mode_*` helpers, marks non-stat reads as data reads, and applies cache-tier promotion policy when a tier's base pool requires rollback. For `CEPH_OSD_OP_CALL`, it decodes class and method names from `indata`, opens the class through `ClassHandler`, obtains method flags, maps read/write/promote method flags into RMW bits, records `ClassInfo`, and translates class/method lookup failures into OSD error codes. Watch/notify paths force promotion and watch also forces read-data ordering. Delete/cache/read/writefull special cases set skip-promote or skip-handle-cache bits under narrow conditions.

## State and Persistence Behavior

`OpInfo` state is per request and in-memory: a `uint64_t rmw_flags` bitset and a vector of class method descriptors. It does not persist anything, but its decisions directly affect persistent behavior because promotion, rollback-required tiers, write ordering, and capability checks determine which OSD execution path handles the operation.

## Dependencies and Integration Points

The implementation depends on `OSDMap`, `MOSDOp`, `OSDOp` opcode helpers, `ClassHandler`, Ceph bufferlists, and pool metadata. `OpRequest` embeds `OpInfo`; `OSDCap` consumes class info for class-method authorization; `PrimaryLogPG` uses read/write/cache/promotion and ordering flags to choose locks, cache handling, and operation execution strategy.

## Risks and Test Signals

Classification errors can become security bugs, stale reads, unnecessary promotion, skipped promotion when data is needed, or broken EC behavior. Dynamic class lookup can fail at classification time, so error mapping must remain compatible with client expectations. The explicit allow/deny list for rollback-required tier promotion is fragile when new opcodes are added. Test signals include unit tests for every opcode category, class method flag tests, capability checks for class methods, cache-tier promotion behavior, delete FAILOK handling, watch ping ordering, and EC class read data classification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/osd_op_util.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/osd_op_util.h -->
# sources/distributed-fs/ceph/src/osd/osd_op_util.h

## Purpose

`osd_op_util.h` declares the `OpInfo` request-classification type used by OSD request processing. It presents a compact API for deriving read/write/cache/order/promotion/capability information from OSD operation vectors and for exposing object-class method metadata to authorization code.

## Important APIs and Types

`OpInfo::ClassInfo` stores class name, method name, read bit, write bit, and whether the class method is allowed. Private state is `uint64_t rmw_flags` plus `std::vector<ClassInfo> classes`. Public methods include `clear()`, `get_flags()`, all boolean predicates over the flag set, setters for individual categories, the two `set_from_op()` overloads, and `get_classes()`. A free `operator<<` formats `ClassInfo`.

## Control Flow

The header separates declaration from the policy implementation in `osd_op_util.cc`. Callers construct or reuse an `OpInfo`, call `set_from_op()` with a `MOSDOp` or op vector plus PG and `OSDMap`, then consult predicates such as `may_read()`, `may_write()`, or `need_promote()`. `clear()` resets only the flags; successful class classification appends to `classes` in the implementation.

## State and Persistence Behavior

`OpInfo` is transient request metadata. It is not encoded or persisted, but its flags influence persistent side effects by selecting OSD execution, ordering, promotion, and authorization paths. Because `get_classes()` returns a vector by value, consumers get a snapshot of class metadata rather than a mutable reference.

## Dependencies and Integration Points

The header includes `OSDMap` and `MOSDOp`, making the type part of the OSD request layer rather than a generic utility. It is included by `OpRequest.h`; `OpRequest::classes()` exposes `OpInfo` class metadata to capability checks in `OSDCap.cc`. `PrimaryLogPG` depends on `OpInfo` predicates to choose lock and cache behavior.

## Risks and Test Signals

The main API risk is stale `classes` entries if an `OpInfo` instance is reused and `clear()` resets only `rmw_flags`. That behavior should be reviewed against actual lifecycle expectations in `OpRequest`. Other risks are mismatched declarations and implementation when new RMW flags are added. Compile coverage, request classification tests, class authorization tests, and regression tests around reused `OpInfo` objects are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/osd_op_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/osd_perf_counters.cc -->
# sources/distributed-fs/ceph/src/osd/osd_perf_counters.cc

## Purpose

`osd_perf_counters.cc` registers the OSD, peering-state, and scrubber performance counters declared in `osd_perf_counters.h`. It maps numeric counter IDs to public metric names, descriptions, priorities, units, average types, and histograms through `PerfCountersBuilder`.

## Important APIs and Functions

`build_osd_logger(CephContext*)` creates the main `osd` counter set. It defines operation latency and request-size histogram axes, registers client op counters, replica read counters, subop/recovery counters, OSD map/cache/storage counters, cache-tier counters, object-context cache counters, PG info counters, watch timeout counters, and scrub IO/reservation/result counters split across replicated and EC pools. `build_recoverystate_perf(CephContext*)` creates `recoverystate_perf` latency and invalidation counters for peering state transitions. `build_scrub_labeled_perf(CephContext*, std::string label)` creates a labeled scrub counter family for shallow/deep and replicated/EC combinations.

## Control Flow

Each builder function constructs a `PerfCountersBuilder` with a name and numeric range, sets default priority as needed, calls `add_u64`, `add_u64_counter`, `add_time_avg`, `add_u64_avg`, or `add_u64_counter_histogram`, and returns `create_perf_counters()`. The main OSD logger starts with useful/critical operation metrics, lowers default priority for debug-only internal metrics, then raises priority for scrub metrics. Histogram configuration is local and declarative: op latency/request-size histograms use log2 scales, while scrub reservation replica-count uses a linear x axis and log2 duration y axis.

## State and Persistence Behavior

The file does not update counters and stores no persistent state. It defines the runtime schema of perf counters exposed by an OSD process. Counter values live inside the returned `PerfCounters` objects and are incremented elsewhere by `PrimaryLogPG`, `OSD`, scrubber, peering, and recovery code.

## Dependencies and Integration Points

It depends on `common/perf_counters.h`, `common/perf_counters_key.h`, `CephContext`, and the counter ID ranges in the header. Integration points found in the OSD tree include `PrimaryLogPG` increments for op latency, bytes, WIP, cache hits, and delayed ops; `OSD.cc` queue/dequeue latency updates; `PeeringState.cc` recovery-state latency updates; and scrubber code using both global scrub IDs and labeled scrub counters.

## Risks and Test Signals

The main risks are ID/name mismatches with the enum, duplicate or missing registrations, unit/priority mistakes that affect monitoring, and histogram axis choices that hide important latency ranges. Since external dashboards may rely on names, renames are compatibility-sensitive. Test signals include perf counter schema tests, daemon startup tests that build all counter sets, `ceph daemon osd.N perf dump` coverage, dashboard/telemetry compatibility checks, and scrub/peering workloads that verify counters move.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/osd_perf_counters.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/osd_perf_counters.h -->
# sources/distributed-fs/ceph/src/osd/osd_perf_counters.h

## Purpose

`osd_perf_counters.h` declares numeric performance-counter IDs for the OSD subsystem and factory functions that build the corresponding `PerfCounters` sets. It is the shared contract between metric registration and the many OSD call sites that increment counters by enum value.

## Important APIs and Types

`enum osd_counter_idx_t` reserves the `10000` range for main OSD counters, including client operation counts/bytes/latencies, read/write/rw breakdowns, delayed ops, replica reads, subops, recovery messages, map cache, storage stats, cache-tiering, object context cache, PG info, scrub reservation, watch timeouts, and scrub IO/result/reservation counters for replicated and EC pools. The file declares `build_osd_logger(CephContext*)`. A second anonymous enum starting at `20000` declares peering-state latency and invalidation counters plus `build_recoverystate_perf(CephContext*)`. A third anonymous enum starting at `20500` declares labeled scrub counters and `build_scrub_labeled_perf(CephContext*, std::string label)`.

## Control Flow

There is no executable control flow in the header. The enum order defines numeric IDs consumed by `osd_perf_counters.cc` registration and by callers invoking `PerfCounters::inc()`, `tinc()`, `hinc()`, and related update methods. Adding a counter requires adding the enum constant and registering it in the matching builder.

## State and Persistence Behavior

The header declares process-local metric IDs only. Counter values are runtime state inside `PerfCounters`; they are not persisted by these declarations. The numeric and string schema is externally observable through Ceph admin sockets and monitoring integrations.

## Dependencies and Integration Points

The header includes common Ceph forward declarations and perf counter builder types. It is included throughout OSD code wherever counters are updated: primary op handling, OSD queueing, peering-state machinery, scrubber code, and recovery/backfill code. `pg_scrubber.h` maps replicated and EC scrub counter groups to these IDs.

## Risks and Test Signals

Risks include accidentally reordering IDs, failing to register a declared ID, using an ID from the wrong counter set, and breaking external monitoring by changing names in the implementation. Because enum values are positional, inserting counters in the middle can affect consumers expecting stable numeric IDs. Test signals include build-time registration coverage, perf dump schema validation, monitoring integration tests, and workloads that exercise each counter family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/osd_perf_counters.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/osd_tracer.cc -->
# sources/distributed-fs/ceph/src/osd/osd_tracer.cc

## Purpose

`osd_tracer.cc` defines the global OSD tracing object declared in `osd_tracer.h`. It provides storage for `tracing::osd::tracer`, giving OSD code a single namespace-scoped tracing hook.

## Important APIs and Functions

The only symbol defined is `tracing::Tracer tracer` inside namespace `tracing::osd`. There are no functions or methods in this file.

## Control Flow

There is no runtime control flow beyond static/global object construction and destruction according to C++ initialization rules. Any actual tracing behavior is implemented by `common/tracer.h` and call sites that use this global.

## State and Persistence Behavior

The tracer object is process-local runtime instrumentation state. This file does not persist trace data itself; exporters or sinks configured by the common tracer infrastructure determine whether trace spans are emitted externally.

## Dependencies and Integration Points

The implementation includes `osd_tracer.h`, which includes `common/tracer.h`. Its integration point is any OSD code that references `tracing::osd::tracer` for span creation or tracing context.

## Risks and Test Signals

Risks are mostly link-time and initialization related: missing the single definition would cause unresolved externals, while defining it in multiple places would violate the one-definition rule. Test signals include successful OSD linkage with tracing enabled and smoke tests that create OSD tracing spans.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/osd_tracer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/osd_tracer.h -->
# sources/distributed-fs/ceph/src/osd/osd_tracer.h

## Purpose

`osd_tracer.h` declares the OSD subsystem's global tracing hook. It lets OSD source files share a common `tracing::Tracer` instance without including or defining storage themselves.

## Important APIs and Types

The public symbol is `extern tracing::Tracer tracer` in namespace `tracing::osd`. The type comes from `common/tracer.h`.

## Control Flow

The header has no executable flow. Including code can reference `tracing::osd::tracer`; the storage is supplied by `osd_tracer.cc`.

## State and Persistence Behavior

The declaration represents process-local tracing state. No persistent state is encoded here. Trace emission, sampling, and export behavior are delegated to the common tracing implementation and runtime configuration.

## Dependencies and Integration Points

The only dependency is `common/tracer.h`. This header should be included by OSD code that needs subsystem-level tracing, and it must remain paired with exactly one definition in `osd_tracer.cc`.

## Risks and Test Signals

Risks include namespace drift, missing definition during build changes, and accidental additional definitions. Test signals are compile/link coverage for OSD targets and runtime tracing smoke tests that verify spans can be emitted through the OSD tracer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/osd_tracer.h -->

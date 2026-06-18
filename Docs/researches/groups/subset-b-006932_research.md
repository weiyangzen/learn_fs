# Research Group: subset-b-006932

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/Paxos.h -->
# sources/distributed-fs/ceph/src/mon/Paxos.h

## Purpose
`Paxos.h` declares Ceph monitor Paxos, the replication substrate used by monitor services. It documents the monitor store layout: the Paxos prefix stores `first_committed`, `last_committed`, and one opaque encoded transaction per committed version. A committed Paxos value is also decoded and appended to the same `MonitorDBStore::Transaction` that records the Paxos version, so service state and Paxos metadata become durable atomically.

## Important APIs, Types, and Control Flow
The central type is `class Paxos`, owned by `Monitor` and friend to `PaxosService`. Its public surface includes election lifecycle (`init`, `restart`, `leader_init`, `peon_init`), message dispatch (`dispatch`), state sharing (`share_state`, `store_state`), read APIs (`is_readable`, `read`, `read_current`, `wait_for_readable`), write APIs (`is_writeable`, `get_pending_transaction`, `queue_pending_finisher`, `trigger_propose`), and trim/plug controls. The state machine constants cover recovery, active, updating, writing, refresh, and shutdown variants. Private handlers implement phase-1 collect/last handling, phase-2 begin/accept/commit handling, lease extension and timeout handling, and durable commit finish/abort paths.

## State and Persistence Behavior
Persistent state is version-based and stored through `MonitorDBStore`. Important volatile fields track proposal numbers, committed bounds, accepted proposal numbers, peer first/last committed versions, read lease expiry, pending and committing finishers, and timeout events. `decode_append_transaction()` is the key persistence helper: it decodes a service transaction from a bufferlist and appends it into a Paxos transaction. Trimming is guarded by config-derived minimums and `trimming`, while `extra_state_dirs` lets services such as OSD monitor register additional state areas.

## Dependencies and Integration Points
This header depends on monitor messaging (`MMonPaxos`, `MonOpRequest`), `MonitorDBStore`, Ceph contexts, perf counters, JSON formatting, clocks, config, and monitor types. It integrates with monitor elections, the monitor timer, monitor service transactions, peer state transfer, and perf counters identified by the `l_paxos_*` enum.

## Risks and Test Signals
Risks concentrate around state transitions, callback ordering, lease validity, atomic transaction composition, and trim safety. Tests should exercise single-monitor direct commits, multi-monitor collect/recovery with uncommitted accepted values, stale proposal rejection, lease timeout and lease ack timeout elections, read/write wait callbacks, durable transaction replay, and trim boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/Paxos.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/PaxosFSMap.h -->
# sources/distributed-fs/ceph/src/mon/PaxosFSMap.h

## Purpose
`PaxosFSMap.h` provides a small mixin-style holder for the CephFS `FSMap` as managed by a Paxos-backed monitor service. It separates the current committed map from a leader-only pending map and keeps bounded in-memory history by epoch.

## Important APIs, Types, and Control Flow
`class PaxosFSMap` exposes `get_fsmap()` for committed state and `get_pending_fsmap()` for leader-only pending reads. Implementers must provide `is_leader()`. Protected helpers include `get_pending_fsmap_writeable()`, `create_pending()`, `prune_fsmap_history()`, `put_fsmap_history()`, history threshold setters/getters, `get_fsmap_history()`, and `decode()`. `create_pending()` copies the committed `fsmap`, increments its epoch, and returns it for mutation. `decode()` decodes a committed map, inserts it into history if within the retention window, and clears `pending_fsmap` to catch invalid post-commit access.

## State and Persistence Behavior
The class itself does not write to disk; persistence is provided by the owning Paxos service. Its state is the current `FSMap`, the next `pending_fsmap`, a map of historical `FSMap` instances keyed by epoch, and `history_prune_time`. Pruning intentionally keeps at least the newest history entry and preserves the map just before the retention threshold so "last seen" style queries remain meaningful.

## Dependencies and Integration Points
It depends on `mds/FSMap.h`, `mds/MDSMap.h`, Ceph assertions, and `real_clock`. It is intended for the MDS monitor/Paxos service path, where committed FSMap versions are decoded from Paxos values and leader updates work against `pending_fsmap`.

## Risks and Test Signals
Risks include accidental pending-map access on peons, history pruning that removes too much context, and epoch mutation outside the leader-only path. Tests should cover leader assertions, pending epoch increments, decode reset behavior, history insertion and pruning with multiple birth times, and retaining the last history element.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/PaxosFSMap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/PaxosService.cc -->
# sources/distributed-fs/ceph/src/mon/PaxosService.cc

## Purpose
`PaxosService.cc` implements the common monitor-service orchestration around Paxos. It gates client/service messages on readable and writeable Paxos state, batches service-specific pending updates into the shared Paxos transaction, refreshes cached versions from the monitor store, trims old service versions, and persists service health checks.

## Important APIs, Types, and Control Flow
`dispatch()` is the main control flow: reject shutdown/stale election messages, ignore disconnected clients, wait for readability, run `preprocess_query()`, forward writes to the leader, wait for writeability, call `prepare_update()`, then immediately or eventually call `propose_pending()`. `should_propose()` dampens proposal frequency after startup. `propose_pending()` obtains `paxos.get_pending_transaction()`, optionally stashes a full copy, calls service `encode_pending()`, writes `format_version`, queues a `C_Committed` finisher, and triggers Paxos. `_active()` waits for Paxos active state, creates pending leader state, creates initial state when needed, wakes proposal waiters, runs format upgrades, and calls `on_active()`.

## State and Persistence Behavior
Cached `first_committed` and `last_committed` are refreshed from the service prefix. Versions are stored under the service name, full snapshots under `full/<version>`, and latest full snapshot under `full/latest`. `maybe_trim()` decides whether enough old versions can be removed, encodes trim operations, updates `first_committed`, lets services append extra trim metadata, and triggers a Paxos proposal. Health checks are encoded under the global `health` prefix keyed by `service_name`.

## Dependencies and Integration Points
This file integrates with `Monitor`, `Paxos`, `PaxosServiceMessage`, monitor timers, config knobs such as Paxos proposal and trim intervals, `MonitorDBStore`, health logging, and operation retry contexts. Service subclasses provide all domain-specific state transitions through virtual hooks declared in the header.

## Risks and Test Signals
Risks include callback ordering around proposals, stale forwarded requests, delayed proposal timers firing after elections, trimming too aggressively, and read waits that must choose between service-level and Paxos-level wait queues. Tests should cover read-only preprocessing, leader forwarding, delayed and forced proposals, election restart cancellation, initial state proposal, health persistence, format upgrades, and trim min/max behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/PaxosService.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/PaxosService.h -->
# sources/distributed-fs/ceph/src/mon/PaxosService.h

## Purpose
`PaxosService.h` declares the abstract base class for monitor services replicated through Paxos. It standardizes message dispatch, pending-state lifecycle, store key conventions, version caches, health-check persistence, read/write wait behavior, trimming, and full-state stashing.

## Important APIs, Types, and Control Flow
`PaxosService` stores references to `Monitor` and `Paxos`, the service name, proposal flags, `service_version`, `format_version`, and pending/proposal timers. Subclasses must implement `create_initial()`, `update_from_paxos()`, `create_pending()`, `encode_pending()`, `preprocess_query()`, `prepare_update()`, and `encode_full()`. Optional hooks include `post_paxos_update()`, `init()`, `discard_pending()`, `on_active()`, `upgrade_format()`, `on_upgrade()`, `on_restart()`, `tick()`, `get_trim_to()`, and `encode_trim_extra()`. Callback helpers `C_RetryMessage` and `C_ReplyOp` integrate monitor op retry and reply completion.

## State and Persistence Behavior
The class owns version cache fields, `waiting_for_commit`, `waiting_for_finished_proposal`, and standard store key names: `last_committed`, `first_committed`, `full`, and `latest`. Store helpers write committed version values, full snapshots, integer values, and arbitrary bufferlists under the service prefix. `put_last_committed()` also initializes `first_committed` on the first proposal to satisfy service assumptions.

## Dependencies and Integration Points
It depends on Ceph contexts, `health_check.h`, `MonitorDBStore`, and `MonOpRequest`. The class is the bridge between domain monitors such as OSD, MDS, auth, config, and manager services and the shared `Paxos` instance.

## Risks and Test Signals
Risks include subclass contract violations, proposing without pending state, stale cached versions, format-version mismatch handling, and incorrect distinction between Paxos active/readable/writeable and service active/readable/writeable. Tests should use fake subclasses to validate initial-state creation, callback waits, full snapshot stashing, store-key writes, trim extras, health encoding, and dispatch retry behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/PaxosService.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/Session.h -->
# sources/distributed-fs/ceph/src/mon/Session.h

## Purpose
`Session.h` defines in-memory monitor client/session tracking, including subscriptions to monitor maps, authenticated entity information, capabilities, feature accounting, proxied request fields, and lookup structures for OSD sessions.

## Important APIs, Types, and Control Flow
`Subscription` records a session, subscription type, next version, and one-shot flags. `MonSession` is refcounted and stores the `ConnectionRef`, peer identity, addresses, caps, auth handler, global id state, subscriptions, OSD epoch, proxy metadata, and last config state. `_ident()` initializes peer metadata from a connection. `is_capable()`, `get_allowed_fs_names()`, and `fs_name_capable()` delegate capability checks to `MonCap`. `dump()` emits session diagnostics.

`MonSessionMap` owns all sessions, subscription lists by type, OSD-session multimap, and a `FeatureMap`. `add_session()` sets timeout, links the session into lists, indexes OSD sessions, and increments feature counts. `remove_session()` clears subscriptions, removes list nodes and OSD index entries, decrements feature counts, marks closed, and drops the reference. `get_random_osd_session()` picks a likely OSD session and can validate it against the current `OSDMap`. Subscription helpers add, update, and remove per-session subscriptions.

## State and Persistence Behavior
This file manages volatile runtime state only. Session timeout, auth handler ownership, feature counts, and subscription lists are memory-resident and rebuilt as clients reconnect. Correct list membership is enforced by destructor assertions.

## Dependencies and Integration Points
It depends on `Connection`, message types, `FeatureMap`, `AuthServiceHandler`, `OSDMap`, `MonCap`, clocks, and intrusive `xlist`. It integrates with monitor command/message handling, subscription update fanout, auth, capability enforcement, config sharing, and OSD session selection.

## Risks and Test Signals
Risks include iterator misuse in `remove_session()` for OSD multimap entries, stale subscription pointers, feature-count leaks, capability mismatch, and auth handler lifetime. Tests should cover add/remove lifecycle, multiple subscriptions per session, OSD lookup with matching/mismatching addresses, feature map accounting, destructor invariants, and cap checks for monitor and filesystem-scoped permissions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/Session.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/error_code.cc -->
# sources/distributed-fs/ceph/src/mon/error_code.cc

## Purpose
`error_code.cc` implements the monitor-specific Boost error category. The monitor category mostly wraps POSIX-style negative errors while fitting Ceph's `ceph::converting_category` interface.

## Important APIs, Types, and Control Flow
`mon_error_category` overrides `name()`, both `message()` forms, `default_error_condition()`, `equivalent()`, and `from_code()`. `message()` returns `"No error"` for zero and delegates nonzero values to `cpp_strerror()`. `default_error_condition()` maps the monitor value to the generic category. `from_code()` converts Ceph's negative errno convention into a positive category value by returning `-ev`. `mon_category()` returns a function-local static singleton category.

## State and Persistence Behavior
There is no persistent state. The only state is the singleton static category object, initialized on first use. The file intentionally suppresses non-virtual-destructor diagnostics around Boost/category implementation details.

## Dependencies and Integration Points
It depends on `common/error_code.h`, `common/errno.h`, and `mon/error_code.h`. It integrates with any monitor code that returns `boost::system::error_code` or compares monitor errors to generic error conditions.

## Risks and Test Signals
Risks are mostly semantic: wrong sign conversion would break comparisons, and buffer-message truncation must stay NUL-terminated. Tests should cover `mon_category().name()`, zero/nonzero message strings, explicit `make_error_code()` behavior, equivalence with generic POSIX conditions, and conversion from negative errno values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/error_code.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/error_code.h -->
# sources/distributed-fs/ceph/src/mon/error_code.h

## Purpose
`error_code.h` declares monitor error-code integration with Boost.System. It provides the category accessor, an extensible monitor error enum, Boost traits, and conversion functions.

## Important APIs, Types, and Control Flow
The file declares `const boost::system::error_category& mon_category() noexcept`. `enum class mon_errc` is currently empty because monitor replies mostly use POSIX errors. Boost trait specializations mark `mon_errc` as an error-code enum but not an error-condition enum. `make_error_code(mon_errc)` and `make_error_condition(mon_errc)` wrap the enum's integer value with `mon_category()`.

## State and Persistence Behavior
No state is stored here. The header only defines inline conversion helpers and compile-time Boost trait metadata.

## Dependencies and Integration Points
It depends on Boost.System and `include/rados.h`. Including this header lets monitor code use implicit Boost error-code conversion once concrete `mon_errc` values are added.

## Risks and Test Signals
Risks include future enum additions with values that conflict with POSIX errno semantics or category sign handling in `error_code.cc`. Tests should compile-check implicit conversion, verify category identity, and add coverage whenever concrete monitor-specific errors are introduced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/error_code.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/health_check.h -->
# sources/distributed-fs/ceph/src/mon/health_check.h

## Purpose
`health_check.h` defines encoded monitor health payloads: individual health checks, muted health entries, and maps of health checks by code. These types are used by monitor services to persist and report cluster health state.

## Important APIs, Types, and Control Flow
`health_check_t` stores severity, summary, detail lines, and count. It has DENC version 2 with backward-compatible count decoding, equality operators, formatter dumping, and test instances. `health_mute_t` stores code, TTL, sticky flag, summary, and count with DENC support and dump/test helpers. `health_check_map_t` wraps `std::map<std::string, health_check_t>` and provides `clear`, `empty`, `swap`, `add`, `get_or_add`, `merge`, equality, dumping, and generated test instances.

## State and Persistence Behavior
The types are pure value objects serialized through Ceph DENC macros. `PaxosService::encode_health()` persists `health_check_map_t` values into `MonitorDBStore` under the `health` prefix, while `load_health()` decodes them. Merge behavior preserves existing summaries and appends details/counts for duplicate codes.

## Dependencies and Integration Points
It depends on `include/health.h`, `utime_t`, and `Formatter`. It integrates with monitor service health logging, manager/user health reporting, mute handling, and Ceph's encoding test infrastructure via `generate_test_instances()`.

## Risks and Test Signals
Risks include duplicate `add()` assertions, count loss in old encodings, detail growth during merges, and mismatch between severity/summary for duplicate codes. Tests should cover DENC round trips across versions, formatter output with and without details, merge semantics, mute TTL/sticky serialization, and `PaxosService` health persistence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/health_check.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/mon_types.h -->
# sources/distributed-fs/ceph/src/mon/mon_types.h

## Purpose
`mon_types.h` collects monitor-wide value types, service indexes, on-disk magic, feature bitsets, and serialized status payloads shared across monitor components.

## Important APIs, Types, and Control Flow
The Paxos service index enum maps service slots such as MDS map, OSD map, log, monmap, auth, mgr, health, config, key-value, and NVMe gateway. `FeatureMap` tracks entity type to feature mask to count and excludes monitor features from ordinary add/remove unless `add_mon()` is used. `MonitorDBStoreStats`, `DataStats`, and `ScrubResult` encode monitor store/disk/scrub summaries. `mon_feature_t` wraps monitor feature bits with set operations, containment checks, printing, dumping, encoding, and decoding. The `ceph::features::mon` namespace defines release features from Kraken through Umbrella, release-independent features, supported/persistent/optional sets, and name lookup.

## State and Persistence Behavior
Most structures are serialized values stored or exchanged by monitor code. `DataStats` decodes older versions that stored KB values by converting them to bytes. `ProgressEvent` preserves older behavior by setting `add_to_ceph_s` when decoding old non-empty messages. `PoolAvailability` stores pool uptime/downtime accounting. `infer_ceph_release_from_mon_features()` maps the highest contained release feature to a release enum.

## Dependencies and Integration Points
It depends on Ceph feature definitions, base types, formatters, bit-string helpers, release names, message address types, and clocks. It is used by monitor sessions, monitor maps, store stats reporting, feature negotiation, release compatibility checks, progress reporting, and health/status output.

## Risks and Test Signals
Risks include feature-name mismatches, missing new features from supported/persistent sets, backward decode regressions, and inconsistent treatment of monitor features in `FeatureMap`. A notable compatibility signal is that `get_feature_by_name()` uses `"feature-pinging"` while `get_feature_name()` returns `"elector-pinging"`, so callers must be tested for expected accepted strings. Tests should cover encode/decode fixtures, feature set algebra, release inference ordering, FeatureMap add/remove assertions, and old-version decode paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/mon_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/CMakeLists.txt -->
# sources/distributed-fs/ceph/src/osd/CMakeLists.txt

## Purpose
`src/osd/CMakeLists.txt` defines the static `osd` library build composition for the Ceph OSD subsystem. It lists OSD, PG, scrubber, scheduler, EC, tracing, objecter/striper, and performance metric sources, then wires conditional tracing and runtime object-class dependencies.

## Important APIs, Types, and Control Flow
The file defines `osdc_osd_srcs`, conditionally enables GCC `-finstrument-functions` with exclusions for SIMD helper names, and defines `osd_srcs`. `add_library(osd STATIC ${osd_srcs})` creates the target. `target_link_libraries()` exposes `dmclock::dmclock` and `Boost::MPL` publicly and links internal options, objectstore, profilers, fmt, and dl libraries privately. Conditional `add_dependencies()` attach LTTng, eventtrace, and cyg-profile tracepoint generation.

## State and Persistence Behavior
There is no runtime state. Build state is expressed through target sources, link dependencies, compile options, and generated tracepoint dependencies. Object class libraries are declared as runtime dependencies so OSD builds bring in `libcls_*` modules needed for class execution.

## Dependencies and Integration Points
It integrates the classic and newer EC implementations (`ECBackend.cc` and `ECBackendL.cc`), scrubber components, objecter client code, manager OSD perf metric types, class handler support, and optional CephFS/RBD/RGW class libraries.

## Risks and Test Signals
Risks include duplicate or missing source entries, instrumentation flags leaking globally through `add_compile_options`, case mismatch in `set_source_files_properties(osdcap.cc)` versus `OSDCap.cc`, and forgotten runtime class dependencies when new object classes are added. Test signals include clean CMake configure/builds across feature combinations (`WITH_LTTNG`, `WITH_EVENTTRACE`, `WITH_OSD_INSTRUMENT_FUNCTIONS`, `WITH_CEPHFS`, `WITH_RBD`, `WITH_RADOSGW`) and link verification for dynamic class loading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ClassHandler.cc -->
# sources/distributed-fs/ceph/src/osd/ClassHandler.cc

## Purpose
`ClassHandler.cc` implements dynamic loading, registration, dependency resolution, execution, and shutdown for OSD object classes (`libcls_*`). Object classes provide methods and filters that can be invoked by OSD operations.

## Important APIs, Types, and Control Flow
`open_class()` locks the handler, checks configured permission via `_get_class()`, loads the class if needed, and returns its `ClassData`. `open_all_classes()` scans `osd_class_dir` for files matching `libcls_*` plus the platform shared-library suffix and opens permitted classes. `_get_class()` creates metadata and marks whether it is in the default allowed list. `_load_class()` calls `dlopen`, reads optional `class_deps`, recursively loads missing dependencies, invokes `__cls_init`, and marks the class open. Registration functions add methods and filters during initialization. `ClassMethod::exec()` handles both C++ and C object-class ABIs through a `std::variant`, claiming C ABI malloc output into a `bufferlist`.

## State and Persistence Behavior
State is process-local: the `classes` map stores class status, dlopen handle, method/filter maps, dependency sets, and allowed flag. `shutdown()` closes loaded handles and clears all class metadata. There is no durable persistence in this file.

## Dependencies and Integration Points
It depends on Ceph config (`osd_class_dir`, load/default lists), logging, `dlfcn` compatibility, object-class ABI definitions, and the global Ceph context. `ClassHandler::get_instance()` returns a singleton, with a Crimson-specific local context path.

## Risks and Test Signals
Risks include loading unpermitted classes, dependency recursion failures, class registration under the wrong name, ABI memory ownership mistakes, and iterator invalidation during shutdown/unregister. Tests should cover load allow/deny lists, missing `.so`, dlopen failure with existing file, dependency chains, registration and execution of C and C++ methods, filter registration, `open_all_classes()` directory scanning, and shutdown idempotence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ClassHandler.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ClassHandler.h -->
# sources/distributed-fs/ceph/src/osd/ClassHandler.h

## Purpose
`ClassHandler.h` declares the OSD object-class registry and loader interface. It models object classes, methods, and filters, and provides synchronized lookup/open APIs for OSD code.

## Important APIs, Types, and Control Flow
`ClassHandler` owns a `CephContext`, a map of class metadata, and a mutex. `ClassData` tracks load status (`CLASS_UNKNOWN`, `CLASS_MISSING`, `CLASS_MISSING_DEPS`, `CLASS_INITIALIZING`, `CLASS_OPEN`), class name, handler, dlopen handle, default allowed flag, method/filter maps, dependencies, and missing dependencies. It provides method/filter registration and lookup helpers. `ClassMethod` stores method name, a C or C++ callback variant, flags, and backpointer, with `exec()`, `unregister()`, and synchronized `get_flags()`. `ClassFilter` stores filter factory metadata.

## State and Persistence Behavior
All state is in-memory and protected by the handler mutex for lookup and flag reads. Object classes themselves are loaded from shared libraries by the `.cc` implementation; this header only declares the metadata and lifecycle.

## Dependencies and Integration Points
It depends on Ceph common types, `CephContext`, `ceph::mutex`, and object-class ABI declarations. It integrates with OSD operation execution paths that resolve a class method/filter by name and then call `exec()` or create filters.

## Risks and Test Signals
Risks include returning raw pointers into maps that may be invalidated by unload, insufficient locking during class initialization callbacks, duplicate registration behavior hidden by `try_emplace`, and methods with zero flags. Tests should compile-check ABI variants, verify method lookup and flags, simulate unregister behavior, and exercise concurrent open/lookup under the mutex.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ClassHandler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/Coroutines.h -->
# sources/distributed-fs/ceph/src/osd/Coroutines.h

## Purpose
`Coroutines.h` defines the minimal coroutine handle types used to integrate Boost.Coroutine2 with OSD backend code, especially synchronous-looking wrappers around asynchronous EC reads.

## Important APIs, Types, and Control Flow
The file aliases `yield_token_t` to `boost::coroutines2::coroutine<void>::pull_type` and `resume_token_t` to `push_type`. `CoroHandles` groups references to a yield and resume handle so a caller can yield while an async operation is outstanding and resume from its completion callback.

## State and Persistence Behavior
There is no persistent state and no ownership. `CoroHandles` contains references, so lifetime is entirely controlled by the caller/coroutine frame. Misuse after the coroutine frame exits would be unsafe.

## Dependencies and Integration Points
It depends only on Boost.Coroutine2. `ECBackend::objects_read_sync()` uses `CoroHandles` to call `objects_read_async()`, yield if the read has not completed, and resume when the callback fires.

## Risks and Test Signals
Risks include dangling handle references, double resume, completion before the caller marks itself waiting, and exceptions or cancellation paths that skip resume. Tests should exercise immediate completion, delayed completion, error completion, and cancellation/destruction of async contexts while a coroutine wrapper is waiting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/Coroutines.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/DynamicPerfStats.h -->
# sources/distributed-fs/ceph/src/osd/DynamicPerfStats.h

## Purpose
`DynamicPerfStats.h` implements dynamic OSD performance metric aggregation for manager-defined queries. It tracks counters per `OSDPerfMetricQuery` and key, updates them from OSD operations, merges reports, and emits bounded reports with optional sampling.

## Important APIs, Types, and Control Flow
Constructors initialize `data` from query lists. `merge()` adds counters from another instance by replaying query descriptors. `set_queries()` preserves matching existing counters while dropping disabled queries. `is_enabled()` checks if any query is active. The templated `add()` derives counter increments from op capabilities (`may_write`, `may_cache`, `may_read`), in/out bytes, latency, and query subkeys such as client id, client address, pool id, namespace, OSD id, PG id, object name, and snap id. `add_to_reports()` packs counters into `OSDPerfMetricReport` structures, either all groups or sampled groups when limits apply.

## State and Persistence Behavior
State is in-memory: a nested map from query to metric key to `PerformanceCounters`. There is no durable persistence. Report generation packs counters into bufferlists for manager reporting. Limited reports use weighted random sampling (A-Chao style) based on the chosen counter descriptor.

## Dependencies and Integration Points
It depends on random utilities, stringification, `MOSDOp`, and manager OSD perf metric types. It integrates with OSD op accounting and mgr perf query/report pathways, including Crimson and classic connection address handling.

## Risks and Test Signals
Risks include query descriptor mismatch during merge, regex subkey extraction failures, unsupported counter/subkey types aborting, random sampling bias, and limits ordered by a descriptor not present in the query. Tests should cover each counter type, each subkey type, query reconfiguration preserving counters, merge with multiple keys, report packing with and without limits, and deterministic sampling by controlled random seeds where possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/DynamicPerfStats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECBackend.cc -->
# sources/distributed-fs/ceph/src/osd/ECBackend.cc

## Purpose
`ECBackend.cc` implements the classic erasure-coded PG backend. It handles EC sub-op messages, read reconstruction, read-modify-write submission, recovery pushes, deep scrub reads, local/direct reads, and EC omap journal overlays for pools that support omap.

## Important APIs, Types, and Control Flow
The constructor wires `ReadPipeline`, `RMWPipeline`, `ECRecoveryBackend`, `ECSwitch`, `ErasureCodeInterface`, and `stripe_info_t`, then asserts the plugin's data chunk count and chunk size match the pool stripe width. `_handle_message()` dispatches EC write/read subops, replies, and PG push/push-reply messages. Recovery flows through `open_recovery_op()`, `recover_object()`, `run_recovery_op()`, `ECRecoveryBackend::run_recovery_op()`, `handle_recovery_push()`, and `commit_txn_send_replies()`.

For writes, `submit_transaction()` creates an `ECClassicalOp`, computes a write plan, and starts the RMW pipeline. `handle_sub_write()` applies replica-side transactions, updates stats and missing/log state, appends EC omap journal delete records when needed, registers a commit callback, queues transactions, and marks local apply. `handle_sub_write_reply()` tracks pending commits and finishes the RMW pipeline when all shards commit. For reads, `objects_read_async()` normalizes requested extents, calls `objects_read_and_reconstruct()`, slices reconstructed results back into caller buffers, and completes per-read contexts. `handle_sub_read()` reads shard data, attrs, omap headers, and omap entries; `handle_sub_read_reply()` merges responses, handles errors, determines whether enough shards are available via `minimum_to_decode()`, resends reads if alternate shards can help, and completes the read pipeline in order.

## State and Persistence Behavior
Durable state is stored through `ObjectStore::Transaction` and objectstore reads/writes via `ECSwitch`. The backend maintains volatile pipeline maps, recovery ops, temp-object tracking through the parent/switcher, and EC omap journal overlay state. Omap helpers merge in-memory journal updates and removed ranges with on-disk objectstore omap values for iterate, get, get-values, header, and key-check operations. `on_change()` clears the journal, resets pipelines, and clears recovery state.

## Dependencies and Integration Points
It depends on EC common/pipeline utilities, erasure-code plugin interface, EC message types, recovery messages, `PrimaryLogPG`, objectstore, scrub backend, tracing, and `ECSwitch`. It integrates tightly with `PGBackend::Listener` for log updates, stats, message sending, transaction queuing, recovery scheduling, OSDMap epochs, and scrub counters.

## Risks and Test Signals
Risks include minimum-shard calculations, read ordering under redundant/fast reads, suppressing harmless fast-read `ENOENT` without masking real corruption, omap overlay range semantics, transaction/log ordering, missing-state behavior during async recovery, and iterator erasure bugs in omap filtering. Tests should cover degraded reads, redundant reads with late errors, direct local reads, subchunk reads, RMW writes across data/parity shards, recovery push accounting, omap journal update/delete/range overlays, deep scrub digest behavior, error injection paths, and `on_change()` cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECBackend.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECBackend.h -->
# sources/distributed-fs/ceph/src/osd/ECBackend.h

## Purpose
`ECBackend.h` declares the classic erasure-coded OSD backend. It extends `ECCommon` and exposes PG backend hooks for recovery, EC subop handling, transaction submission, reads/reconstruction, scrub support, EC encode/decode helpers, and omap operations that account for EC journal overlays.

## Important APIs, Types, and Control Flow
Public hooks include `open_recovery_op()`, `run_recovery_op()`, `recover_object()`, `_handle_message()`, `can_handle_while_inactive()`, sub-write/read handlers and reply handlers, `check_recovery_sources()`, `on_change()`, `clear_recovery_state()`, `dump_recovery_info()`, and `submit_transaction()`. Read APIs include coroutine-backed `objects_read_sync()`, direct `objects_read_local()`, `extent_to_shard_extent()`, `objects_readv_sync()`, async `objects_read_and_reconstruct()`, RMW-specific reconstruction, and `objects_read_async()`. EC helpers include `ec_can_decode()`, `ec_encode_acting_set()`, `ec_decode_acting_set()`, and `ec_get_sinfo()`.

The nested `ECRecoveryBackend` adapts `RecoveryBackend` to EC-specific recovery and transaction reply behavior. `ECRecPred` and `ECReadPred` implement recoverability/readability predicates using the erasure-code plugin's `minimum_to_decode()` requirements and the local shard identity.

## State and Persistence Behavior
Members include the parent listener, Ceph context, `ECSwitch`, read and RMW pipelines, recovery backend, erasure-code plugin reference, and immutable `stripe_info_t`. Persistence occurs through objectstore transactions and reads in the implementation. Omap methods expose a journal-aware view over on-disk omap and in-memory EC omap changes.

## Dependencies and Integration Points
It depends on EC common headers, extent cache, listener interfaces, EC types/utilities, `OSD`, `PGBackend`, erasure-code interfaces, bufferlists, scrub backend, and coroutine aliases. It is the bridge between `PrimaryLogPG`/PG backend logic and erasure-code shard IO.

## Risks and Test Signals
Risks include API contract drift between `ECCommon`, `PGBackend`, and `ECSwitch`, incorrect shard-size mapping for legacy EC objects, predicate mistakes for subchunk-capable plugins, and omap behavior for unsupported pools. Tests should cover predicate outcomes for enough/insufficient shards, shard offset mapping, encode/decode helper round trips, recovery handle lifecycle, omap unsupported return codes, and objectstore integration through mocked listeners/switchers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ECBackend.h -->

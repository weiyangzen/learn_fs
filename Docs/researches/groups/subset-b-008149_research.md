# Research: subset-b-008149

Grouped research for DAOS engine sources under `sources/object-store/daos/src/engine`. Each section preserves the source path and is bounded for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/engine/event.pb-c.h -->
# sources/object-store/daos/src/engine/event.pb-c.h

## Purpose
Generated protobuf-c header for `event.proto`. It defines the C ABI used by DAOS engine/control-plane code to serialize and deserialize RAS cluster event notifications. The file is not handwritten business logic, but it is an integration contract: field numbers, oneof cases, init macros, and descriptors must match the `.proto` schema and the generated implementation.

## Important APIs, Types, and Functions
The primary types are `Shared__RASEvent`, `Shared__RASEvent__EngineStateEventInfo`, `Shared__RASEvent__PoolSvcEventInfo`, `Shared__ClusterEventReq`, and `Shared__ClusterEventResp`. `Shared__RASEvent__ExtendedInfoCase` models the protobuf oneof for opaque string data, engine-state details, or pool-service details. Generated methods include `*_init`, `*_get_packed_size`, `*_pack`, `*_pack_to_buffer`, `*_unpack`, and `*_free_unpacked` for the top-level event, request, and response messages. External descriptors such as `shared__rasevent__descriptor` are consumed by protobuf-c runtime calls.

## Control Flow
Callers initialize stack or heap messages with the generated `*_INIT` macros or `*_init` functions, fill scalar fields and pointer fields, then ask protobuf-c to pack them into a byte buffer. Receivers call `*_unpack`, inspect required fields and the `extended_info_case`, and release allocations with `*_free_unpacked`. Nested engine-state and pool-service structures are referenced by pointer from `Shared__RASEvent`.

## State and Persistence Behavior
This header owns no runtime state and persists nothing. It defines serialized state exchanged across process boundaries. The durable compatibility concern is wire-level schema stability: field numbers and oneof tags are effectively persistent API. Strings default to `protobuf_c_empty_string`, and repeated service-rank arrays are represented by `n_*` plus pointer pairs.

## Dependencies and Integration Points
The only direct dependency is `protobuf-c/protobuf-c.h`, with version guards requiring protobuf-c headers compatible with protoc-c output. DAOS RAS notification producers and consumers use this contract to communicate event identifiers, severity, host/rank/incarnation context, job/pool/container/object identifiers, control operation hints, and optional extended event data.

## Risks
Manual edits will be overwritten by regeneration and may desynchronize the C ABI from `event.proto`. Callers must keep the oneof discriminator consistent with the active union member. Pointer fields require lifetime care until packing completes. Schema changes can break older control-plane binaries if field semantics or required interpretation changes without compatibility handling.

## Test Signals
Useful tests are protobuf round trips for each event shape, control-plane compatibility tests using real RAS events, version-skew checks for generated files, and negative unpack tests for missing or unknown extended information. Build failures around descriptor symbols or protobuf-c version guards are also strong integration signals.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/engine/event.pb-c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/engine/init.c -->
# sources/object-store/daos/src/engine/init.c

## Purpose
`init.c` is the DAOS engine process entry point and lifecycle coordinator. It parses command-line options, initializes global libraries and server subsystems, opens the service to external traffic once management setup completes, handles process signals, and tears the engine down in dependency order.

## Important APIs, Types, and Functions
Public-facing helpers include `dss_set_join_version`, `dss_get_join_version`, `engine_in_check`, `dss_self_rank`, and `get_module_info`. Major private routines are `server_init`, `server_fini`, `dss_topo_init`, `abt_init`, `modules_load`, `dss_crt_event_cb`, `dss_crt_hlc_error_cb`, `server_id_cb`, `parse`, and `main`. Global configuration includes `daos_sysname`, `dss_hostname`, storage/NVMe/socket paths, NVMe memory sizing, instance index, topology handles, NUMA/core selection, module facility flags, storage tier count, and check mode.

## Control Flow
`main` parses options, blocks normal shutdown/debug signals while leaving fault signals unblocked, registers signal-stack fault handling, calls `server_init`, then waits on `sigwait`. `server_init` sets umask, starts HLC recovery, initializes TLS/debugging/topology/telemetry/dRPC/dbtree/Argobots/module framework/CART/placement/IV/modules/NVMe/services, notifies the parent `daos_server` over dRPC, waits for `DSS_INIT_STATE_SET_UP`, registers CART event/HLC callbacks, opens the xstream barrier, and records readiness metrics. `server_fini` reverses this order while preserving the important rule that module cleanup runs before xstreams are stopped because cleanup may create ULTs.

## State and Persistence Behavior
Most state is process-global configuration. `dss_join_version` is copied into xstream TLS after service startup; `dss_check_mode` changes module selection and retry behavior; topology data caches hwloc state and optional NUMA core maps. HLC recovery deliberately delays startup if needed so post-restart HLC values do not appear older than pre-restart values. Persistent storage is initialized indirectly through VOS/NVMe/server DB paths.

## Dependencies and Integration Points
The file coordinates Argobots, CART, dRPC, telemetry, DAOS debug/logging, TLS, hwloc, placement, handle hash tables, IV, BIO/NVMe, VOS dbtree class registration, and dynamically loaded DAOS modules. It also interacts with management through `drpc_notify_ready`, `ds_notify_*` RAS helpers, and CART rank/dead-rank events.

## Risks
Initialization ordering is fragile: TLS must precede debug ID callbacks, HLC recovery must end before modules read HLC, modules must load before module init, and xstreams must remain alive for cleanup. Topology validation has many edge cases around oversubscription, NUMA split, helper XS count, and `dss_core_offset` being stored as an unsigned sentinel initialized to `-1`. Event handling can intentionally SIGKILL the process when self-exclusion is detected.

## Test Signals
Strong coverage comes from engine startup/shutdown tests with different target/helper/NUMA options, check mode, invalid numeric options, dRPC notify failures, module load failures, CART event callbacks, HLC drift notification, and SIGUSR1/SIGUSR2 Argobots dump paths. Fault-injection around each `server_init` exit label should verify cleanup order and leak-free partial initialization.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/engine/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/engine/module.c -->
# sources/object-store/daos/src/engine/module.c

## Purpose
`module.c` implements the server-side dynamic module framework. It loads DAOS module shared libraries, resolves their exported `struct dss_module`, registers module TLS keys, RPC handlers, dRPC handlers, metrics hooks, setup/cleanup callbacks, and unloads modules during shutdown.

## Important APIs, Types, and Functions
`struct loaded_mod` tracks a `dlopen` handle, module interface pointer, list link, and init flag. Public functions include `dss_module_get`, `dss_module_load`, `dss_module_init_all`, `dss_module_unload`, `dss_module_setup_all`, `dss_module_cleanup_all`, `dss_module_init`, `dss_module_fini`, `dss_module_unload_all`, `dss_module_init_metrics`, `dss_module_fini_metrics`, and `dss_module_nr_pool_metrics`. `dss_modules[DAOS_MAX_MODULE]` provides fast module lookup by module id.

## Control Flow
`dss_module_load` validates the short module name, opens `lib<name>.so`, resolves `<name>_module`, checks `sm_name`, then links it into `loaded_mod_list`. `dss_module_init_all` walks the load order and calls `dss_module_init_one`, which invokes `sm_init`, registers TLS keys, DAOS RPC protocol handlers, dRPC handlers, and returns module facility bits. Cleanup paths unregister RPC and dRPC handlers, unregister keys, call `sm_fini`, close libraries, and free tracking objects. Setup runs in load order; cleanup runs reverse order.

## State and Persistence Behavior
Module state is in-process only: the loaded module list, `dss_modules` lookup array, and any module-owned state initialized behind `sm_init` or setup hooks. The framework does not persist data directly, but loaded modules such as VOS/pool/container may open persistent state as part of their own callbacks.

## Dependencies and Integration Points
This file depends on `dlopen`/`dlsym`/`dlclose`, GURT lists, DAOS RPC registration, dRPC handler registration, module TLS key registration, and telemetry metrics initialization. It is invoked from `init.c` around CART startup and from service setup/cleanup paths.

## Risks
The module list is protected by a pthread mutex for structural updates, but metrics helpers iterate without taking the lock; this assumes stable module lifetime after startup. `dss_module_init_one` removes and frees a module on init failure while `dss_module_init_all` is iterating, so error paths must remain list-safe. A module id outside `DAOS_MAX_MODULE`, duplicate id, or inconsistent name can corrupt dispatch expectations. Partial registration failures must unregister only what was already registered.

## Test Signals
Tests should cover successful and failed `dlopen`, missing symbol, mismatched module name, RPC/dRPC registration failures, reverse cleanup order, repeated unload of missing modules, metrics init/fini for SYS/TGT tags, and module lookup for CART-originated pseudo module ids above `DAOS_MAX_MODULE`.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/engine/module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/engine/profile.c -->
# sources/object-store/daos/src/engine/profile.c

## Purpose
`profile.c` provides a small DAOS server profiling API. It starts and stops per-xstream profiling data collection and associates profile output with the current engine rank and target id.

## Important APIs, Types, and Functions
The file exports `srv_profile_start(char *path, int avg)` and `srv_profile_stop(void)`. It uses `dss_get_module_info()` to access the current `struct dss_module_info`, especially `dmi_dp` for the active `struct daos_profile *` and `dmi_tgt_id` for target attribution.

## Control Flow
`srv_profile_start` gets the current module info, asks CART for the current rank via `crt_group_rank`, then calls `daos_profile_init` with output path, averaging option, rank, and target id. The resulting profile pointer is stored in `dmi->dmi_dp`. `srv_profile_stop` fetches that pointer, dumps profile data, destroys the profile object, and clears `dmi_dp`.

## State and Persistence Behavior
The only local state is the profile pointer stored in per-xstream module info. Profile output is persisted by the profiling library to the supplied path when dumped. There is no guard against starting twice on the same xstream without stopping first, so callers own sequencing.

## Dependencies and Integration Points
The file integrates with CART rank lookup, DAOS profile helpers, server TLS/module info, BIO/SMD includes, and dRPC internals. It is intended to be triggered by server management/profile control paths rather than normal request handling.

## Risks
`srv_profile_stop` assumes `dmi->dmi_dp` is valid; stopping without a successful start could pass NULL to profile helpers depending on their tolerance. Start failure after partial profile allocation depends on `daos_profile_init` cleanup semantics. Rank lookup failure prevents profiling and returns the CART error. Profile paths and averaging settings are not validated here.

## Test Signals
Tests should start and stop profiling on a valid xstream, inject `crt_group_rank` and `daos_profile_init` failures, call stop after start to verify pointer clearing, and exercise management plumbing that requests profile dumps from system and target xstreams.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/engine/profile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/engine/rpc.c -->
# sources/object-store/daos/src/engine/rpc.c

## Purpose
`rpc.c` contains server RPC utility wrappers around CART calls. It offers a synchronous send helper for ULT context and a reply helper that honors DAOS fail-location injection.

## Important APIs, Types, and Functions
`dss_rpc_send(crt_rpc_t *rpc)` sends a CART RPC and waits for completion through an Argobots eventual. `dss_rpc_reply(crt_rpc_t *rpc, unsigned int fail_loc)` sends a reply unless the supplied fail location is active. The private callback `rpc_cb` copies `cci_rc` into the eventual.

## Control Flow
`dss_rpc_send` creates an `ABT_eventual`, adds a CART request reference, sends the RPC with `crt_req_send`, waits for the callback to set completion status, frees the eventual, and returns the callback status. `dss_rpc_reply` checks `DAOS_FAIL_CHECK`; when not dropping the reply it calls `crt_reply_send` and logs failures.

## State and Persistence Behavior
No persistent state is owned here. The send helper temporarily owns an eventual and adds a CART request reference, relying on CART request lifecycle rules for the extra reference. The result status is transferred through callback memory owned by Argobots eventual storage.

## Dependencies and Integration Points
The file depends on `daos_srv/daos_engine.h` for CART, Argobots, DAOS error conversion, logging, and fail injection. It is a utility for server modules that need blocking-style RPC send/reply semantics inside ULTs.

## Risks
Blocking on `ABT_eventual_wait` requires the associated CART context to keep progressing elsewhere; otherwise deadlock is possible. If `crt_req_send` fails, the function frees the eventual but relies on request reference handling outside this wrapper. The reply helper silently drops replies when fail injection is enabled, which is intentional but can obscure tests if fail locations leak between cases.

## Test Signals
Useful tests include successful send completion, send callback error propagation, Argobots eventual create/wait failures, reply send failure logging, fail-location reply drop behavior, and integration tests proving the relevant CART context progresses while synchronous waits are active.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/engine/rpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/engine/sched.c -->
# sources/object-store/daos/src/engine/sched.c

## Purpose
`sched.c` implements the DAOS engine's custom Argobots scheduler and request admission/throttling layer. It multiplexes network polling, NVMe polling, and generic ULT execution; queues pool-scoped requests; applies VOS space-pressure throttling; rejects overload early; tracks sleep/wakeup state; and monitors long-running or inactive ULTs.

## Important APIs, Types, and Functions
Key internal types are `sched_request`, `sched_pool_info`, `sched_req_info`, `stats_window`, `sched_cycle`, and `sched_data`. Exported functions include `dss_sched_init`, `dss_sched_fini`, `sched_req_enqueue`, `sched_req_get`, `sched_req_put`, `sched_req_sleep`, `sched_req_yield`, `sched_req_wakeup`, `sched_req_abort`, `sched_req_wait`, `sched_req_space_check`, `sched_stop`, `sched_cur_msec`, `sched_cur_seq`, `sched_create_ult`, `sched_cond_wait`, `sched_cond_wait_for_business`, and `sched_exec_time`.

## Control Flow
Incoming RPCs enter through `sched_req_enqueue`. Anonymous or disabled-priority requests are immediately turned into ULTs; pool-scoped requests are wrapped in `sched_request`, placed in FIFO or sorted retry heap for update/fetch, or per-type lists for GC/scrub/migrate. Each scheduler cycle starts with network poll, refreshes timestamps, wakes sleeping requests, processes pool queues, calculates per-type kick limits, then runs generic ULTs and periodically NVMe poll ULTs. `check_space_pressure` queries VOS pool space, maps free-space ratios to pressure levels, and drives `throttle_io` or `throttle_sys`.

## State and Persistence Behavior
Scheduler state lives per xstream in `struct sched_info`, including idle request cache, sleep queue, FIFO queue, retry heap, pool hash, counters, telemetry nodes, current sequence/time, and watchdog fields. Pool state is cached in `sched_pool_info` records keyed by pool UUID and purged when VOS reports pool deletion and no requests/GC ULTs remain. No state is persisted, but scheduling decisions can affect externally visible latency, timeout, and ENOSPACE behavior.

## Dependencies and Integration Points
The scheduler integrates tightly with Argobots schedulers/pools/threads/tasks/futures, DAOS telemetry, VOS space queries, BIO NVMe polling, server xstream metadata, DAOS fail/error conventions, and module-provided request attributes. `srv.c` creates the scheduler for each xstream and the RPC handler feeds module request attributes into it.

## Risks
This is high-risk concurrency code. Queue counters, heap membership, request ownership, and GC sleeping counts must stay balanced across yield/sleep/wakeup/abort/shutdown. The pool hash is no-lock because scheduling runs on one xstream, so cross-xstream access would be unsafe. Overload estimation is approximate and may reject too aggressively or too late. Scheduler monitor intentionally kills the engine on prolonged inactivity when configured. Time moving backward is handled with warnings but may affect sleeps and watchdogs.

## Test Signals
Important signals include queue counter assertions, telemetry for wait/sleep/reject/cycle duration, overload retry behavior under large queues, VOS space-pressure throttling, retried RPC heap ordering, sleep wakeup timing, shutdown draining with sleeping requests, scheduler watchdog warnings, monitor SIGKILL behavior under injected stalls, and Argobots pool lifecycle tests.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/engine/sched.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/engine/server_iv.c -->
# sources/object-store/daos/src/engine/server_iv.c

## Purpose
`server_iv.c` implements DAOS server-side IV support on top of CART IV. It manages IV class registration, namespace lifecycle, key packing/unpacking, entry caches, leader-aware fetch/update/invalidate callbacks, lazy asynchronous operations, retry behavior, and namespace cleanup for pool service state.

## Important APIs, Types, and Functions
Key APIs include `ds_iv_class_register`, `ds_iv_class_unregister`, `iv_key_pack`, `iv_key_unpack`, `ds_iv_ns_create`, `ds_iv_ns_update`, `ds_iv_ns_start`, `ds_iv_ns_stop`, `ds_iv_ns_leader_stop`, `ds_iv_ns_cleanup`, `ds_iv_ns_reint_prep`, `ds_iv_ns_id_get`, `ds_iv_fetch`, `ds_iv_update`, `ds_iv_invalidate`, `ds_iv_init`, and `ds_iv_fini`. The CART callback table `iv_cache_ops` wires DAOS behavior into IV fetch/update/refresh/hash/get/put/pre-sync operations.

## Control Flow
Classes are registered by mapping a DAOS class id to DAOS class ops and a CART IV ops slot. Namespaces are created with a pool UUID and CART group, then assigned a monotonically increasing local namespace id. Fetch/update/invalidate operations set the key version/rank, pack the key, call CART IV, wait on an Argobots future, and optionally retry retryable, not-leader, and busy errors. Lazy sync clones the key/value and launches an async ULT on the system xstream.

## State and Persistence Behavior
Global process state includes class lists, namespace lists, namespace ids, tree topology, and dynamically grown CART IV class array. Per namespace state includes pool UUID, CART namespace handle, master rank/term, refcount, stop flag, condition variable, and cached `ds_iv_entry` list. Entries cache values and validity; class callbacks may customize allocation, update, refresh, validation, destruction, and private get/put state. State is memory-resident cache/coherency metadata, not directly persistent.

## Dependencies and Integration Points
The file depends on CART IV, Argobots futures/conditions, DAOS IV class definitions, DAOS SGL helpers, server rank/version/check-mode helpers, and scheduler sleep/ULT creation. Pool/container/object subsystems register IV classes and use namespaces to distribute service and object metadata coherently across ranks.

## Risks
Refcounting is subtle: namespace references are held across in-flight operations and callbacks, `ivc_on_get` pairs with `ivc_on_put`, and stop waits for refcount drain. Comments note a possible leak if private-entry allocation fails after `ivc_value_alloc`. Leader changes return `-DER_NOTLEADER` or `-DER_GRPVER` in specific paths; retry loops can run indefinitely until namespace stop. Key comparison defaults to equality when no class comparator exists, so class ops must be correct for nontrivial keys.

## Test Signals
Tests should cover class registration reuse of CART ops, duplicate class ids, namespace create/update/stop/refcount drain, fetch forwarding on non-leader, update rejection for stale master rank, lazy update cloning and cleanup, retry behavior under `-DER_NOTLEADER` and retryable errors, reintegration prep deleting selected IV classes, and leak checks around `ivc_on_get` failures.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/engine/server_iv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/engine/srv.c -->
# sources/object-store/daos/src/engine/srv.c

## Purpose
`srv.c` implements the DAOS engine service runtime: xstream topology, CPU/NUMA binding, CART context creation, per-xstream TLS, NVMe polling, scheduler integration, dRPC listener startup, shutdown draining, memory telemetry, RPC dispatch into the scheduler, and Argobots diagnostics.

## Important APIs, Types, and Functions
Important exports include `dss_ctx_nr_get`, `dss_xstream_set_affinity`, `dss_xstream_exiting`, `dss_xstream_cnt`, `dss_get_xstream`, `dss_sleep`, `dss_rpc_cntr_get`, `dss_rpc_cntr_enter`, `dss_rpc_cntr_exit`, `dss_srv_init`, `dss_srv_fini`, `dss_srv_set_shutting_down`, `dss_dump_ABT_state`, `dss_get_start_epoch`, `dss_set_start_epoch`, `dss_has_enough_helper`, and `dss_bind_to_xstream_cpuset`. `struct dss_xstream_data` owns global xstream lifecycle state.

## Control Flow
`dss_srv_init` allocates the xstream pointer array, creates synchronization primitives, initializes standalone TLS and local DB, registers BIO bulk ops, starts xstreams, notifies BIO that NVMe started, and starts the dRPC listener. `dss_xstreams_init` reads scheduler/chore environment settings and starts system, main I/O, and offload xstreams. Each `dss_srv_handler` sets affinity, initializes TLS/module info, optionally creates a CART context, registers RPC callbacks, initializes the server-side client scheduler, starts NVMe polling and chore queues, waits at the startup barrier, then progresses CART until shutdown.

## State and Persistence Behavior
Global runtime state includes target/helper counts, system xstream count, helper-pool mode, NVMe health bypass, start epoch, and `xstream_data`. Per xstream state includes scheduler, Argobots pools, shutdown/stopping futures, CART context id, target id, NVMe context, TSE scheduler, chore queue, memory stats, and RPC counters. Persistent storage is touched indirectly through `vos_sys_db_init` and BIO/NVMe contexts.

## Dependencies and Integration Points
The service integrates Argobots, hwloc, CART, dRPC, BIO/NVMe, VOS, telemetry, server TLS, scheduler, module dispatch, RAS/version helpers, and management fail-location parameters. `init.c` calls `dss_srv_init/fini`; CART invokes `dss_rpc_hdlr`; modules provide request attributes and retry-hint encoding.

## Risks
Startup and shutdown have complex synchronization: creator waits for each progress ULT initialization, non-SWIM xstreams wait on a barrier, shutdown sets stopping then shutdown futures, and handlers drain all pools before destroying TLS/CART/NVMe. Incorrect xstream-to-context assertions indicate topology bugs. Affinity selection has edge cases for NUMA, shared helper pools, and reserved system cores. `dss_srv_set_shutting_down` creates tasks on every xstream and assumes prompt execution.

## Test Signals
Coverage should include xstream count/context mapping for helper-pool and per-target helper modes, NUMA and non-NUMA affinity selection, startup failure cleanup at each init step, CART RPC dispatch scheduling and overload retry, NVMe poll ULT startup/failure, graceful shutdown draining blocked ULTs, memory telemetry under `D_MEMORY_TRACK`, dRPC listener lifecycle, and ABT dump signal output.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/engine/srv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/engine/srv.pb-c.c -->
# sources/object-store/daos/src/engine/srv.pb-c.c

## Purpose
Generated protobuf-c implementation for `srv.proto`. It provides message initialization, packing, unpacking, freeing, and descriptor metadata for dRPC messages exchanged between DAOS I/O engines and the control server.

## Important APIs, Types, and Functions
The file implements generated functions for `Srv__NotifyReadyReq`, `Srv__GetPoolSvcReq`, `Srv__GetPoolSvcResp`, `Srv__PoolFindByLabelReq`, `Srv__PoolFindByLabelResp`, `Srv__ListPoolsReq`, `Srv__ListPoolsResp__Pool`, and `Srv__ListPoolsResp`. It also defines `ProtobufCFieldDescriptor`, field index, range, and `ProtobufCMessageDescriptor` objects for each message.

## Control Flow
Each `*_init` copies a static init macro into the caller-provided struct. `*_get_packed_size`, `*_pack`, and `*_pack_to_buffer` assert the descriptor and delegate to protobuf-c runtime helpers. `*_unpack` delegates to `protobuf_c_message_unpack` with the matching descriptor. `*_free_unpacked` checks for NULL, asserts the descriptor, and releases unpacked memory through protobuf-c.

## State and Persistence Behavior
There is no mutable application state. Static const descriptors encode the wire contract: field names, field numbers, labels, C offsets, default values, packed repeated scalar flags, nested message descriptors, and package/name metadata. Serialized messages may persist in dRPC buffers only for the duration of request handling.

## Dependencies and Integration Points
The file includes `srv.pb-c.h` and uses protobuf-c runtime internals. dRPC client/server code uses these functions for notify-ready, pool service lookup, pool label lookup, and pool listing messages. `init.c` indirectly depends on `NotifyReadyReq` through `drpc_notify_ready`.

## Risks
Because this is generated code, manual edits risk divergence from `srv.proto`. ABI risks come from mismatched generated header/source versions, protobuf-c version mismatches, or schema changes that reuse field numbers incorrectly. Callers must supply arrays matching `n_*` counts for repeated fields and must not pass uninitialized messages to pack routines.

## Test Signals
Generated-code tests should focus on schema round trips for every message, packed repeated `uint32` service-rank arrays, nested `ListPoolsResp.Pool` messages, compatibility between generated header and source descriptors, and dRPC integration tests for ready notification and pool queries.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/engine/srv.pb-c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/engine/srv.pb-c.h -->
# sources/object-store/daos/src/engine/srv.pb-c.h

## Purpose
Generated protobuf-c header for `srv.proto`. It defines C structs, init macros, method prototypes, closure types, and descriptors for DAOS engine dRPC service messages.

## Important APIs, Types, and Functions
Messages include `Srv__NotifyReadyReq`, `Srv__GetPoolSvcReq`, `Srv__GetPoolSvcResp`, `Srv__PoolFindByLabelReq`, `Srv__PoolFindByLabelResp`, `Srv__ListPoolsReq`, `Srv__ListPoolsResp`, and nested `Srv__ListPoolsResp__Pool`. Generated methods cover initialization, packed-size calculation, packing, buffer packing, unpacking, and freeing for all top-level messages; the nested pool message has an init helper and descriptor.

## Control Flow
Callers build requests/responses by initializing structs, assigning scalar and pointer fields, setting `n_*` counts for repeated values, then packing via protobuf-c. Receivers unpack bytes to generated structs, inspect status/UUID/service-rank/list fields, and free unpacked messages with the generated free helpers.

## State and Persistence Behavior
The header defines serialized state but owns no live state. `NotifyReadyReq` carries engine runtime metadata such as primary/secondary CART URIs, context counts, dRPC listener socket, instance index, target count, HLC incarnation, and check-mode flag. Pool query responses carry DAOS status codes and service rank arrays.

## Dependencies and Integration Points
The file depends on protobuf-c headers and version guards. It is consumed by dRPC code connecting the engine to the control server, especially startup readiness and management pool lookup/listing operations.

## Risks
The repeated fields require correct `n_secondaryuris`, `n_secondarynctxs`, `n_svcreps`, and `n_pools` counts. The generated C field names encode proto names such as `drpcListenerSock` as `drpclistenersock`, so handwritten callers must use the generated names. Schema evolution must preserve wire compatibility for control-plane/engine version skew.

## Test Signals
Tests should verify message initialization defaults, notify-ready payloads with secondary providers, pool service response arrays, list-pools nested messages, unpack/free behavior under custom allocators, and build-time protobuf-c version compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/engine/srv.pb-c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/engine/srv_cli.c -->
# sources/object-store/daos/src/engine/srv_cli.c

## Purpose
`srv_cli.c` lets server code run DAOS client tasks from inside the engine. It provides a per-xstream TSE scheduler progress ULT and a helper to schedule tasks synchronously or asynchronously.

## Important APIs, Types, and Functions
The exported functions are `dsc_task_run(tse_task_t *task, tse_task_cb_t retry_cb, void *arg, int arg_size, bool sync)` and `dsc_scheduler(void)`. Private helpers are `dsc_progress`, `dsc_progress_start`, and `dsc_task_comp_cb`.

## Control Flow
Before running a client task, `dsc_task_run` ensures the current xstream has a DSC progress ULT. In synchronous mode it creates an `ABT_eventual` and registers `dsc_task_comp_cb` to copy task result into the eventual. If a retry callback is supplied, it is registered last so it runs first on completion. The task is scheduled with `tse_task_schedule`; synchronous callers wait on the eventual and return the task result.

## State and Persistence Behavior
The state is per-xstream: `dx->dx_dsc_started` prevents duplicate progress ULT creation, and `dx->dx_sched_dsc` is the TSE scheduler initialized in `srv.c`. No persistence is performed. Task completion status moves through task fields and optional Argobots eventual storage.

## Dependencies and Integration Points
This file depends on DAOS client task/event APIs, server xstream metadata, Argobots eventuals, and `dss_ult_create`. It is used by server subsystems that need to call client-layer APIs, such as recovery paths, while continuing to progress their TSE scheduler.

## Risks
The file notes that client APIs may acquire global pthread locks and block an entire xstream. Progress ULT lifetime is tied to xstream shutdown and loops until `dss_xstream_exiting`. Synchronous waits require the progress ULT to run; failures during callback registration must complete the task and free eventuals correctly. Callback ordering is deliberate for retry behavior.

## Test Signals
Tests should cover async and sync task execution, progress ULT single-start behavior, task scheduling failure, completion callback result propagation, retry callback ordering, eventual create/wait failures, and shutdown while the progress loop is active.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/engine/srv_cli.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/engine/srv_internal.h -->
# sources/object-store/daos/src/engine/srv_internal.h

## Purpose
`srv_internal.h` is the internal contract shared by DAOS engine implementation files. It defines xstream, scheduler, telemetry, NUMA, and chore queue data structures plus prototypes and inline helpers used across startup, scheduling, RPC dispatch, IV, and service lifecycle code.

## Important APIs, Types, and Functions
Core types include `struct dss_xstream`, `struct sched_info`, `struct sched_stats`, `struct sched_hist_seq`, `struct mem_stats`, `struct dss_chore_queue`, `struct engine_metrics`, and `struct dss_numa_info`. It declares globals such as `dss_engine_metrics`, `dss_hostname`, `dss_topo`, `dss_core_nr`, `dss_sys_xs_nr`, `dss_helper_pool`, `dss_tgt_offload_xs_nr`, and scheduler tunables. Inline helpers include `sched_relax_mode2str`, `sched_relax_str2mode`, `sched_xstream_stopping`, `sched_create_task`, `sched_create_thread`, `dss_xs2tgt`, and `dss_xstream_has_nvme`.

## Control Flow
The header does not execute top-level control flow, but its inlines gate common runtime paths. `sched_create_task/thread` reject creation when the current xstream is stopping, update busy timestamps for non-periodic work, and enqueue into the generic Argobots pool. `dss_xs2tgt` maps xstream ids to VOS targets differently depending on helper-pool layout. `dss_xstream_has_nvme` determines where NVMe contexts and poll ULTs are created.

## State and Persistence Behavior
The structures describe live in-memory state: per-xstream scheduler queues/counters, RPC counters, TSE scheduler, shutdown futures, telemetry handles, memory usage counters, chore queues, and topology data. No persistent state is stored here, but fields like target id, context id, start metrics, and rank metrics reflect persistent service identity.

## Dependencies and Integration Points
This header depends on DAOS engine public headers, telemetry, and GURT heap/list types. It links `init.c`, `srv.c`, `sched.c`, `module.c`, `server_iv.c`, metrics, and dRPC-related code. It is not a public API for external modules beyond engine internals.

## Risks
Because it exposes shared structs, layout changes affect many translation units. The inline `sched_xstream_stopping` assumes TLS is initialized for ULT callers and bypasses main-thread callers. `dss_xs2tgt` asserts ids are in range and depends on global target/helper counts being initialized. Adding fields without initialization in `srv.c` can produce subtle scheduler or shutdown bugs.

## Test Signals
Build coverage across all engine files is the main signal. Runtime tests should validate xstream-to-target mapping for helper layouts, NVMe-capable xstream detection, scheduler create rejection after stopping future is set, relax mode parsing, telemetry pointer initialization, and structure counter assertions during shutdown.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/engine/srv_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/engine/srv_metrics.c -->
# sources/object-store/daos/src/engine/srv_metrics.c

## Purpose
`srv_metrics.c` initializes global engine telemetry metrics that report startup readiness, rank identity, and received dead-rank event activity.

## Important APIs, Types, and Functions
It defines the global `struct engine_metrics dss_engine_metrics` and exports `dss_engine_metrics_init(void)` and `dss_engine_metrics_fini(void)`. Metrics created include `started_at`, `servicing_at`, `rank`, `events/dead_ranks`, and `events/last_event_ts`.

## Control Flow
`dss_engine_metrics_init` zeroes the global metrics struct, then creates each telemetry node with `d_tm_add_metric`. It returns immediately on any creation failure, logging the specific metric that failed. `dss_engine_metrics_fini` currently has no cleanup work and returns success.

## State and Persistence Behavior
The file owns process-global telemetry node pointers. Values are recorded elsewhere: `init.c` records startup and ready timestamps, sets rank, and CART event callbacks increment dead-rank counters and update last-event timestamp. Metrics are live telemetry state, not durable storage.

## Dependencies and Integration Points
It depends on `srv_internal.h` for `struct engine_metrics` and on GURT telemetry producer APIs. Initialization is called after `d_tm_init` in `server_init`; metrics are consumed by `init.c` and event callbacks.

## Risks
Partial initialization leaves some metric pointers NULL if a later metric creation fails. Callers that record metrics should tolerate missing telemetry nodes according to telemetry API semantics. `fini` doing nothing is correct only if telemetry teardown is centralized in `d_tm_fini`.

## Test Signals
Tests should inject `d_tm_add_metric` failures at each metric, verify successful node names and types, confirm startup/ready/rank/dead-rank updates from `init.c`, and run shutdown under telemetry leak detection.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/engine/srv_metrics.c -->

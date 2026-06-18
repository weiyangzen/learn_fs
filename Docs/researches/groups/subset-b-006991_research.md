# Group Research: subset-b-006991

This grouped report covers the RGW source files assigned to `subset-b-006991`. Each file section preserves the original source path so the reconciliation lane can split it into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_log.cc -->
## sources/distributed-fs/ceph/src/rgw/rgw_log.cc

Purpose: implements RGW usage logging and operation logging. It turns `req_state` plus optional `RGWOp` data into usage accounting batches, JSON/file/socket records, and encoded RADOS log objects.

Important APIs/functions: `render_log_object_name()` expands time and bucket tokens for RADOS log object names; `rgw_log_usage_init()`/`rgw_log_usage_finalize()` own the global `UsageLogger`; `rgw_format_ops_log_entry()` formats `rgw_log_entry` for JSON output; `rgw_log_op()` is the main request logging entry point. Concrete sink methods implement `OpsLogManifold`, `OpsLogFile`, `JsonOpsLogSink`, `OpsLogSocket`, and `OpsLogRados`.

Control flow: `rgw_log_op()` first calls `log_usage()` when enabled, then exits if ops logging is disabled. It validates bucket existence and UTF-8 bucket names, extracts object identity, request environment fields, URI, auth identity, token claims, optional x-headers, ownership, byte counters, timestamps, status, and transaction id, then sends the completed entry to the configured `OpsLogSink`. File logging is asynchronous: `OpsLogFile::log_json()` appends to an in-memory queue and wakes a thread that calls `flush()`.

State and persistence: `UsageLogger` keeps a mutex-protected `usage_map` keyed by user/bucket and flushes by timer or threshold through `driver->log_usage()`. `OpsLogFile` buffers `bufferlist` entries until flush to an append-only file. `OpsLogRados` encodes `rgw_log_entry` and writes it via `driver->log_op()` to an object name derived from configuration.

Dependencies/integration: depends on request state, SAL driver, REST logging filters, ACL owners, auth identity writers, `ACCOUNTING_IO`, Ceph timers, `OutputDataSocket`, and RADOS SAL. Main RGW setup wires these sinks in `AppMain::init_opslog()`.

Risks and test signals: file sink drops entries when the configured memory buffer is full; file flush retries with exponential sleep and can block its thread. The global `usage_logger` pointer has lifecycle assumptions around RGW startup/shutdown. `rgw_log_entry::generate_test_instances()` and `dump()` provide encoding/dump coverage signals, while integration tests should verify multi-delete `op_data`, requester-pays usage attribution, x-header filtering, and RADOS object-name rendering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_log.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_log.h -->
## sources/distributed-fs/ceph/src/rgw/rgw_log.h

Purpose: declares the serialized operation log model and the sink abstraction used by RGW request logging.

Important APIs/types: `delete_multi_obj_entry` and `delete_multi_obj_op_meta` capture per-object outcomes for S3 multi-object delete logs. `rgw_log_entry` is the central encoded log record, including owners, bucket/object identifiers, request/response fields, byte counts, elapsed time, headers, auth identity, STS claims, access key, temp URL, account/role ids, and optional Keystone scope. `OpsLogSink` is the sink interface; `OpsLogManifold` fans out to multiple sinks; `JsonOpsLogSink` formats entries; `OpsLogFile`, `OpsLogSocket`, and `OpsLogRados` provide concrete transports.

Control flow: implementations fill `rgw_log_entry`, then call `OpsLogSink::log()`. JSON sinks share formatter handling and delegate the resulting `bufferlist` to `log_json()`. The manifold returns failure when any child sink fails.

State and persistence: `rgw_log_entry::encode()` currently writes version 16 with legacy compatibility down to version 5. Decode has explicit branches for historical bucket id formats, old owner encoding, optional x-headers, token claims, identity fields, multi-delete metadata, account/role ids, and Keystone scope.

Dependencies/integration: includes common RGW request structures, `OutputDataSocket`, versioned owner conversion, SAL forward declarations, and Keystone scope. It is used by request execution, Lua `Request.Log()`, RADOS log storage, and admin/dump tooling.

Risks and test signals: backward-compatible decode branches are high risk because old logs may still be readable after upgrades. `WRITE_CLASS_ENCODER` and `generate_test_instances()` make this file a target for Ceph encoding tests. New fields must bump encode versions and add decode guards without breaking old clusters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_log.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_lua.cc -->
## sources/distributed-fs/ceph/src/rgw/rgw_lua.cc

Purpose: implements RGW Lua script context naming, script CRUD through the SAL Lua manager, script syntax verification, and optional LuaRocks package allowlist/install support.

Important APIs/functions: `to_context()` maps case-insensitive strings such as `prerequest`, `postauth`, `background`, `getdata`, and `putdata` to `rgw::lua::context`; `to_string()` reverses it. `verify()` loads a script into a Lua state without executing it. `script_oid()` creates persistent object ids as `script.<context>.<tenant>`. `read_script()`, `read_script_or_bytecode()`, `write_script()`, and `delete_script()` call `sal::LuaManager`. Package functions behind `WITH_RADOSGW_LUA_PACKAGES` manage allowlisted LuaRocks packages.

Control flow: script CRUD is a thin null-checked manager dispatch returning `-ENOENT` if no manager exists. `add_package()` shells out to `luarocks search --porcelain`, optionally restricts to binary rocks, removes previous versions by base package name, then records the allowlist entry. `install_packages()` reads the allowlist, creates a parent and temporary tree, sets `HOME`, optionally logs `luarocks config`, and installs each package into the tree while collecting failures.

State and persistence: scripts and package allowlists persist in the SAL Lua manager, not local memory. `install_packages()` creates transient install directories and returns the chosen directory to callers for `package.path`/`cpath` setup.

Dependencies/integration: depends on Lua C API, `lua_state_guard`, SAL driver/LuaManager, Boost.Process, filesystem, and `CEPH_LUA_VERSION`.

Risks and test signals: shell command construction with package names is sensitive to quoting and input validation. `mkdtemp()` mutates the template string and installation directories must be cleaned by the owner. Tests should cover context parsing, invalid script syntax, missing manager handling, LuaRocks-not-found behavior, allowlist replacement, and failed package collection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_lua.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_lua.h -->
## sources/distributed-fs/ceph/src/rgw/rgw_lua.h

Purpose: public interface for RGW Lua administration and script/package persistence.

Important APIs/types: `enum class context` lists execution contexts: `preRequest`, `postAuth`, `postRequest`, `background`, `getData`, `putData`, and `none`. Declarations expose `to_context()`, `verify()`, `write_script()`, `read_script()`, `read_script_or_bytecode()`, and `delete_script()`. When package support is compiled in, `packages_t` plus `add_package()`, `remove_package()`, `list_packages()`, `reload_packages()`, and `install_packages()` form the package management API.

Control flow: callers convert external context names to `context`, verify and persist scripts through `sal::LuaManager`, then later retrieve either source or cached bytecode for request/data/background execution.

State and persistence: this header defines no storage itself. The contract is that script data is keyed by tenant and context in the Lua manager, while package allowlists are globally managed through the default Lua manager.

Dependencies/integration: includes Lua version/type helpers, async yield support, SAL forward declarations, and `DoutPrefixProvider`. It is consumed by REST/admin Lua endpoints, request/data filters, and background script execution.

Risks and test signals: all APIs return negative errno-style codes, so callers must preserve those semantics. Tests should cover context-string compatibility because external admin APIs rely on these names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_lua.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_lua_background.cc -->
## sources/distributed-fs/ceph/src/rgw/rgw_lua_background.cc

Purpose: implements the RGW Lua background execution thread, a shared Lua-visible `RGW` table, and script-to-bytecode caching for faster request/data-context execution.

Important APIs/functions: `RGWTable::increment_by()` backs `RGW.increment()`/`RGW.decrement()`. `Background::start()`, `shutdown()`, `pause()`, and `resume()` control the runner thread. `initialize_lguard_state()` creates a limited Lua VM with libraries, package path, debug action, and the `RGW` table. `process_script_add()`, `process_scripts()`, and `get_script_bytecode()` manage bytecode cache updates.

Control flow: `run()` loops until stopped. If paused, it waits. Otherwise it initializes a fresh Lua state, reads the tenantless background script, executes it when present, updates success/failure counters, processes queued script compile work, and sleeps for `execute_interval` or until stop. `process_scripts()` drains a lockfree queue, reads updated scripts from `LuaManager`, compiles them with `luaL_loadstring()`, dumps bytecode using `lua_dump()`, and stores it in a shared cache.

State and persistence: persistent scripts live in `LuaManager`; runtime state is `rgw_map`, a mutex-protected in-memory map of string/integer/double/bool values visible to Lua as `RGW`. Bytecode cache is in-memory and protected by `std::shared_mutex`.

Dependencies/integration: used by `RGWRealmReloader::Pauser`, request/data Lua contexts, SAL Lua manager, perf counters, and Ceph thread naming/logging.

Risks and test signals: `RGWTable::increment_by()` manually calls `mtx.unlock()` while using `unique_lock`, which is a correctness hazard if reached. Queue capacity is fixed at 16 and dropped pushes are silently retained only by unreleased ownership behavior. Tests should cover pause/resume, absent script, runtime/memory limit failures, map mutation/iteration, bytecode cache refresh/removal, and background table visibility from request/data scripts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_lua_background.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_lua_background.h -->
## sources/distributed-fs/ceph/src/rgw/rgw_lua_background.h

Purpose: declares the Lua background service and the Lua-visible `RGW` shared table metatable.

Important APIs/types: `BackgroundMapValue` is `std::variant<std::string, long long int, double, bool>`; `BackgroundMap` maps names to values. `RGWTable` implements `__index`, `__newindex`, `__len`, and `__pairs` for the `RGW` Lua table, including reserved `increment` and `decrement` function names. `Background` owns the runner thread, script manager, shared table, bytecode cache, and pauser hooks.

Control flow: writers call `put_table_value()` from C++ or assign `RGW[key]` from Lua. Lua writes validate supported value types, total key/value size, and max entry count; assigning `nil` erases keys and updates iterator metadata. Background lifecycle is start/shutdown/pause/resume, with script updates queued through `process_script_add()`.

State and persistence: table contents are process-local and disappear on restart. Cached bytecode is process-local. Script source persists through `LuaManager`.

Dependencies/integration: includes `rgw_realm_reloader.h`, `rgw_lua_utils.h`, Boost lockfree queue, shared mutexes, and Ceph logging. The class is held by `AppMain` and registered with the realm reloader pauser set.

Risks and test signals: table limits (`MAX_LUA_VALUE_SIZE`, `MAX_LUA_KEY_ENTRIES`) need boundary tests. Lua iterator invalidation logic is subtle, especially erasing during iteration. Background shutdown must join the thread before `LuaManager`/Ceph context teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_lua_background.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_lua_data_filter.cc -->
## sources/distributed-fs/ceph/src/rgw/rgw_lua_data_filter.cc

Purpose: runs Lua scripts in object data paths for GET and PUT, exposing the current data chunk as a Lua `Data` table.

Important APIs/functions: `BufferlistMetaTable` gives Lua 1-based byte indexing, `pairs()` iteration, and length for `bufferlist`. `RGWObjFilter::execute()` creates the Lua VM and global tables. `RGWGetObjFilter::handle_data()` and `RGWPutObjFilter::process()` wrap RGW data pipelines.

Control flow: each data chunk creates a memory/runtime-limited state, opens restricted standard libraries, installs `RGWDebugLog`, creates `Data`, `Request`, and `Offset` globals, optionally exposes background `RGW`, then calls `lua_execute()` with script or bytecode. GET and PUT wrappers ignore filter execution errors and continue the underlying data pipeline.

State and persistence: no persistent data is written. Lua sees the chunk `bufferlist` by pointer for the duration of execution. `Offset` identifies the logical offset. Background `RGW` accesses shared in-memory state if available.

Dependencies/integration: depends on `RGWGetObj_Filter`, `rgw::putobj::Pipe`, request Lua metatables, process environment Lua background pointer, and `lua_state_guard`.

Risks and test signals: per-chunk VM creation can be expensive. The script cannot mutate `Data` through this metatable, so behavior is observational unless scripts modify request/background state. Because errors are ignored by design, tests should assert request success despite Lua failure and should validate byte iteration boundaries, offsets, and package path/debug availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_lua_data_filter.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_lua_data_filter.h -->
## sources/distributed-fs/ceph/src/rgw/rgw_lua_data_filter.h

Purpose: declares Lua-backed GET/PUT object data filters.

Important APIs/types: `RGWObjFilter` stores `req_state*` and `LuaCodeType` and exposes `execute(bufferlist&, off_t, const char*)`. `RGWGetObjFilter` derives from `RGWGetObj_Filter` and overrides `handle_data()`. `RGWPutObjFilter` derives from `rgw::putobj::Pipe` and overrides `process()`.

Control flow: callers insert these wrappers into existing RGW data pipelines when `getdata` or `putdata` Lua scripts are configured. Each wrapper invokes `RGWObjFilter` and then forwards to the next filter/processor.

State and persistence: the classes retain only request/script references. Object data persistence remains owned by the surrounding GET/PUT pipeline.

Dependencies/integration: includes `rgw_op.h` for request and data pipeline base classes. Integrates with request Lua metatables and background Lua through the implementation.

Risks and test signals: `LuaCodeType` is copied into the filter, which is safe for script lifetime but may be costly for large bytecode. Tests should confirm forwarding still happens after Lua errors and that construction handles both source and bytecode variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_lua_data_filter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_lua_request.cc -->
## sources/distributed-fs/ceph/src/rgw/rgw_lua_request.cc

Purpose: implements the Lua request context, exposing RGW request state to scripts through nested Lua metatables and allowing selected request mutation, tracing, and logging.

Important APIs/functions: `create_top_metatable()` creates global `Request`. `execute()` runs a script/bytecode with request globals and optional integer return-code capture. `RequestLog()` invokes normal `rgw_log_op()`. `SetAttribute()` and `AddEvent()` expose tracing. Metatables model response errors, quotas, placement, user, trace, owner, bucket tags, bucket, object, ACL grants, IAM policies/statements, HTTP request info, copy source, zonegroup, and the top-level request.

Control flow: `execute()` creates a limited Lua state, opens libraries, sets package path from `s->penv.lua.manager`, creates debug action, installs `Request`, adds `RGW_ABORT_REQUEST`, attaches `Request.Log`, exposes background `RGW` if present, then calls `lua_execute()`. After success it attempts to read an integer return from the stack for script-controlled request handling.

State and persistence: scripts can mutate `s->err` response fields, `s->trace_enabled`, request HTTP metadata map, storage class, and empty-bucket URL name. Many nested structures are read-only. `Request.Log()` persists through configured ops-log sinks. Tracing calls persist in the active span when recording.

Dependencies/integration: depends on RGW request/operation state, ACL/IAM policy structures, SAL bucket/object interfaces, ops logging, trace span API, background Lua service, and Lua utilities.

Risks and test signals: the top-level script return-code path is suspicious because `lua_execute()` uses `luaL_dostring()`/`lua_pcall()` with zero expected results for bytecode, so returned values may not be consistently left on the stack. `RequestLog()` logs through normal sinks and may duplicate logs if scripts call it unexpectedly. Tests should cover every exposed field, write permissions, unknown field errors, trace no-op when not recording, IAM/ACL iteration, package path setup, abort return code semantics, and null/empty bucket/object cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_lua_request.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_lua_request.h -->
## sources/distributed-fs/ceph/src/rgw/rgw_lua_request.h

Purpose: declares the public request-context Lua execution API.

Important APIs: `create_top_metatable(lua_State*, req_state*, const char*)` exposes `Request` into an existing Lua state. Two `execute()` overloads run Lua source/bytecode with `RGWREST`, `OpsLogSink`, `req_state`, `RGWOp`, and optionally return an integer script return code by reference.

Control flow: users either create only the metatable for a larger Lua environment, as data filters do, or run a complete request-context script through `execute()`.

State and persistence: this header itself stores no state. The implementation can mutate request state and write ops logs through the provided pointers.

Dependencies/integration: uses forward declarations to avoid pulling in RGW operation internals. Consumed by request processing and data filters.

Risks and test signals: because pointer arguments are not owning, caller lifetime is critical. Tests should include null/empty optional objects and ensure both overloads return consistent errno-style results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_lua_request.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_lua_types.h -->
## sources/distributed-fs/ceph/src/rgw/rgw_lua_types.h

Purpose: defines the shared type used to carry either Lua source text or compiled Lua bytecode.

Important API/type: `using LuaCodeType = std::variant<std::string, std::vector<char>>;`.

Control flow: producers read scripts or bytecode from the Lua manager/background cache; consumers pass the variant to `lua_execute()`, which dispatches on the active alternative.

State and persistence: source strings and bytecode vectors are value types. Persistence is external to this header.

Dependencies/integration: included by Lua administration, request execution, data filters, and utility code.

Risks and test signals: callers must understand that `std::string` means executable source while `std::vector<char>` means Lua bytecode. Tests should cover both alternatives wherever scripts are executed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_lua_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_lua_utils.cc -->
## sources/distributed-fs/ceph/src/rgw/rgw_lua_utils.cc

Purpose: implements shared Lua runtime utilities: debug logging, library restriction, package path setup, memory/runtime guarded Lua state creation, and script/bytecode execution.

Important APIs/functions: `create_debug_action()` installs global `RGWDebugLog`; `stack_dump()` prints Lua stack diagnostics; `set_package_path()` sets Lua `package.path` and `package.cpath`; `open_standard_libs()` opens libraries and removes dangerous loaders/debug/`os.exit`; `allocator()` enforces memory limits; `lua_state_guard` owns a Lua state and perf counter accounting; `lua_execute()` runs a `LuaCodeType`.

Control flow: `lua_state_guard` creates a Lua state with a custom allocator, sets panic conversion to C++ exceptions, and optionally installs a runtime hook. The hook checks elapsed wall time on line/count events and raises Lua errors past the limit. Destructor disables limits for cleanup, closes Lua, logs possible leaks, and decrements VM counters.

State and persistence: state is per Lua VM. Memory usage is tracked in `lua_state_guard::mem_in_use`; runtime configuration is stored in the Lua registry as lightuserdata to guard-owned fields.

Dependencies/integration: depends on Lua C API, Ceph context/logging, perf counters, `CEPH_LUA_VERSION`, and `LuaCodeType`.

Risks and test signals: `pushtime()` in the header uses `std::localtime`, which is not thread-safe. The destructor computes a percentage with `max_memory`; logging when max is zero could be fragile if memory remains. `lua_execute()` for source uses `luaL_dostring()`, which discards detailed result handling expectations. Tests should cover memory-limit allocation failure, runtime limit, restricted globals, package path values, bytecode load errors, and perf counter increments/decrements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_lua_utils.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_lua_utils.h -->
## sources/distributed-fs/ceph/src/rgw/rgw_lua_utils.h

Purpose: declares and templates the Lua metatable framework used to expose C++ RGW state safely to Lua scripts.

Important APIs/types: `lua_state_guard` owns a limited VM. Constants define max value/key counts, upvalue indexes, and return-count helpers. `create_metatable()` builds Lua tables with `__index`, `__newindex`, `__pairs`, and `__len` closures bound to arbitrary C++ upvalues. `EmptyMetaTable` provides default read-only/non-iterable behavior. Generic helpers include `pushstring()`, `pushvalue()`, `pushtime()`, `StringMapWriteableNewIndex()`, iterator metadata helpers, `next()`, `Pairs()`, and `StringMapMetaTable`.

Control flow: RGW-specific metatable structs implement static closures and pass themselves to `create_metatable()`. For maps, `Pairs()` creates an iterator closure; `create_iterator_metadata()` stores/reuses iterator userdata and prevents overlapping iterations.

State and persistence: templates bind non-owning pointers into Lua closures as lightuserdata. Iterator state is held in Lua userdata/metatables. Map writes mutate the underlying C++ maps directly.

Dependencies/integration: used heavily by request, data, and background Lua code. Includes perf counters, Ceph time, Lua, and `LuaCodeType`.

Risks and test signals: non-owning lightuserdata requires the C++ object to outlive Lua execution. Iterator reuse and invalidation are subtle. Size checks use `strnlen()` with fixed limits. Tests should cover readonly errors, unknown field errors, map deletion during iteration, nested-iteration rejection, nil handling, and write limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_lua_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_lua_version.h -->
## sources/distributed-fs/ceph/src/rgw/rgw_lua_version.h

Purpose: centralizes the Lua major/minor version string used for Lua package paths.

Important API/type: `const std::string CEPH_LUA_VERSION(LUA_VERSION_MAJOR "." LUA_VERSION_MINOR);`.

Control flow: package installation and runtime path setup append this version to `share/lua/<version>` and `lib/lua/<version>` paths.

State and persistence: no runtime state beyond a constant string initialized from Lua headers.

Dependencies/integration: includes `lua.hpp` for `LUA_VERSION_MAJOR`/`LUA_VERSION_MINOR`. Used by `rgw_lua.cc` and `rgw_lua_utils.cc`.

Risks and test signals: compiled Lua version and installed LuaRocks version must match. Tests should verify package path construction when building against different Lua versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_lua_version.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_main.cc -->
## sources/distributed-fs/ceph/src/rgw/rgw_main.cc

Purpose: executable entry point for the `radosgw` daemon.

Important APIs/functions: `usage()` prints daemon options; `C_InitTimeout` fails startup after `rgw_init_timeout`; `godown_alarm()` exits on alarm; `main()` performs global initialization, service setup, signal registration, frontend startup, wait-for-shutdown, and orderly teardown.

Control flow: `main()` redirects stderr to stdout for FCGI compatibility, sets default config values, parses usage, calls `rgw_global_init()` with deferred privilege drop, constructs `rgw::AppMain`, initializes keyring/frontends/NUMA, daemonizes if configured, starts an initialization timer, finishes common init, registers async signal handlers, initializes storage and subsystems, starts frontends, waits for shutdown, then unregisters signal handlers and calls `AppMain::shutdown()`.

State and persistence: persistent service state is owned by `AppMain` and SAL/RADOS subsystems. This file controls process-level signal and timer state.

Dependencies/integration: integrates global Ceph init, Linux keyring secret handling, RGW signals, storage, ops logging, Lua, KMS cache, dedup when compiled, and frontend service startup.

Risks and test signals: startup failure paths must cancel/shutdown the init timer. Stderr redirection affects diagnostics. Signal registration order matters for clean shutdown. Tests are mostly integration/system-level: invalid storage config, daemonize path, init timeout, frontend init failure, and graceful SIGTERM/SIGINT shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_main.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_main.h -->
## sources/distributed-fs/ceph/src/rgw/rgw_main.h

Purpose: declares the RGW daemon application coordinator and pauser aggregation helpers.

Important APIs/types: `RGWPauser` aggregates `RGWRealmReloader::Pauser` instances. `rgw::AppMain` owns frontends, REST dispatcher, Lua/dedup background services, LDAP, scheduler, rate limiter, realm reloader/watcher, period pusher, config store, site config, process environment, and context pool holder. Public initialization methods split RGW startup into storage, frontends, perf counters, HTTP clients, APIs, LDAP, opslog, tracing, Lua, KMS, and dedup phases.

Control flow: `AppMain` is constructed by `main()` or librgw, initialized in phases, then shut down through `shutdown()`. `rest_filter()` allows sync modules to wrap REST managers; `set_logging()` marks REST managers for operation logging.

State and persistence: `AppMain` owns long-lived process services and `RGWProcessEnv`, including the active SAL driver. Static `ops_log_file` is the process-level file log sink.

Dependencies/integration: central integration point for RGW frontends, realm reload, Lua background, RADOS features, config store, scheduling, and rate limits.

Risks and test signals: init/shutdown ordering is critical because many members hold non-owning references into `env.driver` and `CephContext`. Tests should verify pauser propagation, frontend-free librgw modes, realm reload with Lua/dedup paused, and static ops-log file cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_main.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_mdlog_types.h -->
## sources/distributed-fs/ceph/src/rgw/rgw_mdlog_types.h

Purpose: declares metadata log sync policy and log operation status enums.

Important APIs/types: `RGWMDLogSyncType` defines how metadata sync applies remote entries: always, updates, newer-only, or exclusive. `RGWMDLogStatus` defines metadata log operation status values: unknown, write, set attributes, remove, complete, abort.

Control flow: metadata handlers and mdlog processing use these enums to choose mutation semantics and represent log lifecycle.

State and persistence: enum values are serialized indirectly through structures such as `RGWMetadataLogData`; stable numeric values matter for compatibility.

Dependencies/integration: included by RADOS metadata and sync code.

Risks and test signals: adding/reordering enum values can corrupt interpretation of persisted mdlog records. Encoding tests should validate string dump/decode mappings in `rgw_metadata.cc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_mdlog_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_meta_sync_status.h -->
## sources/distributed-fs/ceph/src/rgw/rgw_meta_sync_status.h

Purpose: defines persisted metadata sync progress structures.

Important APIs/types: `rgw_meta_sync_info` records global sync state, shard count, period id, and realm epoch. `rgw_meta_sync_marker` records per-shard full/incremental state, markers, total entries, position, timestamp, and realm epoch. `rgw_meta_sync_status` combines sync info with a map of shard markers.

Control flow: sync code encodes/decodes these records to resume metadata synchronization across restarts and period changes. JSON decode/dump/test-instance declarations support admin/status tools and encoding tests.

State and persistence: all three structs use Ceph encoding with version gates; `period` and `realm_epoch` were added in version 2 for info/marker records. Defaults initialize sync to `StateInit`/`FullSync` with zero counts.

Dependencies/integration: depends on Ceph time, buffer encoding, JSON/Formatter declarations, and metadata sync engine code elsewhere.

Risks and test signals: stale or malformed markers can cause sync replay gaps or duplication. Tests should cover v1 decode compatibility, realm epoch propagation, JSON status round trips, and marker progress across shard boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_meta_sync_status.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_metadata.cc -->
## sources/distributed-fs/ceph/src/rgw/rgw_metadata.cc

Purpose: implements generic RGW metadata object/log serialization helpers and the `RGWMetadataManager` dispatch layer over typed metadata handlers.

Important APIs/functions: `LogStatusDump::dump()` maps mdlog statuses to strings. `RGWMetadataLogData` encodes read/write versions and status. `RGWMetadataTopHandler` lists registered metadata sections. `RGWMetadataManager` registers handlers, parses metadata keys, finds handlers, and exposes `get()`, `put()`, `remove()`, `mutate()`, shard lookup, list-keys iteration, log-entry dumping, and section listing.

Control flow: metadata keys split on the first `:` into type and entry. Empty type dispatches to the top handler for listing sections. `get()` calls handler `get()` then emits a JSON `metadata_info` envelope with key/version/mtime/data. `put()` parses an incoming JSON envelope, builds the typed `RGWMetadataObject` through the handler, then calls handler `put()` with version tracking and sync options. `remove()` reads current version then calls handler removal.

State and persistence: manager state is a map of type string to handler pointer. Persistent metadata lives behind handlers, usually in RADOS/config stores. Log data persists as encoded `RGWMetadataLogData`.

Dependencies/integration: depends on RADOS metadata/mdlog headers, `RGWMetadataHandler`, `RGWObjVersionTracker`, JSON parser/decoder, and cls log entries.

Risks and test signals: manager does not own registered handlers, so lifetime is external. JSON envelope parsing is strict and returns `-EINVAL` on missing data/version. Tests should cover duplicate handler registration, unknown type, section listing, get/put/remove/mutate dispatch, version propagation, malformed JSON, and mdlog dump decode failure tolerance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_metadata.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_multi.cc -->
## sources/distributed-fs/ceph/src/rgw/rgw_multi.cc

Purpose: implements XML parsing support and utility helpers for S3 multipart upload completion.

Important APIs/functions: `RGWMultiPart::xml_end()` extracts `PartNumber` and `ETag`; `RGWMultiCompleteUpload::xml_end()` collects parts into a `std::map<int,std::string>`; `RGWMultiXMLParser::alloc_obj()` maps XML element names to parser objects; `is_v2_upload_id()` recognizes current/legacy v2 upload id prefixes; `RGWUploadPartInfo::dump()` and `generate_test_instances()` support introspection/encoding tests.

Control flow: the XML parser allocates typed nodes while parsing. At each `Part` close, required child nodes are validated and copied. At upload close, all parsed parts are inserted by part number, naturally sorting and overwriting duplicates by map semantics.

State and persistence: parser state is in XML object instances. Upload part info is serializable elsewhere and dumped here for diagnostics.

Dependencies/integration: used by complete-multipart-upload RGW operations; depends on RGW XML parser, object manifest declarations, SAL forward declarations, and multipart upload id constants.

Risks and test signals: `atoi()` silently accepts malformed part-number suffixes. Duplicate part numbers collapse in the map. Tests should include alternate `CompletedMultipartUpload` root compatibility, missing ETag/PartNumber, duplicate parts, invalid numbers, and v2 prefix recognition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_multi.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_multi.h -->
## sources/distributed-fs/ceph/src/rgw/rgw_multi.h

Purpose: declares multipart completion XML object classes and upload id helpers.

Important APIs/types: constants `MULTIPART_UPLOAD_ID_PREFIX_LEGACY` and `MULTIPART_UPLOAD_ID_PREFIX`; `RGWMultiCompleteUpload` with `parts`; `RGWMultiPart` with `etag` and `num`; leaf node classes for `PartNumber` and `ETag`; `RGWMultiXMLParser`; `is_v2_upload_id()`.

Control flow: RGW operations feed request XML through `RGWMultiXMLParser`, then read `RGWMultiCompleteUpload::parts` to complete multipart uploads.

State and persistence: classes are temporary parser state. Persistent upload metadata is handled elsewhere through manifests and multipart metadata objects.

Dependencies/integration: includes XML support, object types, compression types, SAL fwd, and RADOS object manifest header.

Risks and test signals: parser classes accept multiple root names for compatibility. Header includes a RADOS-specific manifest dependency marked FIXME, so layering changes should be tested across non-RADOS builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_multi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_multi_del.cc -->
## sources/distributed-fs/ceph/src/rgw/rgw_multi_del.cc

Purpose: implements XML parsing for S3 multi-object delete requests and a concurrency scheduler for executing delete batches.

Important APIs/functions: `RGWMultiDelObject::xml_end()` extracts key, version id, optional ETag match, last-modified precondition, and size match. `RGWMultiDelDelete::xml_end()` parses quiet mode and collects objects. `RGWMultiDelXMLParser::alloc_obj()` maps XML elements. `rgw::multi_delete::dispatch()` runs per-item delete callbacks with controlled concurrency and versioned-bucket OLH handling.

Control flow: object XML validates required key, URL-decodes and parses last-modified time, and parses size with `strict_strtoll()`. Dispatch uses `ceph::async::spawn_throttle`. For unversioned buckets, all items run concurrently with `skip_update_olh=false`. For versioned buckets, items are grouped by object name; all but the last delete per key run first with `skip_update_olh=true`, then final deletes run with normal OLH update.

State and persistence: XML parser state is request-local. Delete persistence happens through the caller-provided `Exec` callback. Dispatch preserves request/result order through `Item::index`.

Dependencies/integration: depends on XML parser, async spawn throttle, Boost.Asio yield, strict number parsing, URL/time parsing, and RGW object keys.

Risks and test signals: `if_match` stores `c_str()` from an XML data string; lifetime depends on XML object storage and should be scrutinized. Grouping by key must preserve correctness for repeated deletes. Tests should cover quiet mode, invalid preconditions, versioned duplicate-key ordering, max_aio zero normalization, and on-dispatch callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_multi_del.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_multi_del.h -->
## sources/distributed-fs/ceph/src/rgw/rgw_multi_del.h

Purpose: declares multi-object delete XML parser classes and delete dispatch callback types.

Important APIs/types: `RGWMultiDelObject` exposes key, version id, optional ETag, last-modified time, and size match. `RGWMultiDelDelete` stores `objects` and `quiet`. Leaf XML classes represent `Quiet`, `Key`, and `VersionId`. `rgw::multi_delete::Item`, `Exec`, `OnDispatch`, and `dispatch()` define async delete scheduling.

Control flow: RGW delete operations parse XML into `RGWMultiDelDelete`, convert objects to dispatch `Item`s, then call `dispatch()` with an executor that performs actual deletes.

State and persistence: only request-local parsed state. Object deletion and OLH updates are delegated to executor code.

Dependencies/integration: includes Boost.Asio spawn/yield, RGW XML/common types, and `rgw_obj_key`.

Risks and test signals: accessors expose optional/precondition data used by conditional delete logic; tests should assert defaults for absent optional elements and correct values for parsed XML.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_multi_del.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_multiparser.cc -->
## sources/distributed-fs/ceph/src/rgw/rgw_multiparser.cc

Purpose: small standalone parser utility for multipart completion XML.

Important APIs/functions: `main()` initializes `RGWMultiXMLParser`, reads stdin in 1024-byte chunks, feeds chunks to `parser.parse(buf, len, done)`, reports parse failures, and exits.

Control flow: loop continues until EOF; each chunk indicates `done` based on `feof(stdin)`. Read errors exit with `-1`; parser initialization failure exits with `1`.

State and persistence: no persistent state. Parser object owns transient XML parse state.

Dependencies/integration: useful as a developer/test utility around `rgw_multi` XML parsing; depends on stdin and C stdio.

Risks and test signals: parse failures are printed but do not terminate the process immediately. Utility tests can feed valid/invalid multipart XML through stdin to exercise parser behavior outside the daemon.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_multiparser.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_multipart_meta_filter.cc -->
## sources/distributed-fs/ceph/src/rgw/rgw_multipart_meta_filter.cc

Purpose: implements recognition of multipart metadata object names and extracts the base key used for bucket index shard calculation.

Important APIs/functions: `MP_META_SUFFIX` is `.meta`; `MultipartMetaFilter(const std::string& name, std::string& key)` returns true if the name ends with `.meta` and has a preceding dot separator, then sets `key` to the prefix before that separator.

Control flow: checks minimum length, searches for the suffix exactly at the end, finds the previous dot before the suffix, and extracts `name.substr(0, pos)`.

State and persistence: stateless string utility. It affects how multipart metadata entries are interpreted in bucket indexes.

Dependencies/integration: used by bucket index/listing code that needs to treat multipart metadata objects specially.

Risks and test signals: names with dots near the suffix and malformed upload-id forms need coverage. Function only checks suffix/separator, not upload id prefix, so callers must understand its permissive behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_multipart_meta_filter.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_multipart_meta_filter.h -->
## sources/distributed-fs/ceph/src/rgw/rgw_multipart_meta_filter.h

Purpose: documents and declares the multipart metadata object-name filter.

Important APIs/types: external `MP_META_SUFFIX` and `MultipartMetaFilter(name, key)`.

Control flow: caller passes a bucket-index object name; on true, `key` receives the user object key to use for bucket index sharding.

State and persistence: no state. The result influences placement/index behavior for multipart metadata objects.

Dependencies/integration: only includes `<string>`, making it lightweight for bucket-index users.

Risks and test signals: comments describe names adorned with upload id and suffix, but implementation is suffix/separator based. Tests should verify examples with object keys containing dots, no prefix, no suffix, and suffix-only names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_multipart_meta_filter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_notify_event_type.cc -->
## sources/distributed-fs/ceph/src/rgw/rgw_notify_event_type.cc

Purpose: converts RGW/S3 notification event bitmasks to/from S3 event strings.

Important APIs/functions: `to_string()` maps `EventType` values to `s3:*` strings; `to_event_string()` strips the `s3:` prefix; `from_string()` parses known strings; `operator==()` treats event types as equal when bitmasks intersect; `from_string_list()` parses comma-separated lists.

Control flow: conversions are explicit switch/if chains. `from_string()` supports compatibility spellings such as `NonCurrent` and `Noncurrent`, and some lifecycle/replication/restore event aliases. `from_string_list()` tokenizes with `ceph::for_each_substr()` and appends parsed enum values.

State and persistence: stateless. Event values are bitmask constants declared in the header and may be stored/configured elsewhere as strings.

Dependencies/integration: used by bucket notification configuration, event filtering, lifecycle/replication notification paths, and admin/API serialization.

Risks and test signals: `operator==()` is non-standard equality and returns true for category/subtype intersections, which can surprise generic code. `to_string(ObjectExpirationAbortMPU)` returns `AbortMPU` while parser accepts `AbortMultipartUpload`, so round-trip may not be exact. Tests should cover all enum/string mappings, aliases, unknown events, category matching, and comma parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_notify_event_type.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_notify_event_type.h -->
## sources/distributed-fs/ceph/src/rgw/rgw_notify_event_type.h

Purpose: declares notification event bitmask values and conversion helpers.

Important APIs/types: `enum EventType` assigns bit ranges to object-created, object-removed, lifecycle expiration/transition, object sync, replication, restore, and unknown events. `EventTypeList` is a vector of event types. Helpers include `operator==`, `to_string()`, `to_event_string()`, `from_string()`, and `from_string_list()`.

Control flow: event filtering can compare configured categories with concrete events via bit intersection rather than strict equality.

State and persistence: enum numeric bit values are part of configuration/runtime semantics. String conversions provide external API representation.

Dependencies/integration: lightweight `<string>`/`<vector>` header consumed by notification configuration and event dispatch code.

Risks and test signals: values exceed 32 bits, so storage must use a wide enough type. Tests should verify category masks include intended subtypes and no accidental overlap exists between event families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_notify_event_type.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_obj_manifest.cc -->
## sources/distributed-fs/ceph/src/rgw/rgw_obj_manifest.cc

Purpose: implements object manifest iteration and implicit object-location calculation for RGW head, shadow, and multipart tail objects.

Important APIs/functions: `RGWObjManifest::obj_iterator::operator++()` advances to the next object extent; `seek()` positions by logical offset; `update_explicit_pos()` handles explicit object maps; `update_location()` resolves the current `rgw_obj_select`; `get_implicit_location()` derives physical object names/namespaces for implicit layouts.

Control flow: explicit manifests iterate over `manifest->objs`. Implicit manifests treat offsets below head size as the head object, then use manifest rules to compute part id, stripe id, stripe offset/size, rule transitions, override prefixes, and tail placement. Multipart part/stripe naming uses `.<part>` in multipart namespace for first stripes and `.<part>_<stripe>` in shadow namespace for later stripes.

State and persistence: manifests store layout rules, object size, head/tail placement, prefix, tail instance, and explicit object maps elsewhere; this file mutates iterator state only. Location calculation determines where object data is read/written in RADOS.

Dependencies/integration: depends on RADOS `RGWObjManifest` declaration and bucket namespace constants `RGW_OBJ_NS_SHADOW`/`RGW_OBJ_NS_MULTIPART`.

Risks and test signals: off-by-one errors in stripe/part transitions can corrupt reads or writes. Tests should cover seeking into head/tail, zero-sized objects, explicit manifests, rule boundary offsets, multipart part transitions, override prefixes, tail placement bucket override, and max head size behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_obj_manifest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_obj_types.h -->
## sources/distributed-fs/ceph/src/rgw/rgw_obj_types.h

Purpose: defines fundamental serialized RGW object key and object-location types shared by RGW and lower layers.

Important APIs/types: `rgw_obj_index_key` stores bucket-index key name/instance and comparison/encoding helpers. `rgw_obj_key` stores user-facing name, version instance, and namespace; it parses/serializes raw object ids and index keys, handles namespace escaping, null-instance behavior, and object locator compatibility. `rgw_raw_obj` stores pool, oid, locator, and legacy decode from old `rgw_obj` encodings. `rgw_obj` combines bucket and key plus in-memory flags/index hash source and explicit data-pool selection.

Control flow: object names are mangled into RADOS oids with leading underscore namespace syntax and optional `:<instance>` in namespace. Index keys use similar escaping but keep instance separately. Decode paths include legacy compatibility branches for old object encodings.

State and persistence: these types are persisted widely in bucket indexes, manifests, metadata, and logs. `in_extra_data` and `index_hash_source` are in-memory behavior controls; encoded `rgw_obj` version is 6.

Dependencies/integration: intentionally avoids heavy RGW/SAL dependencies; includes pool, bucket, user types, Formatter, and encoding.

Risks and test signals: empty strings are often indexed at `name[0]`, so callers must ensure non-empty names before certain helpers. Namespace parsing, underscore escaping, and legacy decode are high-risk compatibility areas. `generate_test_instances()` and JSON decode/dump declarations support encoding tests; add cases for underscores, namespaces, instances, null instance, malformed raw oid, and legacy versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_obj_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_object_expirer.cc -->
## sources/distributed-fs/ceph/src/rgw/rgw_object_expirer.cc

Purpose: standalone daemon entry point for RGW object expiration processing.

Important APIs/functions: `StoreDestructor` closes the SAL driver on exit. `usage()` delegates generic server usage. `main()` initializes Ceph, config store, site config, storage driver, constructs `RGWObjectExpirer`, starts its processor, and sleeps forever on `rgw_objexp_gc_interval`.

Control flow: parses args/usage, calls `global_init()`, daemonizes if configured, initializes an `io_context_pool`, creates a config store using `rgw_config_store`, loads `SiteConfig`, opens storage with most optional services disabled and object expiration enabled, then runs the expirer background processor.

State and persistence: expiration state and object deletions are handled by `RGWObjectExpirer` and the SAL driver. This file owns process-lifetime driver and context pool.

Dependencies/integration: depends on Ceph global init/config, SAL DriverManager/config store, site config, RGW object expirer core, and RGW object/log/usage support.

Risks and test signals: the infinite sleep loop means shutdown relies on process signals outside this file. Startup has several `exit(1)` paths. Tests should cover missing config store, site load failure, storage init failure, daemonized startup, and that driver close happens through `StoreDestructor` on early returns after storage creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_object_expirer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_object_lock.cc -->
## sources/distributed-fs/ceph/src/rgw/rgw_object_lock.cc

Purpose: implements JSON/XML parsing and formatting for S3 Object Lock configuration, object retention, and legal hold.

Important APIs/functions: `DefaultRetention::decode_json()/decode_xml()/dump()/dump_xml()` handles retention mode and days/years. `ObjectLockRule` wraps default retention. `RGWObjectLock` parses bucket-level lock configuration, dumps it, computes lock-until date from object mtime, and generates test instances. `RGWObjectRetention` parses/dumps per-object retention. `RGWObjectLegalHold` parses/dumps status and reports enabled state.

Control flow: XML parsing enforces valid modes (`GOVERNANCE`/`COMPLIANCE`), exactly one of Days/Years, `ObjectLockEnabled == Enabled`, ISO-8601 retain-until dates, and legal hold status `ON`/`OFF`. Lock-until calculation adds days or years to mtime when a rule exists.

State and persistence: object lock structures are encoded in bucket/object attrs elsewhere. Retention dates use `ceph::real_time`, with round-trip encode support in the header.

Dependencies/integration: uses RGW XML/JSON decoders, Ceph ISO-8601 time helpers, and Formatter encoders.

Risks and test signals: date arithmetic uses `std::chrono::days/years`; leap-year/year semantics should be validated. XML validation is stricter than JSON decode for default retention. Tests should cover invalid modes, both/neither Days/Years, disabled/missing lock values, retain date parse failure, legal hold status, dump round trips, and lock-until date calculations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_object_lock.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_object_lock.h -->
## sources/distributed-fs/ceph/src/rgw/rgw_object_lock.h

Purpose: declares serialized types for S3 Object Lock bucket configuration, default retention, object retention, and legal hold.

Important APIs/types: `DefaultRetention` stores mode/days/years; `ObjectLockRule` wraps it; `RGWObjectLock` stores enabled/rule state and exposes `retention_period_valid()`, `has_rule()`, getters, XML/JSON methods, and `get_lock_until_date()`. `RGWObjectRetention` stores mode and retain-until date. `RGWObjectLegalHold` stores status and `is_enabled()`.

Control flow: RGW APIs decode request XML/JSON into these types, validate retention fields, encode them to attrs, and dump them back to clients/admin tools.

State and persistence: all classes have `WRITE_CLASS_ENCODER`; `RGWObjectRetention` encode version 2 writes both normal and round-trip time encoding for precision compatibility.

Dependencies/integration: depends on Ceph encoding/time/ISO-8601 and RGW XML support.

Risks and test signals: `RGWObjectLock` defaults `enabled=true` with no rule, which callers must interpret carefully. Tests should cover binary encoding compatibility, retention period validity, and default construction semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_object_lock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_object_ownership.cc -->
## sources/distributed-fs/ceph/src/rgw/rgw_object_ownership.cc

Purpose: implements S3 Object Ownership parsing, serialization, XML output, and attr lookup.

Important APIs/functions: `to_string()` formats `ObjectOwnership`; `parse()` accepts `BucketOwnerEnforced`, `BucketOwnerPreferred`, and `ObjectWriter`; `OwnershipControls::decode_xml()` validates `Rule/ObjectOwnership`; `dump_xml()` emits the XML rule; `encode()`/`decode()` persist controls; `get_object_ownership()` reads `RGW_ATTR_OWNERSHIP_CONTROLS` from attrs and defaults to `ObjectWriter`.

Control flow: XML decode requires a `Rule` element and nested `ObjectOwnership`. Attr lookup decodes the binary ownership controls and falls back to backward-compatible `ObjectWriter` on absent or malformed attrs.

State and persistence: persisted as `OwnershipControls` in bucket attrs under `RGW_ATTR_OWNERSHIP_CONTROLS`.

Dependencies/integration: depends on RGW XML/common attr names and SAL attr map. Used by S3 bucket ownership controls APIs and request authorization/object ownership decisions.

Risks and test signals: fallback on decode error masks corrupted attrs but preserves availability. Tests should cover all valid values, invalid error message, missing XML elements, attr absence, malformed bufferlist fallback, and XML dump shape.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_object_ownership.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_object_ownership.h -->
## sources/distributed-fs/ceph/src/rgw/rgw_object_ownership.h

Purpose: declares S3 Object Ownership configuration types and helpers.

Important APIs/types: `enum class ObjectOwnership` contains `BucketOwnerEnforced`, `BucketOwnerPreferred`, and `ObjectWriter`. `OwnershipControls` stores `object_ownership` and supports XML decode/dump. Free functions handle string conversion, parsing, binary encode/decode, and attr lookup.

Control flow: API handlers parse XML into `OwnershipControls`, persist encoded attrs, and later retrieve ownership mode through `get_object_ownership()`.

State and persistence: default ownership is `ObjectWriter`; encoded controls are stored in RGW bucket attrs.

Dependencies/integration: forward declares XML/Formatter and SAL attrs, and includes Ceph encoding.

Risks and test signals: enum class is encoded directly; compatibility depends on stable enum ordering. Tests should include binary round trips and default behavior when attrs are missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_object_ownership.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_oidc_provider.cc -->
## sources/distributed-fs/ceph/src/rgw/rgw_oidc_provider.cc

Purpose: implements JSON dump/decode and test fixtures for OIDC provider metadata.

Important APIs/functions: `RGWOIDCProviderInfo::dump()` writes id, provider URL, ARN, creation date, tenant, client ids, and thumbprints. `decode_json()` reads the same fields. `generate_test_instances()` returns a populated provider plus a default provider for encoding tests.

Control flow: admin/API code can decode JSON into provider info, persist it through class encoding, and dump it back for responses.

State and persistence: provider info is a serializable value object; persistence is handled by metadata/config code elsewhere.

Dependencies/integration: depends on Ceph JSON/Formatter support and the header's encoder.

Risks and test signals: creation date is a plain string, so validation is external. Tests should cover JSON round trips, empty client/thumbprint vectors, tenant/account id behavior, and binary encode compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_oidc_provider.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_oidc_provider.h -->
## sources/distributed-fs/ceph/src/rgw/rgw_oidc_provider.h

Purpose: declares the serialized OIDC provider metadata model used by RGW IAM/OIDC features.

Important APIs/types: `RGWOIDCProviderInfo` stores `id`, `provider_url`, `arn`, `creation_date`, `tenant`, `client_ids`, and `thumbprints`, with encode/decode version 3, JSON dump/decode, and test-instance generation.

Control flow: provider management APIs populate this struct, encode it for storage, and dump/decode JSON for admin/API exchange.

State and persistence: all fields are persisted in Ceph encoding. `tenant` may be tenant name or account id.

Dependencies/integration: includes `common/ceph_json.h` and uses `WRITE_CLASS_ENCODER`.

Risks and test signals: schema evolution requires encode version changes. Tests should verify decoding older records if versions change and that vector fields retain order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_oidc_provider.h -->

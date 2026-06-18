# subset-b-008151 research

Grouped research for DAOS pool server files. Each section preserves the original source path and is intended to be split into the mapped source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/pool/srv.c -->
# sources/object-store/daos/src/pool/srv.c

## Purpose

This file is the DAOS pool server module registration unit. It wires the pool subsystem into the DAOS server module framework, initializes and tears down global pool-server facilities, registers RPC handlers for supported pool protocol versions, creates per-xstream pool TLS, and attaches module metrics. It is not where most pool operations are implemented; instead it orchestrates `srv_pool.c`, `srv_target.c`, `srv_iv.c`, `srv_layout.c`, and `srv_metrics.c` through declarations in `srv_internal.h`.

## Important APIs, types, and functions

- Globals:
  - `ec_agg_disabled`: set from `DAOS_EC_AGG_DISABLE` and used outside this file to disable EC aggregation.
  - `pw_rf`: pool-wide redundancy factor, read from `DAOS_POOL_RF`, defaulting to `2`, clamped to the supported range `0..4`.
  - `ps_cache_intvl`: pool space cache expiration interval, read from `DAOS_POOL_SPACE_CACHE_INTVL` and capped at `20` seconds.
- `check_pool_redundancy_factor()`: parses and validates the redundancy factor environment variable.
- `init()`: module init path. It initializes the pool cache, pool handle hash, pool IV classes, default pool properties, environment-derived knobs, replicated service class registration, and NVMe reaction ops.
- `fini()`: inverse of `init()`, unregistering replicated service class and freeing global facilities.
- `setup()`: configures `dc_pool_proto_version` for server-side client RPCs and starts all pools when not in check mode and `DAOS_START_POOLS` permits it.
- `cleanup()`: stops all pools at module shutdown.
- `pool_tls_init()` / `pool_tls_fini()`: allocate and free `struct pool_tls`, primarily the xstream-local list of `ds_pool_child` objects.
- `pool_handlers_v6` / `pool_handlers_v7`: RPC handler arrays populated from `POOL_PROTO_CLI_RPC_LIST()` and `POOL_PROTO_SRV_RPC_LIST()`.
- `pool_module_key`, `pool_metrics`, `pool_module`: public module descriptors consumed by the DAOS server framework.

## Control flow

Startup proceeds through `pool_module.sm_init` then `pool_module.sm_setup`. `init()` is ordered defensively: cache init, handle hash init, IV class registration, default property initialization, environment processing, replicated service registration, and BIO reaction registration. Each intermediate failure jumps to a label that undoes only already-initialized subsystems. `setup()` computes the pool RPC protocol version from the engine join version. If the engine is not in check mode, it optionally starts all pool services immediately. Shutdown calls `cleanup()` for live pools and `fini()` for global state.

RPC dispatch is table-driven. The `X` macro converts protocol-list entries from `rpc.h` into `struct daos_rpc_handler` elements, including collective RPC aggregator hooks for target disconnect and query.

## State and persistence behavior

This file owns process/module state, not durable pool metadata. Persistent storage is delegated to `srv_layout.c`/`srv_pool.c`; distributed cache state is delegated to `srv_iv.c`. The persistent side effect of `setup()` is indirect: `ds_pool_start_all()` loads and starts services from RDB-backed pool state. TLS state is transient per xstream and expected to be empty by finalization.

## Dependencies and integration points

It depends on DAOS server module APIs (`dss_module`, TLS keys, join-version helpers), CART RPC protocol registration, BIO reaction hooks, metrics registration, environment parsing, and the pool internal APIs declared in `srv_internal.h`. It integrates with `srv_iv.c` through `ds_pool_iv_init/fini`, with `srv_layout.c` through `ds_pool_prop_default_init/fini`, with target/pool service code through cache/hash/start/stop calls, and with `srv_metrics.c` through `pool_metrics`.

## Risks and edge cases

- Initialization order matters. Moving default property initialization earlier or later can leak ACL memory or leave registered IV classes on failure.
- `pw_rf` uses `(uint32_t)-1` as a sentinel. Any refactor must preserve the sentinel logic around `d_getenv_uint32_t()`.
- TLS finalization only asserts an uncleared child cache when `DAOS_STRICT_SHUTDOWN` is enabled; otherwise it logs. Leaked pool-child references may therefore be non-fatal in production but still indicate shutdown-order bugs.
- `setup()` skips pool start during check mode. Code that assumes pools are started immediately must honor `engine_in_check()`.
- Metrics are registered for `DAOS_SYS_TAG`; the allocator asserts `tgt_id < 0`, so per-target metric use would be invalid.

## Test signals

Useful coverage includes module init failure injection at each step, environment parsing for `DAOS_POOL_RF` and `DAOS_POOL_SPACE_CACHE_INTVL`, startup with `DAOS_START_POOLS=false`, check-mode startup, strict shutdown with intentionally leaked child references, and RPC handler table/protocol-version compatibility tests for pool protocol v6 and v7.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/pool/srv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/pool/srv_cli.c -->
# sources/object-store/daos/src/pool/srv_cli.c

## Purpose

This file provides server-side wrappers for calling DAOS client pool APIs and pool service RPCs from within the engine. It lets management, rebuild, scrub, and other server subsystems perform pool operations without holding a normal client pool handle. The core pattern is a generic replicated-service call loop (`dsc_pool_svc_call`) plus small operation-specific init/consume/fini callbacks.

## Important APIs, types, and functions

- `dsc_pool_open()` / `dsc_pool_close()`: create and release a server-side `dc_pool` object around an existing pool UUID, pool-handle UUID, pool map, and service rank list.
- `dsc_pool_tgt_exclude()` and `dsc_pool_tgt_reint()`: task-based wrappers around client exclude/reintegrate APIs.
- `struct dsc_pool_svc_call_cbs`: callback table for pool-service RPC wrappers. It names the `enum pool_operation` and optional request init, reply consume, and cleanup callbacks.
- `dsc_pool_svc_call()`: common retry loop that creates a pool-service RPC, chooses an RSVC replica, honors leader hints, caps RPC timeout to a deadline, invokes callbacks, and handles backoff or immediate retry.
- Query wrappers:
  - `dsc_pool_svc_query()` with `pool_query_init/consume/fini`.
  - `dsc_pool_svc_query_target()` with target state and media space extraction.
  - `process_query_result()` translates a pool query reply and pool map into `daos_pool_info_t` plus optional enabled, disabled, and SWIM-dead rank lists.
  - `pool_map_get_dead_ranks()` asks CART/SWIM for live membership state.
- Administrative wrappers:
  - `dsc_pool_svc_check_evict()`
  - `dsc_pool_svc_get_prop()` / `dsc_pool_svc_set_prop()`
  - `dsc_pool_svc_extend()`
  - `dsc_pool_svc_update_target_state()` for exclude, reintegrate, and drain
  - `dsc_pool_svc_update_acl()` / `dsc_pool_svc_delete_acl()`
  - `dsc_pool_svc_upgrade()`
  - `dsc_pool_svc_rebuild_stop()` / `dsc_pool_svc_rebuild_start()`
  - `dsc_pool_svc_eval_self_heal()`

## Control flow

`dsc_pool_svc_call()` initializes an `rsvc_client` with the pool service ranks, initializes a backoff sequence with one zero-delay retry, then loops until success, callback termination, or deadline expiration. For each attempt it chooses a replica, creates a request with `ds_pool_req_create()`, invokes the operation init callback, adjusts the CRT timeout so it cannot exceed the caller's absolute millisecond deadline, sends the RPC through `dss_rpc_send()`, and passes completion status plus service leader hints to `rsvc_client_complete_rpc()`. If the RPC reached a valid pool-service reply and the result is not a DAOS retryable error, the consume callback decides whether the call is done, should retry after backoff, or should retry immediately. Fini callbacks release per-attempt resources such as map bulk handles.

Query is the most involved wrapper. The init callback creates a bulk buffer sized by `pqa_map_size`; the consume callback retries immediately on `-DER_TRUNC` using the service-returned map size; successful replies are converted into local pool-map state, rank lists, rebuild status, pool space, layout versions, and optional memory-file byte counts.

## State and persistence behavior

The file does not directly persist RDB data. It sends RPCs that cause the pool service to mutate persistent state, including target state changes, property updates, ACL edits, upgrade state, rebuild control, and handle eviction. Locally it creates transient `dc_pool` handles, task objects, rank lists, bulk map buffers, and sanitized ACL-principal buffers. `dsc_pool_open()` attaches to the management system, initializes an RSVC client, and updates the local client pool map from a server-supplied `pool_map`.

## Dependencies and integration points

It depends on the DAOS client pool stack (`dc_pool_*`, task APIs, scheduler), management system attach (`dc_mgmt_sys_attach`), replicated-service client selection (`rsvc_client_*`), pool RPC helpers from `rpc.h`, CART RPC send/timeout APIs, pool-map conversion helpers, SWIM state through CART group rank state, and engine module context through `dss_get_module_info()`. It is used by server code that needs control-plane pool operations, including management and rebuild paths.

## Risks and edge cases

- Deadline handling is strict. If less than one second remains after timeout capping, the call sleeps until the deadline and returns `-DER_TIMEDOUT`; callers need realistic deadlines.
- `dsc_pool_svc_call()` assumes reply layout has `struct pool_op_out` semantics for the common operation header.
- Query map bulk size starts small and relies on `-DER_TRUNC` retry. Incorrect map-size reporting from service side would cause repeated failures or oversized allocation.
- `process_query_result()` requires non-null output pointers when the corresponding `pi_bits` are requested. Callers must keep requested bits consistent with provided pointers.
- Dead-rank detection mixes pool map UPIN status with CART/SWIM status. It reports ranks dead by SWIM but not yet excluded, which is distinct from disabled ranks.
- `dsc_pool_svc_set_prop()` blocks mutation of properties that are create-time or internally managed: performance domain, EC/RP performance-domain affinity, global version, upgrade status, service-op settings, service redundancy factor, and object version.
- `dsc_pool_svc_delete_acl()` allocates and sanitizes a principal string, but NULL principal names are allowed through to the request for principal-type-only deletes.
- The task wrappers `dsc_pool_tgt_exclude()` and `dsc_pool_tgt_reint()` both use `DAOS_API_ARG_ASSERT(*args, POOL_EXCLUDE)`; this is likely intentional macro reuse but is worth checking if API argument assertions become operation-specific.

## Test signals

Strong tests would simulate RSVC not-leader hints, retryable errors, immediate retry on `-DER_TRUNC`, timeout capping, consume callback errors, invalid target state returning `-DER_INVAL`, immutable-property rejection in `dsc_pool_svc_set_prop()`, query requests with missing rank-list output pointers, SWIM dead-rank detection, ACL principal truncation/null termination, and cleanup of bulk handles across both success and retry paths.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/pool/srv_cli.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/pool/srv_internal.h -->
# sources/object-store/daos/src/pool/srv_internal.h

## Purpose

This header is the internal contract for the DAOS pool server implementation. It centralizes process-wide pool configuration, pool module TLS access, metrics layout, IV serialized value types, helper inline functions, and cross-file function declarations for pool service, target, utility, IV, and metrics code.

## Important APIs, types, and functions

- Extern globals: `pw_rf` and `ps_cache_intvl`, configured in `srv.c`.
- `struct pool_metrics`: telemetry node pointers for pool operation counters and service gauges.
- `struct pool_tls` plus `pool_tls_get()`: per-xstream pool child cache access.
- `ds_pool_skip_for_check()`: returns true in engine check mode until a pool has been CR-checked.
- IV wire/cache structures:
  - `struct pool_iv_map`: master rank, pool map version, and embedded `pool_buf`.
  - `struct pool_iv_prop`: flattened full pool property set with fixed strings, scalar properties, offsets into `pip_iv_buf`, ACL, and service-rank list.
  - `struct pool_iv_conn` and `struct pool_iv_conns`: variable-length handle connection records with credentials.
  - `struct pool_iv_key`: IV private key data with UUID, expected entry size, HLC epoch, and leader term.
  - `struct pool_iv_hdl`: server pool and container handles.
  - `struct pool_iv_entry`: union of all pool IV value types.
- Inline sizing helpers:
  - `pool_iv_conn_size()`
  - `pool_iv_conn_next()`
  - `pool_iv_conn_ent_size()`
- `struct pool_map_refresh_ult_arg`: arguments for asynchronous pool-map refresh ULTs.
- Declarations for major implementation files: service lifecycle and handlers from `srv_pool.c`, target cache and RPC handling from `srv_target.c`, utility functions from `srv_util.c`, IV APIs from `srv_iv.c`, and metrics APIs from `srv_metrics.c`.

## Control flow

The header itself has no runtime control flow beyond inlines. Its declarations define the direction of the pool subsystem: `srv.c` invokes global lifecycle functions; RPC handler tables point at handler declarations here; `srv_pool.c` updates persistent metadata and broadcasts IV changes; `srv_target.c` consumes IV updates to mutate target-local state; and `srv_iv.c` serializes, distributes, fetches, refreshes, and invalidates the IV value types declared here.

## State and persistence behavior

The declared IV structures are transient distributed cache payloads, not direct RDB records, but several mirror persistent pool properties stored through keys declared in `srv_layout.h`. `pool_iv_prop` carries the full property set needed by non-leader ranks, including ACL and service list data in an internal flexible buffer. `pool_iv_conn` carries security credentials and layout versions for connected handles, allowing target ranks to rebuild connection state after service-side operations. `pool_tls` contains per-xstream in-memory pool-child references.

## Dependencies and integration points

The header depends on GURT list primitives, DAOS pool-map types, DAOS engine/server declarations, security structures, and telemetry common types. It is included by the pool module registration, IV implementation, metrics implementation, and service/target files. The IV structures must remain binary-compatible with the serialization/deserialization logic in `srv_iv.c` and the producers/consumers in `srv_pool.c`/`srv_target.c`.

## Risks and edge cases

- `pool_iv_prop` has fixed buffers and offset-based flexible storage. New properties must be added to the serializer, deserializer, default property table, and size calculation in lockstep.
- `pool_iv_conn_next()` trusts `pic_cred_size`. All iteration must validate bounds with `pool_iv_conn_valid()` as done in `srv_iv.c`.
- `pool_iv_conn_ent_size()` includes `struct pool_iv_entry`, while `pool_iv_conn_size()` does not. Mixing them causes under- or over-allocation.
- `ds_pool_skip_for_check()` assumes `pool` is valid and check-mode semantics are respected by callers.
- The prototypes intentionally expose many internal handlers; signature drift between macro-generated RPC handlers and declarations can break module registration at compile time.

## Test signals

Compile-time coverage is important: protocol handler signatures, IV class APIs, and metrics signatures should fail fast on mismatch. Runtime tests should exercise IV connection iteration with variable credential sizes, property serialization after adding any DAOS pool property, check-mode skip behavior, TLS retrieval on initialized module keys, and mixed-version pool-handle formats declared in `srv_layout.h`.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/pool/srv_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/pool/srv_iv.c -->
# sources/object-store/daos/src/pool/srv_iv.c

## Purpose

This file implements the pool IV cache classes. It serializes and distributes pool maps, pool properties, server handles, and connected pool handles across ranks; refreshes target-local state when IV entries change; invalidates stale entries; and registers the pool IV classes with the generic DAOS IV layer. It is a key consistency bridge between the pool service leader and target ranks.

## Important APIs, types, and functions

- Size and allocation:
  - `pool_iv_map_ent_size()`: computes map IV value size for a given `pool_buf` rank count.
  - `pool_iv_prop_ent_size()`: computes property IV size including rounded ACL and service-list buffers.
  - `pool_iv_value_alloc_internal()`: allocates IV entry buffers and initializes connection-buffer bookkeeping.
- Property conversion:
  - `pool_iv_prop_l2g()`: converts local `daos_prop_t` entries into flattened `struct pool_iv_prop`.
  - `pool_iv_prop_g2l()`: rebuilds a `daos_prop_t` from flattened IV state, including ACL validation/duplication and service-list duplication.
- Connection handle helpers:
  - `pool_iv_conn_lookup()`, `pool_iv_conn_delete()`, `pool_iv_conn_insert()`, `pool_iv_conns_buf_insert()`.
  - Fetch/update merge helpers use `pic_size == (uint32_t)-1` as a retry sentinel when a fetch buffer is too small.
- IV callbacks:
  - `pool_iv_ent_init/get/put/destroy/fetch/update/invalid/refresh/value_alloc/pre_sync`.
  - `pool_iv_ops`: callback table registered for all pool IV classes.
- Public update/fetch APIs:
  - `ds_pool_iv_map_update()`
  - `ds_pool_iv_conn_hdls_update()`
  - `ds_pool_iv_conn_hdl_update()`
  - `ds_pool_iv_conn_hdl_fetch()`
  - `ds_pool_iv_conn_hdl_invalidate()`
  - `ds_pool_map_refresh_ult()`
  - `ds_pool_iv_srv_hdl_update/fetch/invalidate()`
  - `ds_pool_iv_prop_update/fetch()`
  - `ds_pool_iv_svc_fetch()`
  - `ds_pool_iv_init/fini()`

## Control flow

Each IV operation is keyed by `struct pool_iv_key`, which carries class ID, expected value size, an HLC epoch, a UUID selector for handle invalidation, and the master term. Updates go through `pool_iv_update()`, which creates a one-iov scatter/gather list and calls `ds_iv_update()` with the selected sync mode.

For map distribution, the service builds a `pool_iv_entry` with master rank, map version, and optional `pool_buf`, then performs an eager synchronous IV update. Fetch begins with a small expected map size and retries if the aggregated result marks `pb_target_nr == (uint32_t)-1` and reports the required `pb_nr`.

For properties, `ds_pool_iv_prop_update()` serializes a full `daos_prop_t` into a flattened payload and sends a lazy retryable update. Fetch allocates space for the maximum ACL length and a temporary service-list bound, fetches the IV entry, reconstructs a `daos_prop_t`, and copies it into the caller-provided property.

For connection handles, single-handle and bulk updates serialize one or more `pool_iv_conn` records. Aggregation inserts unique handles into a variable-length buffer; if the destination is too small it records a sentinel and required size, causing `ds_pool_iv_conn_hdl_fetch()` to allocate a bigger buffer and retry. Invalidating a handle uses the handle UUID in the private IV key and deletes it from the cached connection set.

Callbacks enforce leader and epoch semantics. `pool_iv_ent_fetch()` rejects fetch on a not-yet-valid master as `-DER_NOTLEADER`. `pool_iv_ent_update()` only applies authoritative changes on the IV master rank, forwarding otherwise. Both update and refresh paths ignore stale nonzero epochs. Refresh applies side effects such as `ds_pool_tgt_map_update()`, `ds_pool_tgt_prop_update()`, `ds_pool_tgt_connect()`, and `ds_pool_iv_refresh_hdl()` before updating the local IV cache, unless the pool is stopping.

## State and persistence behavior

IV state is cached distributed memory, not durable storage, but it mirrors persistent pool state and connected-handle state from the pool service. It updates target-local pool maps, properties, server handles, and client handle connections. `pool_iv_pre_sync()` updates a local pool's IV namespace master rank/term and target map before a map sync is forwarded, then signals `sp_fetch_hdls_cond`, connecting IV map changes with handle-fetch synchronization.

No RDB writes occur directly in this file. Durable state changes originate in pool service code and are propagated here through IV updates. The file does mutate in-memory fields such as `sp_srv_cont_hdl`, `sp_srv_pool_hdl`, `sp_map`, `sp_map_version`, and target connection state through helper calls.

## Dependencies and integration points

It depends on `daos_srv/iv.h`, pool-map sizing and creation helpers, DAOS property and ACL APIs, security credential buffers, HLC timestamps, Argobots mutex/condition/eventual primitives, and pool service/target functions declared in `srv_internal.h`. Producers in `srv_pool.c` call the update APIs after loading service state, modifying pool properties, changing maps, and accepting connections. Consumers in target code receive side effects through `ds_pool_tgt_map_update()`, `ds_pool_tgt_prop_update()`, and `ds_pool_tgt_connect()`. Container code can fetch the pool service rank list through `ds_pool_iv_svc_fetch()`.

## Risks and edge cases

- `PROP_SVC_LIST_MAX_TMP` is fixed at 16, and `pool_iv_prop_l2g()` asserts the service list is smaller. Pools with larger service lists would hit assertions unless this path is updated.
- Property serialization must stay synchronized with `DAOS_PROP_PO_NUM`, the default property table, and the pool property set/get service code.
- The `-1` sentinel size protocol is subtle. A sentinel may be cached temporarily; update/refresh logic has explicit branches to avoid applying it on the master or to resize on followers.
- Epoch handling ignores updates with older or equal nonzero HLC epochs. Incorrect epoch initialization could drop a legitimate update.
- Several update paths call side-effect functions that may yield; the code rechecks `sp_stopping` before copying into the IV cache. Future side effects need the same shutdown awareness.
- `pool_iv_ent_update()` declares `struct ds_pool *pool;` without initializing it before the `out_put` label, but the current paths set it via lookup before reaching the final `if (pool != NULL)`. Any new early jump before assignment would be risky.
- `pool_iv_prop_g2l()` assumes an ACL pointer can be derived and then inspects `acl->dal_len`; malformed or undersized IV buffers would be dangerous if validation bounds were weakened.

## Test signals

High-value tests include map fetch retry on undersized buffers, connection-handle aggregation resize/retry, duplicate handle insertion, handle invalidation by UUID, stale epoch suppression, non-leader forwarding, master stepping-up `-DER_NOTLEADER`, service handle update/fetch/invalidate, property round-trips including ACL and service list, pool stopping during refresh side effects, and IV class register/unregister failure cleanup.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/pool/srv_iv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/pool/srv_layout.c -->
# sources/object-store/daos/src/pool/srv_layout.c

## Purpose

This file defines the RDB key objects and default pool property values for the DAOS pool server persistent metadata layout. It is the implementation companion to `srv_layout.h`: the header declares the keys and default property object, while this file instantiates them and initializes dynamically allocated defaults.

## Important APIs, types, and functions

- `RDB_STRING_KEY(ds_pool_prop_, ...)` and `RDB_STRING_KEY(ds_pool_attr_, user)`: instantiate `d_iov_t` keys for root pool properties, pool-handle KVS, user attribute KVS, service operation KVS, server handles, recovery container marker, and all scalar pool properties.
- `pool_prop_entries_default[DAOS_PROP_PO_NUM]`: default value table for optional pool properties. It covers label, space rebuild threshold, self-heal policy, reclaim mode, ACL, owner, owner group, service list, EC/RP layout knobs, data threshold, global/upgrade/object versions, performance domain, scrub, checkpoint, reintegration mode, and service-op settings.
- `pool_prop_default`: `daos_prop_t` view over the default entries table.
- `ds_pool_prop_default_init()`: fills the default ACL entry by calling `ds_sec_alloc_default_daos_pool_acl()`.
- `ds_pool_prop_default_fini()`: frees the dynamically allocated default ACL.

## Control flow

There is little runtime control flow. The RDB key symbols are created at load time via macros. During pool module initialization, `srv.c` calls `ds_pool_prop_default_init()`, which looks up the ACL property entry and allocates the default DAOS pool ACL. During module finalization, `ds_pool_prop_default_fini()` looks up the same entry and frees its pointer.

## State and persistence behavior

The `d_iov_t` key symbols define names used by service code to create, read, update, and destroy RDB records. The file itself does not perform RDB transactions. The default property table is process-global mutable state only for entries that hold allocated pointers, currently the ACL and service list pointer default. The persistent layout includes root pool properties, pool handles, user attributes, and a service-ops KVS shared conceptually with container metadata.

## Dependencies and integration points

It depends on `daos_srv/rdb.h` for key macros, `daos_srv/security.h` for default ACL allocation, and DAOS pool property constants. `srv_pool.c` consumes these key symbols for pool create/load/update/query/upgrade paths. `srv_iv.c` mirrors many of the default property types in `struct pool_iv_prop`. `srv_layout.h` documents the persistent key set and warns about root KVS key-name overlap with container layout.

## Risks and edge cases

- `pool_prop_entries_default` must remain exactly aligned with `DAOS_PROP_PO_NUM` and property type ordering expectations in code that iterates all pool properties.
- Adding a new property requires updates in several files: this default table, `srv_layout.h` declarations, RDB create/load/update paths, IV serialization/deserialization, query/set validation, and tests.
- Default ACL allocation failure aborts pool module initialization with `-DER_NOMEM`.
- `ds_pool_prop_default_fini()` frees `dpe_val_ptr` but does not null it. Current lifecycle is one init/fini pair; repeated init/fini cycles would need care.
- Root KVS key names must not conflict with container root KVS keys because pool and container modules share layout concepts.

## Test signals

Tests should verify default property initialization/finalization under allocation failure, that each optional pool property has exactly one default entry, that RDB key symbols match expected string names, that pool create persists defaults correctly, and that adding a new `DAOS_PROP_PO_*` fails tests unless default, layout, IV, and service paths are updated together.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/pool/srv_layout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/pool/srv_layout.h -->
# sources/object-store/daos/src/pool/srv_layout.h

## Purpose

This header documents and declares the DAOS pool server persistent metadata layout. It names every RDB key used for root pool properties, pool-handle storage, pool user attributes, and service operation tracking, and it defines the serialized pool-handle value formats.

## Important APIs, types, and functions

- Root property key declarations:
  - pool map version and buffer
  - label, ACL, owner, owner group
  - rebuild/self-heal/reclaim/scrub/checkpoint/reintegration policies
  - connectable state and handle count
  - EC/RP layout properties, data threshold, performance domain, service redundancy factor, global/object/upgrade versions
  - service ops KVS and service-op counters/config
  - server pool/container handles and recovery container flag
- KVS declarations:
  - `ds_pool_prop_handles`: pool handle KVS.
  - `ds_pool_attr_user`: user attribute KVS.
  - `ds_pool_prop_svc_ops`: service operations KVS.
- `struct pool_hdl`: current persisted pool-handle value with flags, security capabilities, machine hostname, credential length, and flexible credential bytes.
- `struct pool_hdl_v0`: old pre/current-format handle value containing only flags and capabilities.
- `extern daos_prop_t pool_prop_default`.
- `ds_pool_prop_default_init()` / `ds_pool_prop_default_fini()` declarations.

## Control flow

The header is declarative. It guides service code that opens the pool root KVS, pushes nested KVS paths, reads/writes property records, and upgrades old records. `srv_layout.c` instantiates the key symbols and default property table. Pool service code uses `struct pool_hdl` when recording open pool handles and keeps `struct pool_hdl_v0` for migration or compatibility with old-format records.

## State and persistence behavior

This file is the authoritative map of durable pool metadata keys. The root KVS stores pool metadata and nested KVS references. The pool map is split into `map_buffer` and `map_version` because `pool_buf` does not contain the version. The global version key tracks the overall pool/container layout version. Pool handle keys are UUIDs and values are `struct pool_hdl` objects; user attributes are null-terminated string keys with arbitrary byte-array values; service op keys combine client UUID and HLC timestamp and values record handled RPC results.

## Dependencies and integration points

It depends on DAOS base types and `MAXHOSTNAMELEN`. It must stay coordinated with `src/container/srv_layout.h` because the comments state the root KVS key namespace is shared enough that pool key suffixes must not collide with container root keys. It is consumed heavily by pool create/load/query/update/upgrade code in `srv_pool.c`, recovery container reset calls from container code, and IV property propagation in `srv_iv.c`.

## Risks and edge cases

- Adding new keys without checking container root key names can corrupt or confuse shared metadata layout.
- Value comments are part of the contract; code should not silently change a key's value type.
- `struct pool_hdl` has a flexible credential array and stores `size_t ph_cred_len`; persistent interpretation across platforms or versions must be handled carefully.
- Compatibility with `pool_hdl_v0` must be preserved until old pool formats are no longer supported.
- The global layout version includes container metadata, so pool-only upgrade logic can still affect container compatibility.

## Test signals

Useful tests include RDB layout creation and upgrade tests, old `pool_hdl_v0` migration/read tests, root-key collision checks against container layout, pool map version/buffer load tests, user attribute KVS round trips, service-op KVS idempotency tests, and schema checks ensuring any new key has a documented value type and instantiated `RDB_STRING_KEY`.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/pool/srv_layout.h -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/pool/srv_metrics.c -->
# sources/object-store/daos/src/pool/srv_metrics.c

## Purpose

This file implements telemetry metric allocation and per-pool metric directory lifecycle for the pool server module. It defines the metric nodes that `srv.c` registers through `struct daos_module_metrics pool_metrics` and provides helpers to create/destroy ephemeral telemetry directories for individual pools.

## Important APIs, types, and functions

- `ds_pool_metrics_alloc(const char *path, int tgt_id)`: allocates `struct pool_metrics`, asserts system-level metrics (`tgt_id < 0`), records a `started_at` timestamp, and creates counters/gauges under the supplied path.
- `ds_pool_metrics_count()`: returns the number of telemetry node pointers in `struct pool_metrics`.
- `ds_pool_metrics_free(void *data)`: frees the metrics container.
- `pool_metrics_gen_path()`: formats per-pool telemetry path as `pool/<uuid>`.
- `get_pool_dir_size()`: estimates ephemeral directory size from number of pool metric modules and `PER_METRIC_BYTES`.
- `ds_pool_metrics_start(struct ds_pool *pool)`: creates an ephemeral telemetry directory for a pool and initializes module metrics into `pool->sp_metrics`.
- `ds_pool_metrics_stop(struct ds_pool *pool)`: finalizes module metrics and deletes the ephemeral telemetry directory.

## Control flow

The module framework calls `ds_pool_metrics_alloc()` for module metric initialization. This function keeps going after individual `d_tm_add_metric()` failures, logging warnings but returning the allocated structure unless the structure allocation itself fails. When a pool starts, `ds_pool_metrics_start()` derives `pool->sp_path`, reserves telemetry shared-memory space with `d_tm_add_ephemeral_dir()`, and calls `dss_module_init_metrics()`. If module metric initialization fails after directory creation, it calls `ds_pool_metrics_stop()` to clean up. On pool stop, `ds_pool_metrics_stop()` finalizes module metrics first and then deletes the ephemeral directory.

## State and persistence behavior

Metrics are runtime telemetry state, not persistent pool metadata. The file stores metric node pointers in `struct pool_metrics` and writes into telemetry shared memory through `d_tm_*` APIs. Per-pool path state is stored in `pool->sp_path`, and metric handles are stored in `pool->sp_metrics`.

## Dependencies and integration points

It depends on the internal `struct pool_metrics` declaration in `srv_internal.h`, GURT telemetry producer APIs, DAOS server module metric init/fini helpers, and `struct ds_pool` fields from server pool definitions. Other pool service code increments or sets the metric nodes defined here, such as operation counters and service state gauges.

## Risks and edge cases

- `ds_pool_metrics_count()` assumes `struct pool_metrics` contains only `struct d_tm_node_t *` fields. Adding any non-pointer field would break the count.
- Individual metric creation failures are non-fatal, so later code must tolerate null metric node pointers.
- `D_ASSERT(tgt_id < 0)` means this allocator is only valid for system-level pool metrics.
- `pool_metrics_gen_path()` truncates defensively, but UUID path length changes should still be checked against `sp_path`.
- `ds_pool_metrics_stop()` returns after logging if directory deletion fails; callers do not get an error.

## Test signals

Tests should cover allocation failure, partial metric creation failure, metric count matching the structure field count, start failure cleanup after ephemeral directory creation, stop behavior when directory deletion fails, correct path formatting for pool UUIDs, and callers safely handling null metric pointers after non-fatal metric registration failures.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/pool/srv_metrics.c -->

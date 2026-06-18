# subset-b-007672 Research

Grouped source research for Lustre PTLRPC nodemap storage and Network Request Scheduler policy implementation. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/nodemap_storage.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/nodemap_storage.c

## Purpose

`nodemap_storage.c` owns persistent storage and wire export of Lustre nodemap configuration. It serializes `struct lu_nodemap` state into the `LUSTRE_NODEMAP_NAME` dt index, loads the index back into a fresh `struct nodemap_config`, registers MGS and target-side cache files, and serves nodemap config pages to MGC clients through MGS bulk config reads.

## Important APIs, Types, and Functions

The file revolves around `struct nodemap_key`, `union nodemap_rec`, `struct nm_config_file`, `struct lu_nodemap_fileset_info`, dt index objects, and the global MGS handle `nodemap_mgs_ncf`. Key exported APIs are `nodemap_idx_nodemap_add/update/del`, cluster role/offset/capability add/update/delete helpers, `nodemap_idx_range_add/del`, `nodemap_idx_idmap_add/del`, `nodemap_idx_fileset_add/update/update_header/del/clear`, `nodemap_idx_nodemap_activate`, `nm_config_file_register_mgs/tgt`, `nm_config_file_deregister_mgs/tgt`, `nodemap_process_idx_pages`, `nodemap_index_read`, and `nodemap_get_config_req`.

Local helpers initialize typed keys and records: cluster records capture name, squash IDs, map mode, audit/encryption, readonly/deny mount, GSS, and fileset-IAM flags; role records capture RBAC and privilege-raise masks; offset records capture UID/GID/projid offset ranges; ID map records capture client-to-filesystem IDs; range records support legacy NID4 start/end or newer NID prefix plus netmask; fileset header and fragment records split paths across fixed-size records.

## Control Flow

Write operations follow a consistent pattern: create a local `lu_env`, build a key/record pair, operate on the MGS nodemap index, and finalize the environment. `nodemap_idx_insert_batch`, `nodemap_idx_update`, and `nodemap_idx_delete_batch` declare dt operations, start a local transaction, take the dt write lock, execute insert/delete work, bump the dt object version through `nodemap_inc_version`, unlock, and stop the transaction. Add paths insert new records, update paths delete then insert, and delete paths tolerate `-ENOENT` only where explicitly documented.

Nodemap deletion walks the nodemap's RB trees and lists to remove associated role, offset, capability, UID/GID/projid maps, normal ranges, ban ranges, then the cluster record. Fileset operations use a header subid plus a contiguous subid range for fragments. Add and delete paths track partial progress and attempt undo; if undo fails, they clear the entire fileset subid range and return `-EIO` to signal that the on-disk fileset was wiped to avoid partial corruption.

Load flow is two-pass. `nodemap_load_entries` first walks only cluster records to create all nodemap objects and preserve their saved IDs, then restarts the iterator to process attributes, ranges, maps, global state, capabilities, offsets, and fileset fragments. `nodemap_process_keyrec` dispatches by encoded index type and subid. It uses the most recently referenced nodemap plus a linked list of loaded nodemaps to resolve attribute records that follow cluster records in the index. After loading, missing default nodemap and missing global active records are synthesized and written to disk before the new config is activated.

Wire export flow uses `nodemap_index_read` and `nodemap_page_build` to walk the dt index into `lu_idxpage` containers. The same two-pass ordering is used on the wire: cluster records first, attributes second. `nodemap_get_config_req` validates an `MGS_CFG_T_NODEMAP` request, allocates folios, fills pages from the index, updates the export's nodemap version, and sends pages through PTLRPC bulk put.

## State and Persistence Behavior

Persistent state is the nodemap dt index. Every successful insert, update, and batch delete increments the dt version so clients can detect in-flight config changes. Records are endian-normalized with `cpu_to_le*` and `le*_to_cpu` for scalar fields. Dynamic nodemaps (`nm_dyn`) are intentionally not persisted by the public add/delete/update helpers.

Runtime state includes `nodemap_mgs_ncf` for the MGS index, `ncf_list_head` for registered non-MGS target cache files, and `nodemap_config_loaded` guarded by `nodemap_config_loaded_lock`. `nodemap_config_set_active_mgc` prioritizes network-loaded MGS config over disk cache, resizes preallocated fileset strings to actual length, marks the config loaded, and rewrites all registered target caches from active in-memory config.

Target registration loads disk cache only if no config is already loaded; otherwise it writes the current active config into a fresh local cache. MGS registration loads from the supplied object and makes that object the authoritative persistent store. Deregistration drops dt object references and removes target entries from the list.

## Dependencies and Integration Points

The file depends on Lustre dt object APIs (`dt_trans_create`, declare/start/stop, `dt_insert`, `dt_delete`, iterators, index walk, version get/set), local object/index helpers, LNet NID conversion, nodemap core helpers from `nodemap_internal.h`, PTLRPC bulk transfer, MGS config request capsules, RB trees and lists inside nodemap objects, active config locking, and generated wire-layout constants validated by `wiretest.c`.

It integrates with MGS configuration distribution, MGC network loading, target local cache synchronization, nodemap admin operations that call the `nodemap_idx_*` persistence helpers, and security behavior that consumes the active nodemap config.

## Risks and Edge Cases

The loader assumes attributes can be associated with a previously loaded cluster record; corrupt or unexpectedly ordered indexes can produce `-ENOENT`. Fileset persistence is intentionally defensive but complex: partial add/delete undo mutates `nfi_fragment_cnt` and may wipe a subid range on undo failure. Range serialization rejects non-NID4 legacy range records and oversized netmask prefix records. Offset loading only uses the UID start/limit helper path, so the stored GID/projid offset fields are not independently restored there. Several operations require an MGS config file and return `-EINVAL` when no MGS is registered. `nodemap_cache_find_create` can unlink and recreate an index, so read-only devices and local OID recovery paths need careful coverage.

Concurrency risk is mostly around global config and cache transitions: active config is protected by `active_config_lock`, config loaded state has its own mutex, and target cache list operations have `ncf_list_lock`, but stale `ncf_obj == NULL` entries can exist after previous save failures and are skipped. Bulk export resets `ii_hash_end` to 0 if the dt version changes between reads, requiring clients to restart.

## Test Signals

Useful tests exercise add/update/delete of nodemap cluster records, roles, offsets, capabilities, UID/GID/projid maps, normal and ban ranges, and dynamic nodemap no-op behavior. Fileset tests should cover single-fragment, multi-fragment, alternate fileset IDs, readonly header update, partial insert/delete failure injection, clear-on-undo failure, invalid fragment count, and header subid alignment. Load tests should cover two-pass reconstruction, missing default/global records, legacy non-IAM fileset preservation, NID4 versus NID-mask ranges, corrupt record ordering, and endian round trips. Integration signals include MGS/TGT register/deregister, config-loaded gating, target cache rewrite after MGC activation, dt version restart behavior in `nodemap_index_read`, and PTLRPC bulk response sizing in `nodemap_get_config_req`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/nodemap_storage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/nrs.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/nrs.c

## Purpose

`nrs.c` is the Network Request Scheduler core for PTLRPC services. It registers policy descriptors, instantiates compatible policies on each service partition's regular and high-priority NRS heads, obtains per-request policy resources, enqueues and dispatches requests, supports runtime policy control, and cleans all policy state during service and module teardown.

## Important APIs, Types, and Functions

Central state is `struct nrs_core nrs_core`, `struct ptlrpc_nrs`, `struct ptlrpc_nrs_policy`, `struct ptlrpc_nrs_pol_desc`, `struct ptlrpc_nrs_pol_conf`, `struct ptlrpc_nrs_resource`, and `struct ptlrpc_nrs_request`. Important internal functions include `nrs_policy_start_locked`, `nrs_policy_stop_locked`, `nrs_policy_register`, `nrs_policy_unregister`, `nrs_resource_get_safe`, `nrs_resource_put_safe`, `nrs_request_enqueue`, `nrs_request_get`, and `nrs_request_removed`.

Exported or externally used APIs include `ptlrpc_service_nrs_setup`, `ptlrpc_service_nrs_cleanup`, `ptlrpc_nrs_req_initialize`, `ptlrpc_nrs_req_finalize`, `ptlrpc_nrs_req_add`, `__ptlrpc_nrs_req_get_nolock`, `ptlrpc_nrs_req_del_nolock`, `ptlrpc_nrs_req_pending_nolock`, `ptlrpc_nrs_req_throttling_nolock`, `ptlrpc_nrs_req_hp_move`, `ptlrpc_nrs_policy_control`, `ptlrpc_nrs_init`, and `ptlrpc_nrs_fini`.

## Control Flow

Module initialization creates the core policy list and registers built-in policies. FIFO and delay are registered unconditionally; CRR-N, ORR, TRR, and TBF are registered under server builds. Service setup walks service partitions under `nrs_core.nrs_mutex`, initializes a regular NRS head and optionally an HP head, and registers all compatible descriptors. Policies marked `PTLRPC_NRS_FL_REG_START` start immediately, which makes FIFO the default fallback.

Policy start is serialized per NRS head. Starting a fallback policy is allowed only during setup or as the already active fallback. Starting a primary requires a fallback, optionally restarts if arguments change, grabs a module reference, calls the policy start op outside the spinlock, sets the started reference, and replaces any previous primary. Stopping hides the policy from the NRS head, drops the started reference, waits up to 30 seconds for queued and started requests to drain, and calls the policy stop op when references reach zero.

Request initialization obtains resources for fallback and, if present, primary policies. Resource acquisition walks each policy's resource hierarchy by repeatedly calling `op_res_get`; if a primary rejects a request, only fallback resources remain. Enqueue tries primary resources first, then fallback, increments queued counters, and takes an extra started reference while the request is pending. Dispatch walks policies with queued requests, calls each policy's `op_req_get`, marks returned requests started, updates queued and started counters, and round-robins among policies with queued work. Dequeue and finish paths call policy dequeue/stop hooks and release resource and started references.

High-priority movement obtains HP resources in atomic context, locks the service partition request lock, verifies the request can move, removes it from the regular policy, swaps resource arrays, enqueues it on the HP head, then releases whichever resource set is no longer owned by the request.

## State and Persistence Behavior

NRS state is in-memory only. There is no disk persistence in this file; runtime controls are exposed through policy lprocfs/debugfs implementations and apply to live policy instances. Policy descriptors persist for the lifetime of the PTLRPC module. Policy instances persist for each service partition NRS head until service cleanup or external policy unregistration.

Per-policy state is protected by the NRS head spinlock for lifecycle and counters, plus policy-specific locks or atomic/refcount fields. `pol_start_ref` protects active, queued, and started request ownership. `pol_ref` protects callers that found a policy by name. Module references are held while a policy descriptor has active started instances.

## Dependencies and Integration Points

The core depends on PTLRPC service and service partition structures, `ptlrpc_all_services`, service CPT allocation helpers, built-in policy configuration symbols (`nrs_conf_fifo`, `nrs_conf_delay`, and server-only policies), lprocfs/debugfs policy hooks, Linux modules/refcounting, wait queues, and service request locks. It integrates with PTLRPC request receive/finish paths, high-priority request handling, ldlm lock reorder movement, service registration/unregistration, and lctl-facing policy control paths.

## Risks and Edge Cases

Fallback policy availability is a hard invariant; enqueue ends in `LBUG()` if no policy accepts a request. Runtime start/stop is constrained by transient `STARTING` and `STOPPING` states and can return `-EAGAIN` or `-EBUSY`. The 30-second stop wait means policy stop can fail while requests are still draining. External policies cannot be fallback or auto-start because cleanup cannot safely drain them during partial registration failure. Policy operations run partly outside locks, so policy implementations must obey the core's resource and request ownership contracts exactly.

HP movement is sensitive because it obtains resources before taking the request lock and may allocate with `GFP_ATOMIC`. Request initialized/finalized bits are intentionally accessed without locking at early/late lifecycle points. Debug/control callers can receive `-ENODEV` for stopped policies and `-ENOENT` for missing policy names.

## Test Signals

Core tests should cover service setup with and without HP queues, built-in policy registration order, fallback auto-start, starting and replacing primary policies, resetting to fallback, policy argument restart semantics, stop while queued/started requests drain, and service cleanup. Request tests should cover primary accept/reject fallback behavior, enqueue/dequeue counter updates, queued-policy round robin, peek versus get, finalize releasing both primary and fallback resources, HP move success and no-op cases, and throttling/pending queries. Control tests should exercise regular, HP, and both-queue policy commands, stopped policy `-ENODEV`, missing policy `-ENOENT`, and external policy registration rollback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/nrs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/nrs_crr.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/nrs_crr.c

## Purpose

`nrs_crr.c` implements the CRR-N NRS policy, a client-NID round-robin scheduler for PTLRPC requests. It batches requests per client NID up to a configurable quantum, orders batches by scheduling round and sequence, and exposes debugfs control for the quantum.

## Important APIs, Types, and Functions

The policy uses `struct nrs_crrn_net` for per-policy scheduler state and `struct nrs_crrn_client` for per-client resource buckets. The main hooks are `nrs_crrn_start`, `nrs_crrn_stop`, `nrs_crrn_ctl`, `nrs_crrn_res_get`, `nrs_crrn_res_put`, `nrs_crrn_req_get`, `nrs_crrn_req_add`, `nrs_crrn_req_del`, and `nrs_crrn_req_stop`. `crrn_req_compare` is the binheap comparator. `nrs_crrn_hashfn`, `nrs_crrn_cmpfn`, and `nrs_crrn_hash_params` define the client rhashtable keyed by `struct lnet_nid`. The exported configuration is `nrs_conf_crrn`.

Debugfs support is provided by `ptlrpc_lprocfs_nrs_crrn_quantum_seq_show`, `ptlrpc_lprocfs_nrs_crrn_quantum_seq_write`, and `nrs_crrn_lprocfs_init`, which expose `nrs_crrn_quantum` for regular and HP queues.

## Control Flow

Starting the policy allocates `nrs_crrn_net`, creates an atomic-grow binheap, initializes the client rhashtable, sets the default quantum to `OBD_MAX_RIF_DEFAULT`, and seeds sequence numbering at 1. Resource acquisition is two-level: the first call returns the scheduler resource embedded in `nrs_crrn_net`; the second looks up or inserts a client object by request peer NID, increments its reference count, and returns the client resource.

Enqueue obtains the client bucket from the request resource, decides whether the client needs a new scheduling round, assigns round and sequence to the request, inserts it into the heap, increments active request count, and decrements the client's remaining quantum. The comparator sorts by lower round first and lower sequence first, preserving batched client fairness. Dispatch removes the heap root, decrements the client's active count, logs the start, and advances the global round to the next request's round or increments it if the heap is empty. Dequeue has similar root-adjustment logic when removing a queued request before service.

Quantum control reads or writes `cn_quantum` through `ptlrpc_nrs_policy_control`. The write path accepts `reg_quantum:`, `hp_quantum:`, or a bare numeric value, validates against `LPROCFS_NRS_QUANTUM_MAX`, skips stopped policy instances through `-ENODEV`, and returns success if at least one requested live queue accepted the change.

## State and Persistence Behavior

All state is volatile. `nrs_crrn_net` owns the heap, client hash, global round, global sequence, and current quantum. Each client tracks NID, resource, refcount, active queued requests, current round, sequence, and remaining quantum. No state is persisted across service restart; quantum changes are runtime debugfs settings only.

Client objects remain in the rhashtable for the policy lifetime and are freed during policy stop after the heap is empty and all references have been released. The file asserts zero client references when destroying the hash.

## Dependencies and Integration Points

CRR-N depends on NRS core policy hooks, PTLRPC request peer IDs, LNet NID hashing and formatting, Lustre binheap utilities, Linux rhashtable, debugfs/lprocfs helpers, and PTLRPC policy control. It is registered as `crrn` with compatibility for all PTLRPC services when server policies are enabled.

## Risks and Edge Cases

The scheduler trades strict FIFO latency for per-client fairness; inactive clients with unused quantum are moved to a new round to avoid fragmented batches. `cn_quantum` is documented as accessed unlocked in enqueue, so debugfs writes can race with scheduling decisions but keep the value nonzero. Client hash insertion handles duplicate insertion races, but client objects are only reclaimed at policy stop, so workloads with many transient NIDs grow memory until stop. Request movement to HP can allocate client resources with `GFP_ATOMIC` and can fail under pressure.

## Test Signals

Tests should cover two or more clients with different request rates, quantum exhaustion moving a client to the next round, inactive-client unused quantum behavior, heap ordering by round then sequence, dequeue of the root versus non-root, resource lookup/insert races, reference release at finalize, policy stop with empty heap, debugfs regular/HP/bare quantum parsing, invalid zero or oversized quantum, and stopped-policy `-ENODEV` handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/nrs_crr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/nrs_delay.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/nrs_delay.c

## Purpose

`nrs_delay.c` implements an NRS policy that deliberately delays a configurable percentage of PTLRPC requests for a random interval between configurable minimum and maximum seconds. It is useful for testing, fault injection, and controlled scheduling delay experiments rather than normal fairness scheduling.

## Important APIs, Types, and Functions

The policy state is `struct nrs_delay_data`, which holds a binheap, embedded resource, `min_delay`, `max_delay`, and `delay_pct`. Main hooks are `nrs_delay_start`, `nrs_delay_stop`, `nrs_delay_ctl`, `nrs_delay_res_get`, `nrs_delay_req_get`, `nrs_delay_req_add`, `nrs_delay_req_del`, and `nrs_delay_req_stop`. `delay_req_compare` sorts heap nodes by `nr_u.delay.req_start_time`. The exported configuration is `nrs_conf_delay`.

Debugfs files are created by `nrs_delay_lprocfs_init`: `nrs_delay_min`, `nrs_delay_max`, and `nrs_delay_pct`. Shared parsing is handled by `lprocfs_nrs_delay_seq_write_common`, and each setting has regular and HP queue-specific read/write handlers.

## Control Flow

Starting allocates `nrs_delay_data`, creates an atomic-grow binheap, and initializes defaults: minimum 5 seconds, maximum 300 seconds, and 100 percent delayed. Resource acquisition is one-level and returns the embedded delay resource.

On enqueue, the policy first decides whether this request should be handled by delay. If `delay_pct` is zero, or a random draw is outside the configured percentage, `nrs_delay_req_add` returns 1 so NRS core falls back to another policy. If selected, it computes `req_start_time` as current real seconds plus a random value in `[min_delay, max_delay]` and inserts the request into the heap. Dispatch returns the earliest request only after its start time has passed, unless core calls with `force` to drain a stopped policy. Dequeue removes the heap node. Stop asserts the heap is empty before destroying it.

Control operations read and write min, max, and percentage under the NRS lock. Writes enforce `min <= max`, `max >= min`, and percentage within 0 to 100. Debugfs writes accept `reg_delay_*:`, `hp_delay_*:`, or a bare numeric value, then apply through `ptlrpc_nrs_policy_control`.

## State and Persistence Behavior

The delay heap and settings are runtime-only per policy instance. There is no disk persistence. Existing queued requests retain their already assigned `req_start_time` when min, max, or percentage changes; new values affect later enqueues only.

## Dependencies and Integration Points

The file depends on NRS core hooks, Linux random (`get_random_u32_below`), real-time seconds (`ktime_get_real_seconds`), Lustre binheap utilities, debugfs/lprocfs helpers, PTLRPC request arrival timestamps for logging, and service regular/HP queue control. It is compatible with all PTLRPC services.

## Risks and Edge Cases

`delay_pct` is an unsigned value but the control code still checks `< 0`, which is ineffective but harmless. If `max_delay - min_delay + 1` is large, the random range calculation must remain within type bounds. Since the heap is ordered by wall-clock real seconds, system time changes can affect observed delay. A high delay percentage with long maximum delay can cause service backlog and apparent hangs unless operators understand the policy is active. Stopped-policy draining relies on `force` to return requests before their scheduled start time.

## Test Signals

Tests should cover delay selection at 0, partial, and 100 percent; random start times within inclusive bounds; heap ordering by earliest start time; `peek` preserving heap membership; `force` returning not-yet-ready requests; dequeue and stop with empty heap; debugfs parsing for regular, HP, and bare settings; min greater than max and max less than min rejection; percentage bounds; and runtime changes affecting only subsequent requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/nrs_delay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/nrs_fifo.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/nrs_fifo.c

## Purpose

`nrs_fifo.c` implements the FIFO NRS policy, the default and fallback scheduler for PTLRPC requests. It preserves the historical non-NRS behavior by serving requests in network arrival enqueue order.

## Important APIs, Types, and Functions

The policy uses `struct nrs_fifo_head`, which contains the FIFO list, embedded resource, and debug sequence counter. Main hooks are `nrs_fifo_start`, `nrs_fifo_stop`, `nrs_fifo_res_get`, `nrs_fifo_req_get`, `nrs_fifo_req_add`, `nrs_fifo_req_del`, and `nrs_fifo_req_stop`. The exported policy configuration is `nrs_conf_fifo`, with name `fifo`, compatibility for all services, and flags `PTLRPC_NRS_FL_FALLBACK | PTLRPC_NRS_FL_REG_START`.

## Control Flow

Policy start allocates and initializes the list head. Resource acquisition is one-level and always returns the embedded FIFO resource. Enqueue assigns a monotonically increasing debug sequence and appends the request to the tail of the list. Dispatch returns the first list entry and removes it unless the caller is only peeking. Dequeue removes an arbitrary queued request from the list. Request stop only logs completion with the stored sequence.

Because FIFO is both fallback and auto-started at registration time, NRS core always has a policy that should accept requests when primary policies reject, are stopped, or do not support the request type.

## State and Persistence Behavior

FIFO state is fully in-memory per NRS head. The list contains currently queued requests, and `fh_sequence` is only for tracing. There is no runtime debugfs configuration and no persistent state.

## Dependencies and Integration Points

FIFO depends on NRS core policy hooks, Linux list primitives, Lustre CPT allocation helpers, request peer formatting, and PTLRPC trace logging. It integrates with every PTLRPC service as the regular and HP fallback policy.

## Risks and Edge Cases

This policy deliberately provides no fairness beyond arrival order, so one client or request class can dominate when FIFO is the only active policy. It must remain reliable because NRS core assumes at least fallback enqueue succeeds. Stop asserts the queue is empty, so lifecycle bugs in core or callers show up as assertions. Sequence wrap is possible over very long lifetimes but affects only debug output.

## Test Signals

Tests should verify tail enqueue/head dequeue order, peek without removal, arbitrary dequeue, sequence assignment, empty queue returning NULL, stop requiring an empty list, fallback auto-start during service setup, and fallback handling when a primary policy rejects a request.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/nrs_fifo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/nrs_orr.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/nrs_orr.c

## Purpose

`nrs_orr.c` implements two related server-side NRS policies for OST I/O: ORR, object-based round robin over backend filesystem objects, and TRR, target-based round robin over OST indices. Both batch requests by object or target, sort within a batch by logical or physical offset, and expose runtime controls for quantum, offset mode, and supported RPC types.

## Important APIs, Types, and Functions

Shared state is `struct nrs_orr_data` for a policy instance and `struct nrs_orr_object` for an object or target bucket. Request-specific state lives in `nr_u.orr` fields such as key, range, round, sequence, and cached physical/key flags. Main hooks are `nrs_orr_init`, `nrs_orr_start`, `nrs_orr_stop`, `nrs_orr_ctl`, `nrs_orr_res_get`, `nrs_trr_res_get`, `nrs_orr_res_put`, `nrs_orr_req_get`, `nrs_orr_req_add`, `nrs_orr_req_del`, `nrs_orr_req_stop`, and `nrs_trr_req_stop`. `orr_req_compare` is the heap comparator. Exported configurations are `nrs_conf_orr` and `nrs_conf_trr`, both compatible only with `ost_io`.

Important helpers include `nrs_orr_req_supported`, `nrs_orr_key_fill`, `nrs_orr_range_fill_logical`, `nrs_orr_range_fill_physical`, `nrs_orr_range_fill`, ORR rhashtable operations, TRR XArray lookup/insert, and debugfs conversion helpers for supported request types.

## Control Flow

Start allocates `nrs_orr_data`, creates an atomic-grow heap, creates a per-instance slab cache, and initializes either an ORR rhashtable or a TRR XArray. Defaults are quantum 256, supported requests set to `NOS_DFLT`, physical offset ordering enabled, and sequence seeded to 1. `nrs_orr_init` logs when the policy is used on a service with multiple CPTs, because per-partition scheduling may reduce policy effectiveness.

Resource acquisition first returns the top-level scheduler resource. The second level rejects unsupported opcodes so requests fall back to FIFO or another policy. ORR fills a key from the OST object FID derived from the request OST body and server OST index; TRR uses the server OST index directly. Both fill an offset range from `RMF_OBD_IOOBJ` and `RMF_NIOBUF_REMOTE`; if physical mode is enabled for reads and the call may sleep, ORR/TRR attempts FIEMAP through `obd_get_info` and falls back to logical offsets on failure. ORR stores bucket objects in an RCU-protected rhashtable with refcounts and frees them after removal via `call_rcu`. TRR stores stable target buckets in an XArray and frees them at stop.

Enqueue applies the same batched round-robin algorithm used by CRR-N, but the bucket is an object FID for ORR or OST index for TRR. The request is tagged with bucket round and sequence, inserted into the heap, and the bucket's active count and remaining quantum are updated. The comparator sorts by round, then bucket sequence, then range start, then shorter range end. Dispatch and dequeue remove heap nodes, update active counts, and advance the global round to the next heap root.

Debugfs control is shared between ORR and TRR through `nrs_lprocfs_orr_data`. Each policy exports quantum, offset type (`physical` or `logical`), and supported request type (`reads`, `writes`, or `reads_and_writes`) files. Read and write paths apply settings separately to regular and HP NRS heads and treat stopped instances as skippable `-ENODEV` cases.

## State and Persistence Behavior

All scheduler state is volatile per service partition and NRS queue. `od_quantum`, `od_supp`, and `od_physical` are runtime debugfs settings. ORR bucket objects are reference-counted and can be removed when their resource references drop to zero; TRR bucket objects are retained in the XArray for the policy lifetime. Request keys and physical-offset flags are cached in `nr_u.orr` so HP movement does not need to repeat sleeping or already completed work.

## Dependencies and Integration Points

The file depends on NRS core hooks, OST request layouts (`RMF_OST_BODY`, `RMF_OBD_IOOBJ`, `RMF_NIOBUF_REMOTE`), `ostid_to_fid`, server data OST indices, FIEMAP via `obd_get_info(KEY_FIEMAP)`, Lustre binheap utilities, rhashtable, XArray, RCU, slab caches, PTLRPC debugfs/lprocfs helpers, and regular/HP queue policy control. It integrates only with the `ost_io` PTLRPC service and only schedules `OST_READ` and `OST_WRITE` when enabled.

## Risks and Edge Cases

Unsupported request types, missing exports, missing request capsule fields, or key/range fill errors cause the policy to reject the request and rely on fallback scheduling. Physical offset lookup can sleep, so HP movement and atomic contexts use cached or logical offsets. FIEMAP failure silently falls back to logical ordering, which is safer but may surprise performance investigations. ORR has complex rhashtable insertion races and refcount-zero retry behavior; resize pressure can loop with short delays. Runtime settings are noted as accessed unlocked in scheduling paths. Multiple CPTs reduce global ordering because each partition schedules independently.

There are parser risks in debugfs paths: bare offset and supported-string writes rely on the buffer start when no named regular/HP value is found, so invalid or empty strings must be rejected cleanly. TRR does not define an `op_res_put` hook because its XArray buckets are retained until stop, unlike ORR's refcounted bucket removal.

## Test Signals

Tests should cover ORR object key generation from OST body and server index, TRR target key generation, unsupported opcode fallback, missing export/capsule failures, logical range extraction, physical FIEMAP success and fallback, HP move using cached request data, heap ordering by round, sequence, start offset, and shorter end offset, quantum exhaustion and inactive-bucket behavior, ORR rhashtable race/refcount cleanup, TRR XArray duplicate insertion, stop cleanup with RCU barrier, and all debugfs controls for regular/HP/bare values. Performance tests should compare single-CPT and multi-CPT behavior, and read/write support toggles should be verified against `OST_READ` and `OST_WRITE` traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/nrs_orr.c -->

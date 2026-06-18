# subset-b-007669 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_svc_upcall.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_svc_upcall.c

## Purpose
`gss_svc_upcall.c` implements the server-side RPCSEC_GSS upcall bridge for Lustre PTLRPC. It owns two upcall-backed caches: the RPCSEC init cache (`rsicache`) that sends context-init tokens to userspace, and the RPCSEC context cache (`rsccache`) that stores accepted service contexts imported from userspace. The file also manages reverse service contexts used for callbacks, initializes cache state at module load, and checks whether the `lsvcgssd` init socket is available.

## Important APIs, types, and functions
- Global state: `rsicache`, `rsccache`, `krb5_allow_old_client_csum`, and the randomized `__ctx_index` counter protected by `__ctx_index_lock`.
- Hash helpers: `hash_mem()` and 64-bit `hash_mem_64()` compute cache bucket keys from raw handles and tokens.
- RSI cache functions: `rsi_entry_init()`, `rsi_entry_free()`, `rsi_do_upcall()`, `rsi_parse_downcall()`, `rsi_entry_get()`, `rsi_entry_put()`, and `rsi_upcall_cache_ops`.
- RSC cache functions: `rsc_entry_init()`, `__rsc_free()`, `rsc_do_upcall()`, `rsc_parse_downcall()`, `rsc_accept_expired()`, `rsc_entry_get()`, `rsc_entry_put()`, and `rsc_upcall_cache_ops`.
- Context-facing exports: `gss_svc_upcall_handle_init()`, `gss_svc_upcall_get_ctx()`, `gss_svc_upcall_put_ctx()`, `gss_svc_upcall_destroy_ctx()`, `gss_svc_upcall_install_rvs_ctx()`, `gss_svc_upcall_expire_rvs_ctx()`, `gss_svc_upcall_dup_handle()`, and `gss_svc_upcall_update_sequence()`.
- Lifecycle: `gss_init_svc_upcall()` creates both caches; `gss_exit_svc_upcall()` tears them down.

## Control flow
For `PTLRPC_GSS_PROC_INIT`, `sec_gss.c` calls `gss_svc_upcall_handle_init()`. This builds a temporary `gss_rsi` key from the incoming GSS handle, incoming token, Lustre service type, primary peer NID, and nodemap name. `rsi_entry_get()` may trigger `rsi_do_upcall()`, which formats a single argument containing the cache key, service, NID, suggested context index, nodemap, input handle, and token, then invokes the configured userspace helper with `call_usermodehelper()`. Userspace later writes a downcall. `rsi_parse_downcall()` records major/minor status plus output handle and token.

After the RSI result is available, `gss_svc_upcall_handle_init()` looks up the output handle in `rsccache`. RSC entries are populated by userspace downcalls through `rsc_parse_downcall()`, which imports the mechanism context via `lgss_import_sec_context()`, queries its expiry, and fills service identity fields including remote/root/MDS/OSS flags, mapped uid, uid, gid, mechanism, and nodemap. On success, the request context gets an extra cache reference to `gsc_ctx`, the reverse handle is copied, the target is recorded, and an INIT reply containing the output handle/token and status is packed.

For normal data requests, `gss_svc_upcall_get_ctx()` searches `rsccache` by wire handle and returns the embedded `gss_svc_ctx`; the caller later drops it with `gss_svc_upcall_put_ctx()`. Destroy requests mark the cache entry invalid and force early expiry. Reverse-context helpers install a copied mechanism context into `rsccache`, update expiry from `lgss_inquire_context()`, assign server role bits from the import target type, and preserve sequence state for callbacks.

## State and persistence behavior
All state is in memory. RSI entries are short-lived and invalidated after an init request is handled regardless of success. RSC entries live until their GSS mechanism expiry, explicit destroy, invalidation, or cache cleanup. Context expiry is converted from real-time GSS expiry to monotonic cache expiry using current real seconds. Reverse contexts can be made to expire soon, and their last reverse sequence number can be stored through `gss_svc_upcall_update_sequence()`. Cache initialization seeds `__ctx_index` from kernel randomness to reduce handle collisions after reboot.

## Dependencies and integration points
This file depends on Lustre upcall cache infrastructure, raw object helpers, nodemap lookup, LNet NID conversion, GSS mechanism APIs, PTLRPC reply packing, and kernel userspace-helper/socket APIs. It integrates tightly with `sec_gss.c` for server request admission, error notify packing, reverse context creation, and context lifetime. It also integrates with `lproc_gss.c`, which exposes cache tunables and downcall debugfs files.

## Risks
- `rsi_do_upcall()` must calculate its helper argument length correctly; wrong sizing risks truncation or `-E2BIG`.
- Userspace downcall parsing trusts length fields after magic checks; malformed buffers must be rejected without leaking partially allocated raw objects.
- `gss_svc_upcall_handle_init()` invalidates RSI entries after use, so retry behavior depends on callers and clients reissuing init tokens.
- Reverse-context expiry and accepted-expired logic are delicate: too strict can break callbacks, too permissive can allow use of stale contexts.
- Hash functions are not cryptographic; correctness depends on full match comparisons after bucket selection.
- The old Kerberos checksum compatibility gate is security-sensitive and controlled by the `krb5_allow_old_client_csum` tunable.

## Test signals
Useful tests include GSS mount/authentication with `lsvcgssd` running and absent, malformed RSI/RSC downcalls, INIT with missing/oversized handles or tokens, old-client checksum compatibility toggling, context expiry and destroy behavior, reverse callback context install/expire/update paths, nodemap identity propagation, and reboot/failover cases where randomized context indexes avoid stale-handle confusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_svc_upcall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/lproc_gss.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/lproc_gss.c

## Purpose
`lproc_gss.c` provides the sysfs and debugfs control surface for Lustre GSS security. It exposes GSS init-channel input, compatibility and namespace tunables, RSI/RSC cache helper paths and expiry values, downcall injection files used by userspace GSS daemons, replay/out-of-sequence statistics, and an `lgss_keyring` debug-level knob.

## Important APIs, types, and functions
- Global objects: `gss_debugfs_dir`, `gss_kobj`, and `gss_kobj_lk`.
- Statistics: `gss_stat_oos` stores client fall-behind counts and server replay/pass counters; `gss_stat_oos_record_cli()` and `gss_stat_oos_record_svc()` update it.
- Sysfs attributes: `init_channel`, `krb5_allow_old_client_csum`, optional `gss_check_upcall_ns`, `rsi_upcall`, `rsi_entry_expire`, `rsi_acquire_expire`, and `lgss_keyring/debug_level`.
- Debugfs files: `replays`, `rsi_info`, and `rsc_info`.
- Downcall handlers: `ldebugfs_rsi_info_seq_write()` and `ldebugfs_rsc_info_seq_write()`.
- Lifecycle: `gss_init_tunables()` creates sysfs/debugfs nodes; `gss_exit_tunables()` removes them.

## Control flow
During module initialization, `gss_init_tunables()` initializes the OOS spinlock, creates `debugfs/sptlrpc/gss`, installs debugfs file operations, creates the `sptlrpc/gss` sysfs kobject, then creates the nested `lgss_keyring` kobject. Failures unwind through `gss_exit_tunables()`.

`init_channel_store()` passes written bytes to `gss_do_ctx_init_rpc()` for client context initialization. `rsi_upcall_store()` copies a user-supplied path, validates it through `upcall_cache_set_upcall()`, and updates the RSI helper. Expiry stores parse signed integer input and reject negative or too-large acquire expiry values.

`ldebugfs_rsi_info_seq_write()` and `ldebugfs_rsc_info_seq_write()` implement two-pass dynamic allocation. They first read the fixed header, validate the magic, use the embedded payload length to allocate the full structure, then re-read the full user buffer. RSI downcalls are handed to `upcall_cache_downcall()` with the user-provided hash. RSC downcalls first extract the context handle, create or acquire the matching RSC cache entry on the fly, mark the entry acquiring, and then call `upcall_cache_downcall()` using the entry key.

## State and persistence behavior
Tunables are runtime kernel state only. Cache expiry and upcall path changes persist only until module unload or reset. OOS statistics are in-memory counters reset on module reload. The downcall files do not store data themselves; they mutate the upcall caches in `gss_svc_upcall.c`. Cleanup removes sysfs groups, drops kobject references, and recursively removes debugfs entries.

## Dependencies and integration points
The file depends on sysfs/kobject APIs, debugfs/Lustre ldebugfs helpers, `copy_from_user()`, upcall-cache APIs, and GSS structs declared in `gss_internal.h`. It directly manipulates `rsicache` and `rsccache` created by `gss_svc_upcall.c`, calls client upcall code through `gss_do_ctx_init_rpc()`, and reports sequence-window events generated by `sec_gss.c`.

## Risks
- Downcall writes allocate based on userspace-provided lengths after magic validation; large or inconsistent lengths can cause memory pressure or parse failure.
- The RSC downcall path manually extracts and allocates the handle before cache insertion; error paths must free the temporary `gss_rsc` correctly.
- Changing `rsi_upcall` can break authentication immediately if the path is not executable or points to a mismatched helper.
- `krb5_allow_old_client_csum` weakens compatibility behavior and needs operational care.
- Debugfs/sysfs initialization ordering matters because other GSS init steps expect the tunables to exist or cleanly unwind.

## Test signals
Test by reading/writing each sysfs tunable, validating bad boolean/integer/path input, injecting malformed RSI/RSC downcalls, verifying successful daemon downcalls create usable contexts, checking replay statistics after duplicate or delayed sequence traffic, and exercising init failure unwind by forcing kobject or debugfs creation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/lproc_gss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/sec_gss.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/sec_gss.c

## Purpose
`sec_gss.c` is the main Lustre PTLRPC RPCSEC_GSS security policy implementation. It formats and verifies GSS wire headers, signs and verifies integrity-protected messages, wraps and unwraps privacy-protected messages, manages client and server GSS context lifetimes, enforces sequence replay windows, allocates/enlarges secure request and reply buffers, handles server-side request admission, and initializes all GSS mechanisms and policy support.

## Important APIs, types, and functions
- Wire helpers: `gss_header_swabber()`, `gss_swab_header()`, `gss_mech_payload()`, `gss_sign_msg()`, `gss_verify_msg()`, and `gss_unseal_msg()`.
- Client context lifecycle: `cli_ctx_expire()`, `cli_ctx_check_death()`, `gss_cli_ctx_uptodate()`, `gss_cli_ctx_finalize()`, `gss_cli_ctx_init_common()`, and `gss_cli_ctx_fini_common()`.
- Sequence protection: `gss_do_check_seq()` and `gss_check_seq_num()` implement main and back replay windows.
- Client request/reply operations: `gss_cli_ctx_sign()`, `gss_cli_ctx_verify()`, `gss_cli_ctx_seal()`, `gss_cli_ctx_unseal()`, and `gss_cli_ctx_handle_err_notify()`.
- Security object helpers: `gss_sec_create_common()`, `gss_sec_destroy_common()`, `gss_sec_kill()`, `gss_sec_install_rctx()`, and `gss_copy_rvc_cli_ctx()`.
- Buffer APIs: `gss_alloc_reqbuf()`, `gss_free_reqbuf()`, `gss_alloc_repbuf()`, `gss_free_repbuf()`, and `gss_enlarge_reqbuf()`.
- Server operations: `gss_svc_accept()`, `gss_svc_handle_init()`, `gss_svc_handle_data()`, `gss_svc_handle_destroy()`, `gss_svc_verify_request()`, `gss_svc_unseal_request()`, `gss_svc_alloc_rs()`, `gss_svc_authorize()`, `gss_svc_free_rs()`, `gss_svc_invalidate_ctx()`, and `gss_pack_err_notify()`.
- Module lifecycle: `sptlrpc_gss_init()` and `sptlrpc_gss_exit()`.

## Control flow
On the client side, request allocation chooses a layout from the negotiated service: NULL/AUTH/INTG use an outer GSS header, embedded Lustre message, optional user and bulk descriptors, and optional MIC; PRIV uses a clear inner Lustre message plus an encrypted outer token. `gss_cli_ctx_sign()` fills a GSS header and MIC for non-private traffic, incrementing the context sequence and repacking if the sequence falls too far behind concurrent sends. `gss_cli_ctx_seal()` wraps the clear message into a privacy token. Replies are verified by `gss_cli_ctx_verify()` for integrity modes or unwrapped by `gss_cli_ctx_unseal()` for privacy. Server GSS error notifications can expire and replace dead client contexts to recover from server reboot or stale handles.

On the server side, `gss_svc_accept()` decodes the GSS header, allocates `gss_svc_reqctx`, saves the wire context, restores byte order for MIC coverage, and dispatches by `gh_proc`. INIT requests are parsed by `gss_svc_handle_init()` and delegated to `gss_svc_upcall_handle_init()`. DATA requests find an established service context, then verify MIC or unwrap privacy data, unpack user/bulk descriptors, and set request pointers. DESTROY requests verify with INTG service and invalidate the context. Reply allocation and authorization mirror the selected service: `gss_svc_sign()` signs integrity replies, while `gss_svc_seal()` wraps privacy replies.

The recovery-sensitive sequence algorithm uses phase 0 before integrity verification to reject obvious replays without advancing the window, phase 1 after verification to commit main-window sequence numbers, and phase 2 to allow a limited back window for requests that fell behind during expensive verification or unwrap processing.

## State and persistence behavior
The file keeps early-reply offset caches in `gss_at_reply_off_integ` and `gss_at_reply_off_priv`. Client contexts hold GSS mechanism contexts, handles, service handles, sequence counters, expiry times, flags, request lists, and generation/connection counters. Service request contexts carry a policy reference and refcount; reply states hold an extra reference until freed. Sequence windows live in the service context and are protected by spinlocks. Security objects hold imports, mechanism references, nodemap names, flavor, garbage-collection interval, and reverse-context state. All state is in-memory and reconstructed through GSS upcalls, reconnect, or reverse-context copy.

## Dependencies and integration points
`sec_gss.c` sits between PTLRPC core, Lustre message packing, sptlrpc policy registration, GSS mechanisms (`null`, Kerberos, and shared-key), keyring/upcall code, bulk security descriptors, nodemap identity, OBD import/export state, and adaptive timeout early replies. It calls into `gss_svc_upcall.c` for service-context lookup/install/destroy and into `lproc_gss.c` statistics for out-of-sequence tracking. Module init orders tunables, client upcall, service upcall, mechanisms, and keyring so the registered policy is usable immediately.

## Risks
- Message layout calculations must stay synchronized across allocation, enlargement, signing, sealing, verifying, and reply authorization.
- The sequence replay algorithm is intentionally permissive for delayed valid requests; mistakes can either reject legitimate traffic under load or allow replay.
- Error-notify handling can trigger context replacement and resend; wrong conditions could loop or hide real authorization failures.
- Privacy paths copy decrypted data back into the incoming Lustre message buffer and assume output fits the original buffer.
- Request enlargement mutates `rq_reqmsg` while replay traversals can inspect requests; the code uses import locking as a narrow race workaround.
- Reverse context cleanup deliberately avoids some final RPCs and must not destroy a callback context still needed for recovery.

## Test signals
Strong coverage includes NULL/AUTH/INTG/PRIV request and reply round trips, bulk read/write descriptors, user descriptor packing, early replies with checksum and AT offsets, duplicate/reordered/high sequence numbers, context INIT/CONTINUE/DESTROY, stale handle and bad MIC error notifications, server reboot/failover with context replacement, request buffer enlargement under replay, privacy unwrap with malformed ciphertext, and module init unwind across each mechanism/keyring failure point.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/sec_gss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/heap.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/heap.c

## Purpose
`heap.c` implements Lustre's generic binary min-heap used by PTLRPC/NRS code. It stores caller-owned `struct binheap_node` pointers, orders them through caller-provided callbacks, and uses a segmented pointer array so the heap can grow without reallocating one contiguous large table.

## Important APIs, types, and functions
- Allocation macros: `CBH_ALLOC()` chooses CPT-aware or normal allocation and honors `CBH_FLAG_ATOMIC_GROW`; `CBH_FREE()` frees one pointer fragment.
- Capacity management: `binheap_grow()` allocates single, double, and triple indirect pointer fragments in `CBH_SIZE` chunks.
- Lifecycle: `binheap_create()` allocates and preallocates capacity; `binheap_destroy()` frees all pointer fragments and the heap object.
- Access and ordering: `binheap_pointer()`, `binheap_find()`, `binheap_bubble()`, and `binheap_sink()`.
- Mutators: `binheap_insert()`, `binheap_remove()`, and `binheap_relocate()`.
- Exported symbols: create, destroy, find, insert, remove, and relocate.

## Control flow
`binheap_create()` validates that a compare callback exists, allocates the heap on the requested CPT if provided, initializes counters and private data, pre-grows to the requested count without atomic growth, then enables `CBH_FLAG_ATOMIC_GROW` for future inserts if requested. Inserts grow capacity if `cbh_nelements == cbh_hwm`, call optional `hop_enter()`, append the node at the end, increment the element count, and bubble it toward the root. Removes validate the node index, replace the removed slot with the last node unless removing the last node, relocate the replacement by bubbling or sinking, poison the removed node index, and call optional `hop_exit()`. `binheap_relocate()` is the caller-facing operation for priority changes.

## State and persistence behavior
The heap stores only in-memory pointers and per-node `chn_index` values. Capacity high-water mark grows in `CBH_SIZE` chunks and is not shrunk on removal. Node ownership remains with callers; this file only owns the pointer indirection arrays and the heap object. `CBH_POISON` marks removed nodes. There is no persistence and no internal synchronization.

## Dependencies and integration points
The implementation depends on `lustre_net.h`, `heap.h`, Lustre allocation wrappers, assertions, and optional CPT allocation APIs. The header notes NRS policies as the primary consumer, with heap instances tied to CPTs. Callers provide ordering and entry/exit hooks through `struct binheap_ops`.

## Risks
- No locking is provided; callers must serialize insert, remove, find, and priority-change operations.
- `binheap_remove()` returns early when removing the last node before poisoning the node or calling `hop_exit()`, so callers and hooks must account for that behavior.
- Capacity is never reduced, so transient large workloads keep pointer fragments until destroy.
- Compare callback semantics define heap correctness; inconsistent ordering can corrupt scheduling behavior.
- Triple-indirect growth has hard limits based on `CBH_SHIFT` and 32-bit index space.

## Test signals
Test with ordered, reverse-ordered, random, and equal-priority inserts; repeated remove-root sequences; removal of arbitrary middle and last elements; priority increases/decreases followed by relocate; forced growth through single/double/triple indirection boundaries; callback failure from `hop_enter()`; atomic allocation mode; CPT allocation; and debug assertions for stale or double-removed nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/heap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/heap.h -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/heap.h

## Purpose
`heap.h` declares the public interface and data structures for Lustre's generic binary min-heap. It documents expected caller responsibilities: embed `struct binheap_node` in caller objects, provide a mandatory comparison callback, and perform external locking.

## Important APIs, types, and functions
- Constants: `CBH_SHIFT`, `CBH_SIZE`, `CBH_MASK`, `CBH_NOB`, and `CBH_POISON` define fragment sizing and removed-node poison value.
- Flags: `CBH_FLAG_ATOMIC_GROW` requests atomic allocation for capacity growth after creation.
- `struct binheap_ops`: optional `hop_enter()` and `hop_exit()` callbacks plus mandatory `hop_compare()` predicate. The predicate returns true when node `a` should sort before node `b`.
- `struct binheap`: contains triple/double/single indirect element arrays, element count, high-water mark, flags, ops, caller private data, and CPT placement fields.
- Public functions: `binheap_create()`, `binheap_destroy()`, `binheap_find()`, `binheap_insert()`, `binheap_remove()`, and `binheap_relocate()`.
- Inline helpers: `binheap_size()`, `binheap_is_empty()`, `binheap_root()`, and `binheap_remove_root()`.

## Control flow
Consumers include this header, embed `struct binheap_node` in schedulable objects, initialize the node index according to local convention, create a heap with callbacks, insert nodes, inspect index 0 with `binheap_root()`, and remove root or arbitrary nodes as scheduling decisions are made. If a node's priority changes while it is in the heap, callers invoke `binheap_relocate()` to restore ordering.

## State and persistence behavior
The header exposes the heap internals rather than making `struct binheap` opaque. The heap tracks current size in `cbh_nelements`, allocated pointer capacity in `cbh_hwm`, and each node's current position in its embedded `chn_index`. State is volatile and caller-owned except for the heap's pointer fragments.

## Dependencies and integration points
The header relies on `struct binheap_node` being declared elsewhere in Lustre headers, and on `struct cfs_cpt_table` for CPT-aware allocation. It is intended for PTLRPC/NRS users but generic enough for other kernel-internal Lustre users needing a min-heap.

## Risks
- Because internals are public, consumers can accidentally mutate heap fields and violate invariants.
- The interface does not encode locking; misuse in concurrent paths can corrupt `chn_index` and pointer arrays.
- `hop_compare()` semantics are easy to invert, producing a max-heap or unstable ordering.
- `binheap_root()` and `binheap_remove_root()` call `binheap_find(0)` and return NULL on empty heaps; callers must handle NULL.

## Test signals
Header-level validation should include compile coverage for callback signatures, users that call all inline helpers on empty and non-empty heaps, static analysis for external locking around heap mutation, and ABI/API compatibility checks for NRS policy users embedding `struct binheap_node`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/heap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/import.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/import.c

## Purpose
`import.c` manages Lustre client-side PTLRPC imports: connection state, reconnect and failover, invalidation, replay recovery, disconnect, idle disconnect, cleanup, and adaptive timeout measurement. An import is the client's connection/session state toward a target; this file is the state-machine core that moves it between NEW, CONNECTING, FULL, DISCON, REPLAY, RECOVER, EVICTED, IDLE, and CLOSED.

## Important APIs, types, and functions
- State helpers: `import_set_state_nolock()`, `import_set_state()`, `ptlrpc_init_import()`, `ptlrpc_import_enter_resend()`, and `deuuidify()`.
- Disconnect/invalidate: `ptlrpc_set_import_discon()`, `ptlrpc_deactivate_import()`, `ptlrpc_invalidate_import()`, `ptlrpc_cleanup_imp()`, `ptlrpc_fail_import()`, and `ptlrpc_reconnect_import()`.
- Connect path: `import_select_connection()`, `ptlrpc_connect_import()`, `ptlrpc_connect_import_locked()`, `ptlrpc_connect_interpret()`, `ptlrpc_connect_set_flags()`, and `ptlrpc_prepare_replay()`.
- Recovery: `ptlrpc_import_recovery_state_machine()`, `signal_completed_replay()`, `completed_replay_interpret()`, and `ptlrpc_invalidate_import_thread()`.
- Disconnect path: `ptlrpc_disconnect_prep_req()`, `ptlrpc_disconnect_import_async()`, `ptlrpc_disconnect_import()`, `ptlrpc_disconnect_and_idle_import()`, and their interpret/end helpers.
- Adaptive timeout utilities: `obd_at_measure()` and `import_at_get_index()`.
- Local structs: `ptlrpc_connect_async_args` carries committed transno and initial-connect status; `disconnect_async_arg` carries completion/result/noclose for async disconnect.

## Control flow
Failure begins with `ptlrpc_set_import_discon()` or `ptlrpc_fail_import()`, which transition a FULL import to DISCON, optionally mark it invalid, emit OBD events, and wake the pinger. `ptlrpc_invalidate_import()` deactivates the import if needed, aborts inflight RPCs, waits until `imp_inflight` reaches zero, emits invalidate events, flushes security contexts, and wakes waiters.

Connect starts in `ptlrpc_connect_import_locked()` under `imp_lock`. It rejects CLOSED/FULL/already-connecting imports, increments connection count, records initial versus reconnect state, selects a connection, adapts security, rebuilds connect data from original requested flags, lets the OBD layer prepare reconnect data, packs a CONNECT RPC with DLM handle, connect data, optional SELinux policy, timeout data, async args, and replay/transno flags, then queues it to `ptlrpcd`.

`ptlrpc_connect_interpret()` is the central decision point. On errors it wakes no-resend delayed requests, updates force-reconnect flags, deactivates on permanent access/version failures, schedules pinger retries, and leaves the import DISCON. On success it validates server connect data, negotiated flags, checksums, BRW sizes, mod-RPC limits, namespace flags, adaptive-timeout support, and version compatibility. It then chooses a recovery path based on connect reply flags: initial connect may go FULL or wait for server recovery; reconnect may enter REPLAY, REPLAY_LOCKS, RECOVER, EVICTED, or FULL depending on handles, recovery flags, invalid state, lightweight flags, and cached-data availability.

The recovery state machine replays committed and replay lists, replays LDLM locks, sends a replay-complete PING, waits for replay completion, resends pending requests, activates the import, and wakes delayed requests. Eviction launches a separate invalidation thread to avoid blocking the triggering task.

Disconnect uses a target-specific DISCONNECT opcode, sets no-resend and short timeout, then either sends async and completes on interpretation or directly closes/disconnects when already not FULL or forced. Idle disconnect sends a DISCONNECT only when the import has no resource holders beyond the disconnect request and no namespace lock references; a late reply can either move to IDLE or immediately reconnect if new requests appeared.

## State and persistence behavior
The import state is in-memory and guarded mostly by `imp_lock`. `import_set_state_nolock()` also maintains a ring history of states and timestamps and initializes replay substate on replay transitions. `imp_generation` invalidates old requests across disconnect/reconnect boundaries. Flags such as `IMPF_INVALID`, `IMPF_REPLAYABLE`, `IMPF_RESEND_REPLAY`, `IMPF_PINGABLE`, `IMPF_DEACTIVE`, `IMPF_CONNECT_TRIED`, and `IMPF_VBR_FAILED` coordinate recovery and retry behavior. Lists such as sending, delayed, committed, replay, unreplied, and connection lists are manipulated under lock. Adaptive timeout state keeps rolling bins, current timeout, and worst-ever timestamp in memory. No state survives module unload or client restart except through server recovery protocols and replayed transactions.

## Dependencies and integration points
This file integrates with PTLRPC request allocation/packing/queuing, ptlrpcd, the pinger, OBD reconnect/import events, LNet peer discovery, class import/export/connection references, LDLM namespace and lock replay, sptlrpc security adaptation and context flushing, SELinux policy packing, checksum negotiation, adaptive timeout code, failure-injection hooks, and Lustre console/debug logging. It exports key entry points for other client subsystems to initialize, deactivate, reconnect, disconnect, idle, and clean imports.

## Risks
- State transitions are highly concurrent: pinger, request callbacks, invalidation thread, disconnect, idle disconnect, and user-triggered reconnect can race.
- `ptlrpc_invalidate_import()` waits indefinitely in principle for inflight RPC completion; sluggish networks and long reply unlink paths are explicitly handled but operationally risky.
- Connect flag negotiation must reject unsupported server-granted features without breaking rolling upgrades.
- Replay ordering depends on committed/replay lists and known replied XID preparation; incorrect ordering risks transaction loss or duplicate replay.
- Server-handle changes distinguish recoverable failover from eviction; mistakes can either evict unnecessarily or retain invalid server state.
- Idle disconnect uses generation checks to handle late replies; incorrect generation updates can strand requests or reconnect unexpectedly.

## Test signals
Important coverage includes initial connect, reconnect after timeout, multi-NID failover selection, unreachable peers, access denied and protocol mismatch paths, checksum and BRW negotiation, server handle change with and without recovery flags, replay of committed/replay lists, LDLM lock replay, replay-complete failure, eviction invalidation thread, delayed/no-resend request wakeup, disconnect while recovering, async disconnect completion, idle disconnect races with new requests, adaptive-timeout bin rollover and bounds, and failure-injection points named in the code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/import.c -->

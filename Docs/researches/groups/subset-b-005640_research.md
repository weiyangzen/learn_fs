# Research: subset-b-005640

This grouped report covers the DLM source set under `sources/distributed-fs/ceph-client/fs/dlm/`. Each section preserves its source path for deterministic split into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/debug_fs.c -->
# sources/distributed-fs/ceph-client/fs/dlm/debug_fs.c

## Purpose
`debug_fs.c` exposes DLM lockspace and communication state through debugfs when `CONFIG_DLM_DEBUG` is enabled. It is not part of normal lock acquisition, but it is a critical observability and manual test surface for resource state (`rsb`), lock blocks (`lkb`), waiters, queued ASTs, and midcomms peer state. It also contains write paths that deliberately inject synthetic LKBs or waiters for debugging.

## Important APIs and Functions
- `dlm_register_debugfs()` and `dlm_unregister_debugfs()` create/remove the top-level `dlm` debugfs directory and `dlm/comms`.
- `dlm_create_debug_file()` creates per-lockspace files: `<ls>`, `<ls>_locks`, `<ls>_all`, `<ls>_toss`, and `<ls>_waiters`.
- `dlm_delete_debug_file()` removes the per-lockspace dentries recorded in `struct dlm_ls`.
- `dlm_create_debug_comms_file()` and `dlm_delete_debug_comms_file()` create per-peer files under `dlm/comms/<nodeid>/` for midcomms state, flags, send queue count, protocol version, and raw message injection.
- Four seq-file formats are implemented by `print_format1()` through `print_format4()` over lockspace `ls_slow_active` or `ls_slow_inactive` lists.
- `waiters_read()` dumps `ls_waiters`; `waiters_write()` injects a waiter using `dlm_debug_add_lkb_to_waiters()`.
- `table_write2()` parses a debug write to `<ls>_locks` and calls `dlm_debug_add_lkb()`.
- `dlm_rawmsg_write()` sends an arbitrary DLM header-bearing message to a midcomms peer via `dlm_midcomms_rawmsg_send()`.

## Control Flow
The per-lockspace seq files use `table_seq_start()`, `table_seq_next()`, and `table_seq_stop()` to hold `ls_rsbtbl_lock` while iterating a stable slow list. The selected `seq_operations` determines whether the active list or inactive toss list is walked and which printer runs. Each printer takes `res_lock` via `lock_rsb()` before reading resource queues, LVB state, recovery flags, and lookup lists.

Format 1 is human-oriented and groups granted, conversion, waiting, and lookup queues for each resource. Format 2 emits a compact lock-oriented line with lock ids, owner pid, xid for userspace locks, flags, modes, queue age, resource owner, and name. Format 3 is a fuller machine-readable resource plus lock dump, including LVB bytes and lookup entries. Format 4 targets inactive/tossed resources and includes master/dir/our node ids and toss time.

Debug write paths copy bounded user buffers, parse fixed fields with `sscanf()`, validate counts, then call lock-layer debug helpers. Waiter reads and writes coordinate with recovery by using `dlm_lock_recovery_try()`; if recovery cannot be read-locked they return `-EAGAIN`.

## State and Persistence Behavior
The file keeps global debugfs dentries in `dlm_root` and `dlm_comms`, and one static 4 KiB `debug_buf` protected by `debug_buf_lock` for waiter reads. Per-lockspace dentries live in `struct dlm_ls` fields declared in `dlm_internal.h`. All state is runtime-only; debugfs entries disappear with module/lockspace teardown. Synthetic LKBs inserted through debugfs enter the live lockspace xarray/resource queues and therefore affect runtime state until removed by normal or debug-driven paths.

## Dependencies and Integration Points
This file depends heavily on `dlm_internal.h` structures, `lock.h` queue locking helpers, `ast.h` for queued AST debug output, and `midcomms.h` for peer state/raw send hooks. It integrates with `lockspace.c` through per-lockspace create/delete calls and with `lock.c` through `dlm_debug_add_lkb()` and `dlm_debug_add_lkb_to_waiters()`.

## Risks
- Debug write interfaces mutate live DLM state and can create artificial LKBs or waiters. They are appropriate for fault injection but dangerous on production systems.
- Seq iteration holds `ls_rsbtbl_lock` while printers take `res_lock`; this matches local locking expectations but any future lock order change in `lock.c` could deadlock debug reads.
- Resource names are printed as strings in some formats; non-printable detection is present in formats 3 and 4 but format 2 emits `%s`, so binary names are less robust there.
- `dlm_rawmsg_write()` deliberately permits raw protocol injection up to one page and depends on debugfs permissions to limit misuse.

## Test Signals
- Mount debugfs and verify per-lockspace files appear after lockspace creation and disappear after release.
- Create locks in several modes and confirm `*_locks`, `*_all`, and the human-readable file show matching queues, ids, wait types, LVB flags, and AST state.
- Exercise recovery or forced waiter insertion and verify `<ls>_waiters` returns `-EAGAIN` while recovery is exclusively blocking operations.
- Use fault-injection tests for `table_write2()` and `waiters_write()` parse failures: malformed input should return `-EINVAL`, inaccessible user buffers should return `-EFAULT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/debug_fs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/dir.c -->
# sources/distributed-fs/ceph-client/fs/dlm/dir.c

## Purpose
`dir.c` implements the DLM resource directory: mapping a resource-name hash to a directory node, recovering directory records after membership changes, and serving batched lists of resource names mastered by the local node. The directory lets non-master nodes discover the current master node for a resource without broadcasting every lookup.

## Important APIs and Functions
- `dlm_hash2nodeid()` maps a jhash value to a node id using `ls_total_weight` and `ls_node_array`; single-node lockspaces short-circuit to `dlm_our_nodeid()`.
- `dlm_dir_nodeid()` returns `r->res_dir_nodeid`.
- `dlm_recover_dir_nodeid()` recomputes directory ownership for each RSB in a recovery root list.
- `dlm_recover_directory()` queries every other member for master resource names, then calls `dlm_master_lookup(..., DLM_LU_RECOVER_DIR, ...)` to rebuild local directory records.
- `dlm_copy_master_names()` services remote `DLM_RCOM_NAMES` requests by copying name-length/name records for resources mastered locally and whose directory node is the requester.
- The private `struct dlm_dir_dump` tracks a multi-message dump cursor and sanity information while a requester pages through names.

## Control Flow
Normal resource lookup starts outside this file in `lock.c`: a name is hashed, `dlm_hash2nodeid()` selects the directory node, and a lookup message is sent if the local RSB does not already know the master. During recovery, `dlm_recover_directory()` loops over members, asks each for names after the last returned name, parses `__be16` length prefixes from `ls_recover_buf`, and terminates on either zero-length end-of-buffer or `0xFFFF` end-of-node sentinel. Each received name is reconciled through `dlm_master_lookup()` using the sender as the asserted master.

`dlm_copy_master_names()` walks `ls_masters_list` under `ls_masters_lock`. For a fresh dump it allocates a `dlm_dir_dump` context, records the current recovery sequence, and starts at the head of the masters list. For a continuation it finds the previous RSB by name and resumes after its `res_masters_list` entry. It emits records until the output buffer lacks room for another name plus a terminator, then writes a zero-length marker; at end of list it writes `0xFFFF`, logs counts, removes the dump context, and frees it.

## State and Persistence Behavior
Directory state is kept in each RSB (`res_dir_nodeid`, `res_master_nodeid`, `res_masters_list`) and in the lockspace dump list (`ls_dir_dump_list`). It is not persistent across module unload or lockspace destruction. During recovery the directory is reconstructed from live peer state, using `ls_recover_seq` to detect stale continuation requests. The dump context is per requester node and is dropped/replaced if the same node starts another dump before finishing.

## Dependencies and Integration Points
`dir.c` depends on membership (`member.h`), recovery communication (`rcom.h`), low/mid communication state, config, recovery status helpers, and `lock.c` master lookup/search functions. It is called by recovery orchestration to rebuild directory ownership and by RCOM handlers to fill `DLM_RCOM_NAMES_REPLY` payloads.

## Risks
- Directory recovery trusts remote name dumps enough to create or update local directory records, so length validation and sentinel parsing are essential. The code checks buffer bounds and `DLM_RESNAME_MAXLEN`.
- `find_rsb_root()` falls back from rhashtable lookup to `ls_masters_list`; this covers recovery races but means stale list membership would affect dump continuation.
- Multi-message dump cursors are keyed only by requester node; overlapping dumps from the same node intentionally drop the older context.
- The weighted node array must be correctly built by membership code. A bad `ls_total_weight`/`ls_node_array` relationship would misplace directory ownership.

## Test Signals
- Unit-style recovery tests should verify hash-to-node stability for single-node and weighted multi-node lockspaces.
- Recovery tests can force resource masters on several nodes and confirm `dlm_recover_directory()` adds missing directory records and logs mismatched masters.
- RCOM name dump tests should cover exact-buffer-fit, continuation, zero-length block terminator, and `0xFFFF` final terminator behavior.
- Fault tests should inject oversized or truncated name records and expect `-EINVAL` recovery failure rather than out-of-bounds parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/dir.h -->
# sources/distributed-fs/ceph-client/fs/dlm/dir.h

## Purpose
`dir.h` declares the small public interface for DLM directory ownership and directory recovery. It separates directory mapping/name-copy routines from `lock.c`, `recover.c`, and RCOM handlers.

## Important APIs
- `dlm_dir_nodeid(struct dlm_rsb *rsb)` returns the directory node id stored in an RSB.
- `dlm_hash2nodeid(struct dlm_ls *ls, uint32_t hash)` maps a resource hash to a node id using the lockspace membership map.
- `dlm_recover_dir_nodeid(struct dlm_ls *ls, const struct list_head *root_list)` recomputes directory node ids for a list of root resources.
- `dlm_recover_directory(struct dlm_ls *ls, uint64_t seq)` rebuilds local directory records from peer master-name dumps during recovery.
- `dlm_copy_master_names(...)` fills an output buffer with length-prefixed names mastered locally for a requesting directory node.

## Control Flow and State
The header itself has no state. Its declarations expose the directory lifecycle: hash mapping during resource lookup, recomputation during recovery, and name dump serving for remote recovery requests. All persistent runtime state remains in `struct dlm_rsb` and `struct dlm_ls`.

## Dependencies and Integration Points
Consumers must already see `struct dlm_ls`, `struct dlm_rsb`, and Linux list types, normally through `dlm_internal.h`. `lock.c` uses the mapping helpers during `find_rsb()` and master lookup. Recovery code and RCOM handling use the directory rebuild/name-copy functions.

## Risks
- The API exposes raw buffers and lengths for `dlm_copy_master_names()`, so callers must pass valid RCOM payload storage and matching buffer lengths.
- Hash mapping depends on lockspace membership fields being initialized before use.

## Test Signals
- Compile coverage should ensure all users include `dlm_internal.h` before `dir.h`.
- Recovery tests should verify each declared function is exercised through directory-enabled lockspaces and skipped or altered appropriately when `LSFL_NODIR` is set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/dir.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/dlm_internal.h -->
# sources/distributed-fs/ceph-client/fs/dlm/dlm_internal.h

## Purpose
`dlm_internal.h` is the central private header for the DLM implementation. It defines logging helpers, lockspace membership and recovery structures, lock block (`dlm_lkb`) state, resource block (`dlm_rsb`) state, wire protocol structures, lockspace-wide state (`dlm_ls`), flag conversion helpers, and debugfs stubs.

## Important Types and Constants
- `struct dlm_member` records member node id, weight, slot, communication sequence, and generation.
- `struct dlm_recover` carries recovery node configuration and sequence data.
- `struct dlm_args` is an internal normalized argument package passed from public lock/unlock entry points to lower stages.
- `struct dlm_user_args` and `struct dlm_callback` connect userspace lock requests with completion and blocking AST delivery.
- `struct dlm_lkb` is the lock block. It stores resource pointer, refcount, local and remote ids, external flags, status-block flags, distributed/internal flags, modes, wait state, queue links, callback state, recovery sequence, LVB pointer, and caller/user callback data.
- `struct dlm_rsb` is the resource block. It stores lockspace pointer, refcount, spinlock, resource name/hash, master and directory node ids, LVB state, lookup/grant/convert/wait queues, slow-list/scan/recovery/list membership, and recovery counters.
- `struct dlm_header`, `struct dlm_message`, `struct dlm_rcom`, `struct dlm_opts`, and `union dlm_packet` define the on-wire DLM message, recovery communication, option, and common header formats.
- `struct rcom_status`, `struct rcom_config`, `struct rcom_slot`, and `struct rcom_lock` define RCOM payloads.
- `struct dlm_ls` is the lockspace object and owns the global id, local flags, LKB xarray, RSB rhashtable and slow lists, scan timer, waiters/orphans, membership lists, slots, debugfs dentries, uevent/recovery state, request queue, recovery buffers, master/directory dump lists, callbacks, miscdevice, and lockspace name.

## Control Flow Role
This header does not implement the main algorithms, but it defines the state machine vocabulary consumed throughout the DLM:
- LKB status values distinguish waiting, granted, and converting queues.
- Internal flags track master copies, resend after recovery, dead/end-of-life locks, overlap unlock/cancel, and deadlock cancellation.
- RSB flags track uncertain masters, invalid LVBs, new masters, recovery grant/convert/LVB invalidation state, inactive state, and rhashtable membership.
- LS flags coordinate recovery stop/down/lock/work/running state, RCOM wait readiness, uevent wait, callback delay, no-directory mode, receive blocking, filesystem lockspace mode, and softirq behavior.

## State and Persistence Behavior
All definitions describe in-memory kernel state. There is no disk persistence here. Runtime persistence across membership changes is achieved by recovery protocols: RSBs/LKBs are rebuilt from surviving nodes, directory records are reconstructed, and waiter state is resent or locally completed. The `dlm_ls` object is the root lifetime owner; `lockspace.c` allocates it and `lock.c`, recovery, user, and communication modules mutate the embedded tables and lists.

## Dependencies and Integration Points
The header imports kernel infrastructure including xarrays, rhashtables, kobjects, misc devices, krefs, rwsems, workqueues, spinlocks, and user access types. It also imports UAPI DLM definitions from `<linux/dlm.h>` and `<uapi/linux/dlm_device.h>`. Almost every DLM source file includes this header; its layout is therefore a cross-module ABI within the kernel DLM implementation.

## Risks
- Many fields are protected by different locks (`res_lock`, `ls_rsbtbl_lock`, `ls_lkbxa_lock`, `ls_waiters_lock`, recovery locks). Misidentifying the owner lock for a field can introduce races or deadlocks.
- The distinction between `res_nodeid` and `res_master_nodeid` is explicitly called "odd" and slated for cleanup. Code must preserve the current semantics: `res_nodeid == 0` means local master, while `res_master_nodeid` stores the real node id.
- Wire structures use fixed endian annotations and flexible payloads. Any size/layout change must preserve protocol compatibility.
- Inline flag snapshot/set helpers assume contiguous min/max bit ranges and are used for message serialization and debug output.

## Test Signals
- Build tests with `CONFIG_DLM` and `CONFIG_DLM_DEBUG` should catch declaration drift.
- Sparse/endian checking is valuable for `__le*`/`__be*` protocol fields.
- Lockdep should cover common lock ordering involving `res_lock`, `ls_rsbtbl_lock`, waiters, and recovery rwsems.
- Recovery and mixed user/kernel lock tests should validate distributed flag serialization through `dlm_dflags_val()` and `dlm_set_dflags_val()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/dlm_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/lock.c -->
# sources/distributed-fs/ceph-client/fs/dlm/lock.c

## Purpose
`lock.c` is the core DLM lock manager implementation. It handles public kernel lock/unlock calls, userspace lock operations, resource lookup and master discovery, local queue manipulation, remote wire-message send/receive paths, lock value block transfer, blocking/completion AST queueing, waiter tracking, and major pieces of post-membership-change recovery.

## Important APIs and Functions
- Public kernel APIs: `dlm_lock()` and `dlm_unlock()`.
- Userspace APIs used by device/user code: `dlm_user_request()`, `dlm_user_convert()`, `dlm_user_adopt_orphan()`, `dlm_user_unlock()`, `dlm_user_cancel()`, `dlm_user_deadlock()`, `dlm_user_purge()`, and `dlm_clear_proc_locks()`.
- Resource and lock lifetime helpers: `find_rsb()`, `find_rsb_dir()`, `find_rsb_nodir()`, `dlm_search_rsb_tree()`, `rsb_insert()`, `deactivate_rsb()`, `free_inactive_rsb()`, `create_lkb()`, `find_lkb()`, `dlm_put_lkb()`, `attach_lkb()`, and `detach_lkb()`.
- Queue/grant logic: `can_be_granted()`, `_can_be_granted()`, `conversion_deadlock_detect()`, `grant_pending_locks()`, `grant_pending_convert()`, `grant_pending_wait()`, `queue_cast()`, and `queue_bast()`.
- Four-stage operation pipeline: `request_lock()`/`convert_lock()`/`unlock_lock()`/`cancel_lock()`, then `_request_lock()`/`_convert_lock()`/`_unlock_lock()`/`_cancel_lock()`, then `do_request()`/`do_convert()`/`do_unlock()`/`do_cancel()`.
- Message send/receive: `send_request()`, `send_convert()`, `send_unlock()`, `send_cancel()`, `send_grant()`, `send_bast()`, `send_lookup()`, `send_remove()`, corresponding `receive_*()` handlers, `dlm_receive_buffer()`, and `dlm_receive_message_saved()`.
- Recovery hooks: `dlm_recover_waiters_pre()`, `dlm_recover_waiters_post()`, `dlm_recover_purge()`, `dlm_recover_grant()`, `dlm_recover_master_copy()`, and `dlm_recover_process_copy()`.
- Debug hooks: `dlm_debug_add_lkb()` and `dlm_debug_add_lkb_to_waiters()`.

## Control Flow
The file documents its own four-stage model. Stage 1 validates public entry-point arguments and chooses request, convert, unlock, or cancel. Stage 2 finds the target RSB and locks it. Stage 3 decides local-vs-remote based on `res_nodeid`. Stage 4 performs queue mutations and queues callbacks. For remote operations, the local stage sends a DLM message and waits for the corresponding reply; the remote receiver runs the same stage-4 logic on a master-copy LKB and replies.

Resource lookup uses `jhash()` of the resource name and `dlm_hash2nodeid()` to determine the directory node. With directories enabled, `find_rsb_dir()` may create an RSB, reactivate an inactive RSB, preserve a directory record, mark a stale master as uncertain, or return `-ENOTBLK` when a request reached a non-master. Without directories, `find_rsb_nodir()` maps the hash directly to the master. Master lookup messages are serialized through `set_master()`: the first LKB triggering a lookup waits on `ls_waiters`, while additional LKBs for the same unresolved RSB wait on `res_lookup`.

Grant decisions are driven by VMS-style compatibility matrices and queue ordering. `do_request()` grants immediately, queues on the wait queue, or returns noqueue failure. `do_convert()` handles immediate grant, conversion queueing, conversion deadlock detection/demotion, and noqueue failure. Unlock removes a lock and then grants newly unblocked locks. Cancel reverts a converting/waiting lock and may also unblock others. Blocking ASTs are sent to granted locks whose modes block queued requests.

Messaging builds `struct dlm_message` payloads through `_create_message()`, `create_message()`, and `send_args()`, using midcomms message handles. Receive paths validate lock identity and copy type, deserialize flags/LVBs, run local queue operations, and send replies. `receive_lookup()` can optimize lookup into a request when the directory node is also the master.

## State and Persistence Behavior
The central runtime state is `struct dlm_ls` containing an LKB xarray, RSB rhashtable, active/inactive slow lists, waiters list, orphan list, request queue, and recovery structures. RSBs are refcounted while active; when their refcount drops, `deactivate_rsb()` moves them to the inactive list and optionally the scan list. The scan timer later frees tossable inactive resources and sends `DLM_MSG_REMOVE` to a directory node when needed.

LKBs are refcounted through the lockspace xarray and through queue/list ownership. Adding an LKB to a resource queue takes a reference; deleting it drops that reference. Waiters also hold references while replies are outstanding. Userspace locks add a process-list reference; persistent locks can move to the lockspace orphan list.

LVB state is held per resource (`res_lvbptr`, `res_lvbseq`, invalid flags) and per lock (`lkb_lvbptr`, `lkb_lvbseq`). `set_lvb_lock()`, `set_lvb_unlock()`, and `set_lvb_lock_pc()` implement direction-specific copy/invalidate behavior based on the old and requested lock modes.

There is no durable storage. Membership changes trigger recovery: waiters are completed or flagged for resend, dead-node master-copy locks are purged, locks are rebuilt on new masters via RCOM, process copies learn new remote ids, and pending queues are retried.

## Dependencies and Integration Points
`lock.c` integrates with midcomms for DLM messages, RCOM/recovery code for master-copy rebuild, `dir.c` for hash-to-directory mapping, `member.c` for membership/removal checks, `requestqueue.c` for saving messages during recovery, `ast.c` for callbacks, `user.c` for userspace lock ownership, `memory.c` for object allocation, `lvb_table.h` for LVB sizing, and `lockspace.c` for lockspace lifecycle.

## Risks
- The code is lock-order sensitive. It mixes `res_lock`, `ls_rsbtbl_lock`, `ls_lkbxa_lock`, waiters lock, requestqueue lock, scan lock, and recovery semaphores.
- Remote reply and overlap handling is subtle: force-unlock/cancel can overlap request/convert and must correctly clear waiter counts and flags.
- `res_nodeid` and `res_master_nodeid` have different semantics; stale or partially recovered master state can cause retry loops, `-ENOTBLK`, or incorrect local/remote decisions.
- Conversion deadlock, alternate-mode grant, and LVB invalidation rules are behaviorally dense and easy to regress with queue changes.
- Recovery paths intentionally synthesize local replies and forcibly reset waiter refcounts. Refcount mistakes can leak or prematurely free LKBs.
- Debug helpers can create artificial state and should not be treated as safe production input paths.

## Test Signals
- Lock mode compatibility tests should cover all matrix entries, conversions, `QUECVT`, `NOQUEUE`, `EXPEDITE`, `ALTPR`, `ALTCW`, and `CONVDEADLK`.
- Multi-node tests should cover remote request/convert/unlock/cancel, async grant, BAST delivery, lookup-to-request optimization, and directory remove races.
- Recovery tests should kill a master with pending requests, conversions, unlocks, cancels, and lookups, then verify waiter resend/completion and RCOM remid repair.
- LVB tests should cover VALBLK and IVVALBLK on lock, convert, unlock, remote reply, and failed holder recovery.
- Userspace tests should cover persistent orphan adoption, purge, process close cleanup, deadlock cancel, and mixed user/kernel lock rejection.
- Lockdep/KCSAN-style stress is important around scan timer reactivation, inactive RSB reuse, and requestqueue blocking during recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/lock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/lock.h -->
# sources/distributed-fs/ceph-client/fs/dlm/lock.h

## Purpose
`lock.h` declares the internal lock-manager API exported from `lock.c` to the rest of the DLM subsystem. It also provides small inline helpers for master detection and RSB spin locking.

## Important APIs
- Debug/inspection: `dlm_dump_rsb()`, `dlm_dump_rsb_name()`, `dlm_print_lkb()`.
- Receive entry points: `dlm_receive_message_saved()` and `dlm_receive_buffer()`.
- Mode and resource helpers: `dlm_modes_compat()`, `dlm_search_rsb_tree()`, `dlm_master_lookup()`.
- Lifetime and recovery locking: `free_inactive_rsb()`, `dlm_put_rsb()`, `dlm_hold_rsb()`, `dlm_put_lkb()`, `dlm_lock_recovery_try()`, `dlm_lock_recovery()`, `dlm_unlock_recovery()`, `dlm_rsb_scan()`, `resume_scan_timer()`.
- Recovery hooks: `dlm_recover_purge()`, `dlm_purge_mstcpy_locks()`, `dlm_recover_grant()`, `dlm_recover_waiters_pre()`, `dlm_recover_waiters_post()`, `dlm_recover_master_copy()`, and `dlm_recover_process_copy()`.
- Userspace lock operations: `dlm_user_request()`, `dlm_user_convert()`, `dlm_user_adopt_orphan()`, `dlm_user_unlock()`, `dlm_user_cancel()`, `dlm_user_purge()`, `dlm_user_deadlock()`, and `dlm_clear_proc_locks()`.
- Debug mutation hooks: `dlm_debug_add_lkb()` and `dlm_debug_add_lkb_to_waiters()`.
- Inline helpers: `is_master()`, `lock_rsb()`, and `unlock_rsb()`.

## Control Flow and State
The header is a cross-module contract. Recovery, midcomms, debugfs, lockspace, and user-device code call these functions to enter the lock manager without needing the full private implementation. `is_master()` encodes the local convention that `res_nodeid == 0` means the local node is master, and warns on unresolved `-1` master state.

## Dependencies and Integration Points
Consumers need `struct dlm_ls`, `struct dlm_rsb`, `struct dlm_lkb`, `struct dlm_message`, and `struct dlm_rcom` from `dlm_internal.h`. The function set bridges `lock.c` with `dir.c`, `recover.c`, `recoverd.c`, `debug_fs.c`, `user.c`, and communication receive paths.

## Risks
- Inline `is_master()` relies on `res_nodeid` semantics rather than `res_master_nodeid`; callers must not use it on unresolved RSBs.
- Exposing many recovery hooks increases coupling: changes to lock recovery state must update all users and tests.
- `lock_rsb()`/`unlock_rsb()` use bottom-half disabling spin locks, so callers must respect kernel context constraints.

## Test Signals
- Build coverage with all DLM modules enabled catches declaration drift.
- Recovery and debugfs tests should exercise every non-static function declared here.
- Lockdep should validate caller lock contexts around `lock_rsb()` and recovery lock wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/lock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/lockspace.c -->
# sources/distributed-fs/ceph-client/fs/dlm/lockspace.c

## Purpose
`lockspace.c` owns DLM lockspace lifecycle. It creates and destroys `struct dlm_ls`, exposes lockspace sysfs attributes, coordinates userland `dlm_controld` join/leave handshakes through kobject uevents, starts/stops communication and recovery threads, registers per-lockspace devices/debugfs files, and releases all per-lockspace memory.

## Important APIs and Functions
- Module lifecycle: `dlm_lockspace_init()` creates the `dlm` kset; `dlm_lockspace_exit()` unregisters it.
- Lookup/refcount APIs: `dlm_find_lockspace_global()`, `dlm_find_lockspace_local()`, `dlm_find_lockspace_device()`, and `dlm_put_lockspace()`.
- Creation APIs: `dlm_new_lockspace()` for kernel/filesystem users and `dlm_new_user_lockspace()` for userspace lockspaces, both funneled through `__dlm_new_lockspace()` and `new_lockspace()`.
- Release APIs: `dlm_release_lockspace()` and private `release_lockspace()`.
- Emergency control: `dlm_stop_lockspaces()` stops running lockspaces when userland control disappears.
- Sysfs attribute handlers: `control`, `event_done`, `id`, `nodir`, `recover_status`, and `recover_nodeid`.
- Cleanup helpers: `free_lockspace()`, `remove_lockspace()`, `lockspace_busy()`, `lkb_idr_free()`, and `rhash_free_rsb()`.

## Control Flow
Initialization sets up a global lockspace list guarded by `lslist_lock`, a create/release mutex `ls_lock`, and a kset with uevent operations. Creating the first lockspace starts midcomms. `new_lockspace()` validates names/LVB length/cluster compatibility, reuses an existing lockspace unless `DLM_LSFL_NEWEXCL` forbids it, allocates `struct dlm_ls`, initializes every embedded list/lock/table/timer/waitqueue, starts callback and recovery threads, waits for recoverd to hold the initial recovery lock, adds the kobject, emits an online uevent, waits for userland to configure membership and start recovery, waits for recovery completion, then creates debugfs files.

Releasing checks whether the lockspace is busy according to the requested release mode, removes the create reference or decrements shared create count, deregisters the device, optionally emits an offline uevent, stops recoverd, shuts down scan timer/callbacks/midcomms as needed, removes the lockspace from the global list, deletes debugfs files, drops the kobject, destroys recovery/request/membership state, queues delayed memory freeing, and drops the module reference.

Sysfs `control` calls `dlm_ls_stop()` or `dlm_ls_start()` after taking a lockspace reference. `event_done` stores the userland result and wakes the join/leave waiter. `nodir` can set `LSFL_NODIR`; `id` sets the global lockspace id used in wire headers.

## State and Persistence Behavior
Global state consists of `ls_count`, `ls_lock`, `lslist`, `lslist_lock`, and `dlm_kset`. Per-lockspace state is allocated dynamically and lives until release plus delayed `free_lockspace()` work. There is no disk persistence. Membership and recovery state are rebuilt on each join/recovery cycle from userland configuration and peer communication. `ls_create_count` tracks shared open/create references separately from `ls_count`, which protects active users of an `ls` pointer.

## Dependencies and Integration Points
`lockspace.c` depends on module refs, kobjects/sysfs/uevents, midcomms, recoverd, member/config management, request queue cleanup, user daemon availability, callback workqueues, debugfs creation, lock scanning, and device registration. It is the bridge between in-kernel DLM users, userspace `dlm_controld`, and the lower lock/recovery/message layers.

## Risks
- Creation has many initialized resources with many error labels; unwind order must match initialization order exactly.
- Join/release waits depend on userland writing `event_done`. A missing or wedged control daemon blocks progress unless higher-level handling stops lockspaces.
- `lockspace_busy()` checks the LKB xarray rather than RSB table because AST-pending locks may already be detached from resources; release behavior can surprise callers expecting only granted locks to matter.
- Shared create references (`ls_create_count`) and active pointer refs (`ls_count`) are separate; bugs in either can leak lockspaces or free them while still reachable.
- The first/last lockspace controls global midcomms startup/shutdown, making races around `ls_count` particularly sensitive.

## Test Signals
- Create/release tests should cover first lockspace, additional shared lockspace, `DLM_LSFL_NEWEXCL`, invalid names, invalid LVB lengths, cluster mismatch, and user daemon absence.
- Sysfs tests should verify `control`, `event_done`, `id`, `nodir`, and recovery status/node fields.
- Failure-injection tests should target allocation or thread-start failures in `new_lockspace()` and verify no kobjects, xarrays, rhashtables, timers, or module refs leak.
- Release tests should cover `DLM_RELEASE_NO_LOCKS`, `DLM_RELEASE_UNUSED`, `DLM_RELEASE_FORCE`, `DLM_RELEASE_NO_EVENT`, and `DLM_RELEASE_RECOVER`.
- Integration tests should confirm debugfs files and misc devices are created after successful recovery and removed during release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/lockspace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/lockspace.h -->
# sources/distributed-fs/ceph-client/fs/dlm/lockspace.h

## Purpose
`lockspace.h` declares the lockspace lifecycle and lookup API used outside `lockspace.c`. It is the narrow contract for creating, finding, releasing references to, and stopping DLM lockspaces.

## Important APIs
- `DLM_LSFL_FS` marks a kernel/filesystem lockspace and enables direct BAST/CAST callbacks through `LSFL_FS`.
- `dlm_lockspace_init()` and `dlm_lockspace_exit()` manage global lockspace subsystem setup.
- `dlm_find_lockspace_global()`, `dlm_find_lockspace_local()`, and `dlm_find_lockspace_device()` acquire active references by global id, opaque local pointer, or miscdevice minor.
- `dlm_put_lockspace()` releases a reference acquired by the find helpers.
- `dlm_stop_lockspaces()` stops running lockspaces when userland control is unavailable.
- `dlm_new_user_lockspace()` creates a userspace-facing lockspace. Kernel callers use the corresponding public API implemented in `lockspace.c`/DLM core, while this header exposes the user variant to internal user-device code.

## Control Flow and State
The header has no state. Its functions operate on `struct dlm_ls` and the global lockspace list maintained by `lockspace.c`. The `DLM_LSFL_FS` comment documents that the flag is internal and expected to be removed later, so consumers should avoid expanding its use.

## Dependencies and Integration Points
Consumers must have DLM types and `struct dlm_lockspace_ops` available from public/private DLM headers. The declarations are used by lock, user, recovery, and module lifecycle code to coordinate lockspace references and creation.

## Risks
- `dlm_find_lockspace_local()` treats an opaque `dlm_lockspace_t *` as `struct dlm_ls *`; callers must only pass valid live lockspace handles.
- The reference discipline is manual: every successful find must be matched by `dlm_put_lockspace()`.
- `DLM_LSFL_FS` is internal but still defined in a shared header, which can encourage coupling to a flag planned for removal.

## Test Signals
- Build tests should catch signature drift between `lockspace.h` and `lockspace.c`.
- Refcount tests should pair find/put calls under create/release concurrency.
- User lockspace creation tests should confirm `DLM_LSFL_SOFTIRQ` is rejected for user lockspaces while filesystem lockspaces can set FS behavior through the kernel creation path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/lockspace.h -->

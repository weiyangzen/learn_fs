# Group Research: group_730_linux_sources_os_linux_linux_fs_dlm_debug_fs_c_sources_os_linux_linu_43bd2e5ebcc7

Scope: `Docs/research_subset_a.md`, source tree `sources/os/linux/linux`.

This group covers the Linux kernel Distributed Lock Manager core files for lockspace lifetime, resource directory ownership, lock/request state machines, wire-message handling, recovery integration, and debugfs visibility. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/dlm/debug_fs.c -->
# File Research: sources/os/linux/linux/fs/dlm/debug_fs.c

## Role

`debug_fs.c` implements DLM debugfs surfaces under `/sys/kernel/debug/dlm`. It exposes per-lockspace lock/resource snapshots, waiter lists, inactive/tossed resource records, and midcomms per-node state. It is compiled behind `CONFIG_DLM_DEBUG`; `dlm_internal.h` provides no-op inline stubs when debug support is disabled.

## Main Interfaces

- `dlm_register_debugfs()` initializes `debug_buf_lock` and creates the top-level `dlm` and `dlm/comms` debugfs directories.
- `dlm_unregister_debugfs()` removes the top-level tree.
- `dlm_create_debug_file(struct dlm_ls *ls)` creates per-lockspace files: readable RSB dump, compact locks table, full active-resource dump, inactive/toss list, and waiters list.
- `dlm_delete_debug_file(struct dlm_ls *ls)` removes all per-lockspace debugfs dentries.
- `dlm_create_debug_comms_file(int nodeid, void *data)` creates `dlm/comms/<nodeid>/` files for midcomms state, flags, send queue count, protocol version, and raw message injection.
- `dlm_delete_debug_comms_file(void *ctx)` removes a per-node comms directory.

## Resource Dump Formats

The file implements four seq_file formats over lockspace slow lists:

- Format 1: readable active resource dump with name, master state, LVB, recovery-list state, and granted/convert/waiting/lookup queues.
- Format 2: compact row per active lock with ids, node info, pid, user xid, flags, status, modes, queue age, and resource name.
- Format 3: detailed active RSB rows, optional LVB bytes, and LKB rows including callback history and timestamps.
- Format 4: inactive/tossed RSB rows from `ls_slow_inactive`.

The shared sequence iterator holds `ls_rsbtbl_lock` while walking slow lists and locks each RSB with `lock_rsb()` while formatting detailed resource contents.

## Debug Mutation Paths

`<ls_name>_locks` is writable and calls `dlm_debug_add_lkb()` after parsing a synthetic lock record. `<ls_name>_waiters` is writable and calls `dlm_debug_add_lkb_to_waiters()` after taking the recovery read lock. These are debug-only hooks into live lock-manager state.

## Waiters and Shared Buffer Handling

`waiters_read()` uses a global 4096-byte `debug_buf` protected by `debug_buf_lock`. It returns `-EAGAIN` if it cannot take the recovery read lock. Output is truncated at buffer size, which is acceptable for debugfs but relevant for tooling.

## Midcomms Debugfs

The per-node comms directory exposes `state`, `flags`, `send_queue_count`, `version`, and write-only `rawmsg`. `rawmsg` accepts payloads between `sizeof(struct dlm_header)` and `PAGE_SIZE`, copies from userspace into a page allocation, and delegates sending to midcomms.

## Research Notes

`debug_fs.c` is observability-first but not read-only. It includes synthetic LKB and waiter insertion hooks used for testing and recovery debugging, so readers should treat writable debugfs paths as privileged state mutation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/dlm/debug_fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/dlm/dir.c -->
# File Research: sources/os/linux/linux/fs/dlm/dir.c

## Role

`dir.c` implements the DLM resource directory. The directory maps a resource name hash to the node responsible for answering which node masters that resource. It also rebuilds directory records during recovery by exchanging resource names between members.

## Directory Node Selection

`dlm_hash2nodeid()` chooses the directory node. Single-node lockspaces use `dlm_our_nodeid()`. Multi-node lockspaces use the upper 16 bits of the resource hash modulo `ls_total_weight` as an index into `ls_node_array`.

`dlm_dir_nodeid()` returns `res_dir_nodeid`. `dlm_recover_dir_nodeid()` recomputes `res_dir_nodeid` for each RSB in a recovery root list after membership changes.

## Directory Recovery

`dlm_recover_directory()` rebuilds local directory records by asking each other current member for names it masters and for which this node is directory owner. It repeatedly calls `dlm_rcom_names()`, parses `namelen/name` records from `ls_recover_buf`, treats `0` as end of chunk and `0xFFFF` as end of dump, and calls `dlm_master_lookup(..., DLM_LU_RECOVER_DIR, ...)` for each name.

The parser bounds-checks against remaining buffer length and `DLM_RESNAME_MAXLEN`. It aborts with `-EINTR` if recovery is stopped and marks `DLM_RS_DIR` when complete.

## Master Name Dump Context

Remote nodes serve recovery requests using `dlm_copy_master_names()`. Multi-message dumps are tracked by `struct dlm_dir_dump`, which stores the initial recovery sequence, requester nodeid, last list pointer, and sent resource/message counts. Contexts live on `ls_dir_dump_list` under `ls_dir_dump_lock`.

`dlm_copy_master_names()` writes zero-length records for end-of-block and `0xFFFF` for end-of-dump. It validates that the saved context still matches the current recovery sequence and last list node before resuming.

## Resource Lookup for Resume

`find_rsb_root()` first searches the RSB rhashtable via `dlm_search_rsb_tree()`. If not found, it scans `ls_masters_list` directly as a recovery/dump fallback.

## Research Notes

The directory protocol is cursor-based and restart-aware. It is designed to survive chunked transfers while detecting stale continuation after aborted or restarted recovery.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/dlm/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/dlm/dir.h -->
# File Research: sources/os/linux/linux/fs/dlm/dir.h

## Role

`dir.h` is the internal header for the DLM resource-directory implementation.

## Exposed Functions

- `dlm_dir_nodeid(struct dlm_rsb *rsb)`: returns cached directory owner.
- `dlm_hash2nodeid(struct dlm_ls *ls, uint32_t hash)`: maps resource hash to nodeid.
- `dlm_recover_dir_nodeid(struct dlm_ls *ls, const struct list_head *root_list)`: recomputes directory owners during recovery.
- `dlm_recover_directory(struct dlm_ls *ls, uint64_t seq)`: rebuilds directory entries.
- `dlm_copy_master_names(...)`: fills an RCOM response buffer with locally mastered names for a requesting directory node.

## Research Notes

The boundary is clean: directory internals and dump contexts remain private to `dir.c`; other files only see mapping and recovery entry points.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/dlm/dir.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/dlm/dlm_internal.h -->
# File Research: sources/os/linux/linux/fs/dlm/dlm_internal.h

## Role

`dlm_internal.h` is the central private DLM header. It defines the lockspace, resource, lock, message, recovery, callback, and userspace-process structures shared across `fs/dlm`.

## Core Types

`struct dlm_lkb` is the lock block. It stores resource pointer, refcount, local/remote ids, owner node semantics, external/internal/distributed/status flags, LVB sequence, queue status, requested/granted modes, waiter state, callback state, timestamps, and either kernel AST parameter or userspace args.

`struct dlm_rsb` is the resource block. It stores lockspace pointer, refcount, resource spinlock, name/hash, master/directory nodeids, legacy `res_nodeid`, grant/convert/wait/lookup queues, active/inactive slow-list links, recovery links, LVB data, toss time, and RSB flags.

`struct dlm_ls` is the lockspace object. It owns identity, refcounts, kobject/miscdevice state, LKB xarray, RSB rhashtable, active/inactive lists, scan timer, waiters, orphans, members, debugfs dentries, user/recovery wait queues, callback worker state, recovery request queues, master lists, directory dump contexts, optional callbacks, and local fake message state.

## Protocol Structures

The header defines the DLM wire layout: `struct dlm_header`, `struct dlm_message`, `struct dlm_rcom`, `struct dlm_opts`, and `union dlm_packet`. It also defines message ids, recovery communication ids, status flags, version constants, and RCOM payload structures.

## Important Invariants

- LKBs may be local copies, process copies, or master copies.
- RSB `res_nodeid` uses `-1` for unknown, `0` for local master, and positive values for remote master.
- RSB flags track master uncertainty, LVB validity, recovery grant/conversion state, inactivity, and rhashtable membership.
- `ls_in_recovery`, `ls_recv_active`, and `LSFL_*` flags coordinate normal locking with recovery.

## Inline Helpers

The header provides helpers for RSB flags, lockspace stopped/no-directory checks, and conversion between atomic bitfields and wire-visible integer flag values: `dlm_iflags_val()`, `dlm_dflags_val()`, `dlm_sbflags_val()`, `dlm_set_dflags_val()`, and `dlm_set_sbflags_val()`.

## Research Notes

This header is the DLM internal contract. The highest-value reading points are the three LKB copy types, the dual RSB nodeid model, queue ownership under `res_lock`, and lockspace-wide indexes under `ls_lkbxa_lock` and `ls_rsbtbl_lock`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/dlm/dlm_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/dlm/lock.c -->
# File Research: sources/os/linux/linux/fs/dlm/lock.c

## Role

`lock.c` is the DLM behavioral core. It implements lock/request state machines, RSB/LKB lookup and lifetime, compatibility rules, LVB propagation, inter-node message send/receive, recovery reconciliation, userspace lock operations, orphan/purge handling, and debug injection helpers.

## Locking Pipeline

The file documents four stages:

1. `dlm_lock()` / `dlm_unlock()` split public calls into request, convert, unlock, or cancel.
2. `request_lock()`, `convert_lock()`, `unlock_lock()`, and `cancel_lock()` find and lock the RSB.
3. `_request_lock()`, `_convert_lock()`, `_unlock_lock()`, and `_cancel_lock()` decide local vs remote handling.
4. `do_request()`, `do_convert()`, `do_unlock()`, and `do_cancel()` mutate master-side queues and queue callbacks.

Remote operations call `send_*()`, causing the peer to run equivalent receive and stage-4 logic on the master node.

## Compatibility, Grants, and LVBs

The file defines the VMS-style compatibility matrix, the LVB operation matrix, and a QUECVT conversion matrix. `can_be_granted()` handles normal grant rules plus `EXPEDITE`, `QUECVT`, `NOORDER`, conversion deadlock detection, `CONVDEADLK` demotion, and `ALTPR`/`ALTCW` alternate-mode grants.

`grant_pending_locks()` grants eligible conversions and waiters, then sends BAST callbacks to granted locks that block the highest remaining requested mode.

`set_lvb_lock()`, `set_lvb_unlock()`, and `set_lvb_lock_pc()` implement LVB copy, write, sequence increment, and invalidation semantics for master/local and process-copy locks.

## RSB and LKB Lifetime

RSBs live in `ls_rsbtbl` and on slow active/inactive lists. Active RSBs are refcounted; inactive RSBs are not. `find_rsb()` computes the resource hash, maps a directory node, and dispatches to directory or no-directory lookup logic under RCU.

`deactivate_rsb()` moves an unused RSB inactive and decides whether it remains as a directory record or is scheduled for toss cleanup. `dlm_rsb_scan()` frees expired inactive RSBs and sends `DLM_MSG_REMOVE` to directory nodes when required.

LKBs are allocated in `ls_lkbxa`, looked up with `find_lkb()`, and removed by `__put_lkb()` at final refcount drop. Queue membership is managed by `add_lkb()`, `del_lkb()`, and `move_lkb()`.

## Master Lookup

`set_master()` ensures an LKB has a known master before a request proceeds. Unknown masters trigger `send_lookup()` to the directory node and serialize other requests on `res_lookup`. `dlm_master_lookup()` is the directory-side implementation used by normal lookup and recovery; it can create inactive directory records and repair master mappings.

## Public API

`dlm_lock()` locates the lockspace, takes the recovery read lock, creates or finds an LKB, validates args, performs request/convert, and normalizes asynchronous completion statuses.

`dlm_unlock()` locates the lockspace, takes the recovery read lock, finds the LKB, validates unlock/cancel flags, performs cancel/unlock, and normalizes expected DLM completion and overlap statuses.

## Wire Message Handling

`create_message()` sizes messages by type, including names or LVB data. `send_common()` adds a waiter, serializes LKB fields, and commits via midcomms. Special paths handle down-conversion local replies, directory lookup, directory remove, grant, BAST, and purge.

`dlm_receive_buffer()` validates sender identity, finds the lockspace, gates receive activity with `ls_recv_active`, and dispatches DLM messages or RCOM recovery messages. Normal messages are saved to the requestqueue while recovery blocks receive processing.

Receive handlers implement request, convert, unlock, cancel, grant, BAST, lookup, remove, purge, and replies. `validate_message()` enforces correct master-copy/process-copy direction and rejects user/kernel lock mixing.

## Waiters and Overlaps

Remote operations are represented on `ls_waiters`. Overlapping force-unlock/cancel is tracked with `DLM_IFL_OVERLAP_UNLOCK_BIT`, `DLM_IFL_OVERLAP_CANCEL_BIT`, and `lkb_wait_count`. `_remove_from_waiters()` handles normal and overlapping replies, including preemptively clearing stale cancel state when a convert succeeds.

## Recovery

`dlm_recover_waiters_pre()` marks lookups, requests, and up-conversions for resend when masters may have changed, and synthesizes replies for unlock/cancel/down-conversion cases.

`dlm_recover_waiters_post()` clears stale waiter state and replays affected operations through `_request_lock()` or `_convert_lock()`, unless an overlapping unlock/cancel replaces the original operation.

`dlm_recover_master_copy()` reconstructs master-copy LKBs on a new master from recovery lock records. `dlm_recover_process_copy()` updates process-copy remote ids from recovery replies. `dlm_recover_purge()` removes locks for departed nodes and marks LVB invalidation. `dlm_recover_grant()` grants newly unblocked locks after recovery.

## Userspace Operations

Userspace wrappers manage `struct dlm_user_args` and process lists: `dlm_user_request()`, `dlm_user_convert()`, `dlm_user_unlock()`, `dlm_user_cancel()`, `dlm_user_deadlock()`, `dlm_user_adopt_orphan()`, `dlm_user_purge()`, and `dlm_clear_proc_locks()`.

Persistent userspace locks can become orphan locks and later be adopted by matching resource name and mode.

## Research Notes

Critical invariants: RSB queues are protected by `res_lock`; RSB table/list membership by `ls_rsbtbl_lock` plus RCU; LKB id lifetime by `ls_lkbxa_lock`; normal locking by `ls_in_recovery`; remote operations by `ls_waiters` until a real or synthetic reply resolves them.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/dlm/lock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/dlm/lock.h -->
# File Research: sources/os/linux/linux/fs/dlm/lock.h

## Role

`lock.h` declares the internal interfaces exported by `lock.c` to the rest of DLM and defines the core RSB locking helpers.

## Exported Areas

It declares debug/dump helpers, receive entry points, compatibility helpers, RSB/LKB lifetime functions, recovery gating, scan timer hooks, master lookup helpers, recovery reconstruction/grant functions, userspace DLM operations, process cleanup, and debug LKB/waiter insertion helpers.

## Inline Helpers

`is_master()` returns true when `res_nodeid` is zero and warns if `res_nodeid == -1`. `lock_rsb()` and `unlock_rsb()` wrap `spin_lock_bh()` / `spin_unlock_bh()` around `r->res_lock`.

## Research Notes

`lock.h` is a compact map of what external DLM code is allowed to do with the lock core.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/dlm/lock.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/dlm/lockspace.c -->
# File Research: sources/os/linux/linux/fs/dlm/lockspace.c

## Role

`lockspace.c` manages DLM lockspace lifetime. It creates and destroys lockspaces, tracks them globally, starts/stops global communication, integrates with sysfs and uevents, initializes per-lockspace data structures, and coordinates final cleanup.

## Global State

The file maintains `ls_count`, `ls_lock`, global `lslist`, `lslist_lock`, and the `dlm_kset`.

## Sysfs and Uevents

Per-lockspace sysfs attributes include `control`, `event_done`, `id`, `nodir`, `recover_status`, and `recover_nodeid`.

`do_uevent()` sends online/offline uevents and waits for userspace, normally `dlm_controld`, to write `event_done`. `dlm_uevent()` adds `LOCKSPACE=<name>`.

## References and Lookup

`dlm_find_lockspace_global()`, `dlm_find_lockspace_local()`, and `dlm_find_lockspace_device()` find lockspaces and increment transient `ls_count`. `dlm_put_lockspace()` decrements it and wakes `ls_count_wait` when it reaches zero. `remove_lockspace()` waits for all transient users to drain before removing from `lslist`.

## Creation Flow

`new_lockspace()` validates name/LVB length, pins the module, requires the userspace daemon, checks cluster/callback constraints, reuses existing lockspaces where allowed, allocates `struct dlm_ls`, initializes tables/queues/locks/recovery state/timers, starts callback and recoverd infrastructure, waits for the initial recovery lock, adds sysfs state, emits join uevents, waits for initial recovery, and creates debugfs files.

`__dlm_new_lockspace()` serializes global creation and starts midcomms for the first lockspace. `dlm_new_lockspace()` creates filesystem/kernel lockspaces with `DLM_LSFL_FS`; `dlm_new_user_lockspace()` creates userspace lockspaces and rejects `DLM_LSFL_SOFTIRQ`.

## Release Flow

`release_lockspace()` checks busy state, updates create count, deregisters the device, emits leave uevents where required, stops recoverd, clears running state, shuts down the scan timer, clears membership, stops callbacks, removes the lockspace from global lookup, deletes debugfs files, drops kobject state, destroys recovery allocations, purges queues/members, and queues delayed final free on `dlm_wq`.

`dlm_release_lockspace()` validates options, serializes release, decrements global lockspace count, and stops midcomms when no lockspaces remain.

## Final Free

`free_lockspace()` asynchronously frees remaining LKBs, destroys the LKB xarray, frees all RSBs in the rhashtable, and frees `struct dlm_ls`.

## Emergency Stop

`dlm_stop_lockspaces()` stops all running lockspaces when the userspace control daemon is unavailable.

## Research Notes

`lockspace.c` owns allocation and teardown of `struct dlm_ls`, while `lock.c` owns most behavior. The key invariants are serialized create/release, safe list/ref handling, initial recovery lock acquisition before exposure, and delayed final free after runtime components stop.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/dlm/lockspace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/dlm/lockspace.h -->
# File Research: sources/os/linux/linux/fs/dlm/lockspace.h

## Role

`lockspace.h` declares the internal lockspace lifecycle and lookup API implemented by `lockspace.c`.

## Constants

`DLM_LSFL_FS` marks a kernel/filesystem lockspace user and enables direct BAST/CAST callbacks. The comment notes it is internal and intended for future removal.

## Exposed Functions

- `dlm_lockspace_init()` / `dlm_lockspace_exit()`
- `dlm_find_lockspace_global(uint32_t id)`
- `dlm_find_lockspace_local(void *id)`
- `dlm_find_lockspace_device(int minor)`
- `dlm_put_lockspace(struct dlm_ls *ls)`
- `dlm_stop_lockspaces()`
- `dlm_new_user_lockspace(...)`

## Research Notes

The header exposes only lifecycle and lookup primitives. The heavier `struct dlm_ls` definition remains in `dlm_internal.h`; external public creation/release APIs are declared through broader DLM headers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/dlm/lockspace.h -->
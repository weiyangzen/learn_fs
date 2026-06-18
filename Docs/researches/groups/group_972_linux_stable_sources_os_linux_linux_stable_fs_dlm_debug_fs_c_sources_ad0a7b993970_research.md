# Group Research: group_972_linux_stable_sources_os_linux_linux_stable_fs_dlm_debug_fs_c_sources_ad0a7b993970

Scope: `Docs/research_subset_a.md`; source tree `sources/os/linux/linux-stable` is included. All eight listed DLM files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/debug_fs.c -->
# File Research: sources/os/linux/linux-stable/fs/dlm/debug_fs.c

## Purpose
`debug_fs.c` implements DLM debugfs visibility and limited debug mutation hooks. It creates `/sys/kernel/debug/dlm` files per lockspace for RSB/LKB state dumps, waiters inspection, and communication-peer state under `dlm/comms`.

## Main Interfaces
- `dlm_register_debugfs()` / `dlm_unregister_debugfs()` create and remove the top-level debugfs directories.
- `dlm_create_debug_file()` / `dlm_delete_debug_file()` create per-lockspace files:
  - `<ls_name>`: human-readable RSB dump.
  - `<ls_name>_locks`: compact lock table, writable for debug LKB injection.
  - `<ls_name>_all`: detailed RSB/LKB dump.
  - `<ls_name>_toss`: inactive/tossed RSB dump.
  - `<ls_name>_waiters`: waiters list, writable for debug waiter injection.
- `dlm_create_debug_comms_file()` / `dlm_delete_debug_comms_file()` expose per-node midcomms state, flags, queue count, protocol version, and `rawmsg`.

## Behavior
The file defines four seq-file formats over lockspace RSB lists:
- Format 1 is readable narrative output: resource name, master state, LVB bytes, recovery flags, and granted/convert/wait/lookup queues.
- Format 2 is a one-line-per-lock table with ids, node ids, flags, status, modes, queue time, and resource name.
- Format 3 emits detailed RSB records, LVB records, and LKB records, including callback timing and lookup entries.
- Format 4 dumps inactive/toss-list RSBs, including current node, master node, directory node, toss time, flags, and printable/hex resource names.

The seq iterator takes `ls_rsbtbl_lock` in read mode while walking `ls_slow_active` or `ls_slow_inactive`, and each printer also takes the individual RSB spinlock while reading queues. Overflow checks stop expensive formatting once the seq buffer is full.

## Debug Mutation Hooks
`table_write2()` parses `lkb_id name flags nodeid status` and calls `dlm_debug_add_lkb()`. `waiters_write()` parses `lkb_id mstype to_nodeid` and calls `dlm_debug_add_lkb_to_waiters()`. Both are debug-only paths that intentionally alter internal lock state for testing.

`waiters_read()` uses `debug_buf_lock`, attempts `dlm_lock_recovery_try()`, then dumps `ls_waiters` under `ls_waiters_lock`. If recovery lock acquisition fails, it returns `-EAGAIN`.

## Midcomms Debug Hooks
The `comms/<nodeid>/` files read state from `midcomms` helper functions. `rawmsg` copies a user buffer up to `PAGE_SIZE` and sends it through `dlm_midcomms_rawmsg_send()`.

## Dependencies
Depends on `dlm_internal.h` structures, `lock.h` lock/recovery/debug helpers, `ast.h`, and `midcomms.h`.

## Risks and Notes
The writable debugfs files are powerful: they can inject LKBs, waiters, and raw DLM messages. The code relies on debugfs permissions and `CONFIG_DLM_DEBUG`. Output formatting prints resource names with `%s` in some formats even though DLM names are length-tracked; the file generally limits names through fixed buffers and DLM maximum length.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/debug_fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/dir.c -->
# File Research: sources/os/linux/linux-stable/fs/dlm/dir.c

## Purpose
`dir.c` implements the DLM directory: the mapping from resource-name hashes to directory nodes and, through directory records, to resource master nodes. It also supports directory reconstruction during lockspace recovery.

## Main Interfaces
- `dlm_hash2nodeid()` maps a resource hash to a directory node using the upper 16 hash bits, `ls_total_weight`, and `ls_node_array`.
- `dlm_dir_nodeid()` returns `rsb->res_dir_nodeid`.
- `dlm_recover_dir_nodeid()` recomputes directory node ids for RSBs on a recovery root list.
- `dlm_recover_directory()` rebuilds local directory records by requesting master-name dumps from other members.
- `dlm_copy_master_names()` serves those name-dump requests to other nodes.

## Directory Recovery
`dlm_recover_directory()` iterates current members other than self, repeatedly calls `dlm_rcom_names()`, and parses returned big-endian name-length/name records. It treats:
- `0xFFFF` as end-of-dump for a node.
- `0` as end-of-buffer/chunk.

For each name, it calls `dlm_master_lookup(..., DLM_LU_RECOVER_DIR, ...)` to add or verify a directory record. It logs inconsistent cases where an existing directory entry maps the name to a different master than the member claiming it. On success it sets `DLM_RS_DIR`.

If `LSFL_NODIR` is set, recovery skips directory rebuilding and still marks directory recovery complete.

## Name Dump Serving
`dlm_copy_master_names()` walks `ls_masters_list` under `ls_masters_lock`, selecting only RSBs for which the requesting node is the directory node. It emits a sequence of big-endian length/name records into the provided output buffer, stopping early with a `0` record if the next record plus terminator would not fit. At the end of the list it emits `0xFFFF`.

The function tracks multi-message dump state with `struct dlm_dir_dump` objects stored on `ls_dir_dump_list` under `ls_dir_dump_lock`. Each context records the recovery sequence, requester node, last list position, and sent counters. The code uses this state to continue dumps and sanity-check that recovery sequence/list position did not drift.

## Dependencies
Uses RCOM recovery messaging from `rcom.h`, member lists from `member.h`, lock/RSH lookup helpers from `lock.h`, and lockspace recovery status helpers.

## Concurrency
The local RSB table is read via `dlm_search_rsb_tree()` under `ls_rsbtbl_lock` in `find_rsb_root()`, with a fallback scan of `ls_masters_list`. Directory dump contexts use a separate rwlock. Master-list iteration is protected by `ls_masters_lock`.

## Risks and Notes
The dump protocol is stateful and assumes the peer will continue using the last name/length. If the context is missing or the recovery sequence changed, the function logs and aborts the chunk without writing a structured error into `outbuf`. Buffer parsing in recovery is defensive about record length and maximum DLM resource-name length.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/dir.h -->
# File Research: sources/os/linux/linux-stable/fs/dlm/dir.h

## Purpose
`dir.h` declares the DLM directory API used by locking, recovery, and RCOM code.

## Exports
- `dlm_dir_nodeid(struct dlm_rsb *rsb)`
- `dlm_hash2nodeid(struct dlm_ls *ls, uint32_t hash)`
- `dlm_recover_dir_nodeid(struct dlm_ls *ls, const struct list_head *root_list)`
- `dlm_recover_directory(struct dlm_ls *ls, uint64_t seq)`
- `dlm_copy_master_names(struct dlm_ls *ls, const char *inbuf, int inlen, char *outbuf, int outlen, int nodeid)`

## Integration
The header depends on `struct dlm_ls` and `struct dlm_rsb` definitions from `dlm_internal.h`. It is used by `lock.c` for resource lookup/master routing and by recovery messaging paths for directory rebuild.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/dir.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/dlm_internal.h -->
# File Research: sources/os/linux/linux-stable/fs/dlm/dlm_internal.h

## Purpose
`dlm_internal.h` is the main private DLM header. It defines core in-kernel structures, message formats, state flags, logging helpers, and inline flag conversion helpers used across the DLM implementation.

## Core Structures
- `struct dlm_member`: one lockspace member, with node id, weight, slot, comm sequence, and generation.
- `struct dlm_recover`: recovery input containing member configuration and sequence.
- `struct dlm_args`: internal normalized arguments for lock/unlock operations.
- `struct dlm_user_args`: userspace lock metadata and user pointers copied back through callbacks.
- `struct dlm_callback`: queued AST/BAST callback record.
- `struct dlm_lkb`: lock block. Tracks resource pointer, refcount, ids, remote ids, external/internal/status flags, status queue membership, waiters state, callback state, LVB pointer, and user/kernel callback parameters.
- `struct dlm_rsb`: resource block. Tracks lockspace, refcount, resource name, hash, master/directory node ids, LVB state, grant/convert/wait queues, lookup queue, slow active/inactive list linkage, scan/recovery/master lists, and recovery flags.
- `struct dlm_ls`: lockspace state. Holds global id, refcounts, flags, RSB hash table, LKB xarray, waiters/orphans, members, debugfs dentries, recovery state, request queue, masters/directory-dump lists, scan timer/list, callbacks, user device, and lockspace name.

## Protocol Types
Defines the common `struct dlm_header`, normal `struct dlm_message`, recovery `struct dlm_rcom`, options structures, and `union dlm_packet`.

Message types include request, convert, unlock, cancel, replies, grant, BAST, lookup, remove, and purge. RCOM types cover recovery status, names, lookup, lock transfer, and replies. Recovery status bits track nodes, directory, locks, and done phases.

## Flags and Inline Helpers
Defines:
- LKB status values: waiting, granted, convert.
- Internal LKB flag bit ranges (`DLM_IFL_*`) and distributed flag bits (`DLM_DFL_*`).
- RSB flags for master uncertainty, LVB validity, new master, recovery convert/grant/LVB invalidation, inactive, and hashed.
- Lockspace flags (`LSFL_*`) for recovery control, running state, no-directory mode, softirq behavior, receive blocking, and filesystem users.

Inline helpers include:
- `rsb_set_flag()`, `rsb_clear_flag()`, `rsb_flag()`.
- `dlm_locking_stopped()`, `dlm_recovery_stopped()`, `dlm_no_directory()`.
- Bitfield snapshot/set helpers for internal, distributed, and status-block flags.

## Debug Configuration
Under `CONFIG_DLM_DEBUG`, declares debugfs registration and per-lockspace/per-comms debug file helpers. Otherwise, it provides no-op stubs.

## Integration
This header ties together nearly every file in `fs/dlm`. `lock.c` is its heaviest consumer, using LKB/RSB/lockspace layouts and protocol structs. `lockspace.c` owns creation/destruction of `struct dlm_ls`, and `debug_fs.c` reads many fields directly.

## Risks and Notes
The header encodes wire-visible structures and private in-memory state in one place. Changing fields, bit ranges, or endian-marked protocol structs has broad compatibility implications. Comments call out historical quirks, especially the difference between `res_master_nodeid` and `res_nodeid`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/dlm_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/lock.c -->
# File Research: sources/os/linux/linux-stable/fs/dlm/lock.c

## Purpose
`lock.c` is the central DLM lock engine. It implements lock request/convert/unlock/cancel operations, local and remote message handling, RSB/LKB lifetime management, grant policy, recovery repair, userspace lock wrappers, orphan/purge handling, and debug injection helpers.

## Operation Model
The file documents and implements a four-stage flow:
1. Public API: `dlm_lock()` and `dlm_unlock()`.
2. RSB selection: `request_lock()`, `convert_lock()`, `unlock_lock()`, `cancel_lock()`.
3. Local-vs-remote dispatch: `_request_lock()`, `_convert_lock()`, `_unlock_lock()`, `_cancel_lock()`.
4. Master-side mutation: `do_request()`, `do_convert()`, `do_unlock()`, `do_cancel()`.

Remote sends cause the matching `receive_*()` function on the master node to run the same `do_*()` logic and send a reply.

## Resource and Lock Lifetime
RSBs are stored in `ls_rsbtbl` and mirrored on slow active/inactive lists for iteration. Active RSBs are refcounted; inactive RSBs are cached as toss-list entries and later removed by `dlm_rsb_scan()`. Directory-mode RSBs may remain inactive as directory records for remotely mastered resources.

Key functions:
- `find_rsb()` dispatches to directory or no-directory lookup.
- `find_rsb_dir()` handles local requests, remote requests, directory records, stale master mappings, inactive resurrection, and master lookup uncertainty.
- `find_rsb_nodir()` uses hash-selected node as direct master in no-directory mode.
- `deactivate_rsb()` moves unused RSBs inactive and schedules toss scanning when appropriate.
- `free_inactive_rsb()` asserts all queues/lists are empty before freeing.

LKBs are allocated in `ls_lkbxa` by `create_lkb()` / `_create_lkb()`, found by `find_lkb()`, and released by `dlm_put_lkb()` / `__put_lkb()`. Queue membership adds references; removing from queues drops them.

## Grant Policy
The compatibility matrix implements VMS-style DLM lock mode compatibility. `dlm_lvb_operations` defines whether an LVB is returned, written, invalidated, or untouched for mode transitions.

`can_be_granted()` wraps `_can_be_granted()` and handles:
- `DLM_LKF_EXPEDITE` for NL requests.
- Grant/convert/wait queue conflicts.
- QUECVT FIFO conversion semantics.
- NOORDER bypass.
- conversion deadlock detection.
- CONVDEADLK demotion to NL.
- ALTPR/ALTCW alternate grant modes.

`grant_pending_locks()` tries convert queue then wait queue, grants newly available locks, and sends BASTs to granted locks when blocked waiters remain.

## Messaging
Send helpers construct `struct dlm_message` through midcomms:
- operation sends: request, convert, unlock, cancel.
- async sends: grant, BAST.
- directory sends: lookup, remove.
- replies: request/convert/unlock/cancel/lookup reply.
- purge messages for userspace orphan cleanup.

`send_common()` adds an LKB to `ls_waiters` before sending messages expecting replies. It supports overlap handling where cancel/force-unlock may be issued while another remote operation is pending.

Receive handlers validate message direction and lock identity, locate/create RSBs and LKBs, apply flags/LVB data, run master-side operations, and send replies. `dlm_receive_buffer()` validates node ids, resolves lockspace by global id, and dispatches MSG vs RCOM under `ls_recv_active`.

When the lockspace is recovering, `dlm_receive_message()` queues normal messages on the requestqueue instead of processing immediately.

## Directory/Master Interaction
`set_master()` chooses an LKB target from the RSB master state. If the master is unknown, it sends a lookup to the directory node and places later LKBs on `res_lookup`. `confirm_master()` releases or advances the lookup queue after lookup/request outcomes.

`dlm_master_lookup()` is the directory-node authority for name-to-master mapping. It can create inactive directory records, repair mappings during recovery, and return `DLM_LU_MATCH` or `DLM_LU_ADD`.

## Recovery
Recovery paths include:
- `dlm_recover_waiters_pre()`: handles outstanding waiters before recovery by marking requests/lookups for resend and faking local unlock/cancel replies when the peer is gone.
- `dlm_recover_waiters_post()`: clears waiter state, then resends or locally reprocesses affected requests/conversions, respecting overlap cancel/unlock flags.
- `dlm_recover_purge()`: removes master-copy locks for departed nodes and marks RSBs for grant/LVB recovery.
- `dlm_recover_grant()`: grants locks made possible by purging or rebuilt state.
- `dlm_recover_master_copy()` / `dlm_recover_process_copy()`: rebuild master-copy and process-copy lock state using RCOM lock records.

## Userspace Lock Path
Userspace wrappers mirror kernel APIs while attaching `struct dlm_user_args` and per-process ownership lists:
- `dlm_user_request()`
- `dlm_user_convert()`
- `dlm_user_adopt_orphan()`
- `dlm_user_unlock()`
- `dlm_user_cancel()`
- `dlm_user_deadlock()`
- `dlm_clear_proc_locks()`
- `dlm_user_purge()`

Persistent locks can become orphans and later be adopted by resource name/mode. Nonpersistent locks are force-unlocked on process cleanup. Purge can be local or sent remotely.

## Concurrency
Important synchronization includes:
- `ls_in_recovery` rwsem blocks normal locking during recovery.
- `res_lock` protects each RSB queue and core state.
- `ls_rsbtbl_lock` protects hash-table/list state.
- RCU protects lookup races while RSBs are removed from the hash table.
- `ls_lkbxa_lock` protects xarray/refcount transitions.
- `ls_waiters_lock`, `ls_orphans_lock`, and `ls_clear_proc_locks` protect auxiliary lists.
- Scan timer uses `ls_scan_lock` and avoids blocking recovery by checking `dlm_locking_stopped()`.

## Risks and Notes
This file is concurrency-sensitive and protocol-sensitive. The most fragile areas are waiter overlap handling, RSB inactive resurrection/removal races, directory/master uncertainty, and recovery resends. The code contains detailed comments explaining expected races, especially lookup/request optimization, remove-vs-request races, and aborted recovery cycles.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/lock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/lock.h -->
# File Research: sources/os/linux/linux-stable/fs/dlm/lock.h

## Purpose
`lock.h` declares the public-internal lock engine API used by other DLM files.

## Exported Areas
- Debug/dump helpers: `dlm_dump_rsb()`, `dlm_dump_rsb_name()`, `dlm_print_lkb()`.
- Receive entry points: `dlm_receive_message_saved()`, `dlm_receive_buffer()`.
- Compatibility and lifetime: `dlm_modes_compat()`, `free_inactive_rsb()`, `dlm_put_rsb()`, `dlm_hold_rsb()`, `dlm_put_lkb()`.
- Recovery locking and timers: `dlm_lock_recovery_try()`, `dlm_lock_recovery()`, `dlm_unlock_recovery()`, `dlm_rsb_scan()`, `resume_scan_timer()`.
- Directory/master helpers: `dlm_master_lookup()`, `dlm_search_rsb_tree()`.
- Recovery helpers: purge, grant, waiters pre/post, recover master/process copy.
- Userspace lock operations: request, convert, adopt orphan, unlock, cancel, purge, deadlock, clear process locks.
- Debug mutation helpers used by `debug_fs.c`.

## Inline Helpers
- `is_master(r)` treats `res_nodeid == 0` as locally mastered and warns if master is unknown.
- `lock_rsb()` / `unlock_rsb()` wrap `spin_lock_bh()` and `spin_unlock_bh()` for RSB protection.

## Integration
This is the main cross-file contract for `lock.c`. Recovery, directory, debugfs, requestqueue, RCOM, and user device code use these declarations rather than reaching into `lock.c` internals.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/lock.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/lockspace.c -->
# File Research: sources/os/linux/linux-stable/fs/dlm/lockspace.c

## Purpose
`lockspace.c` manages DLM lockspace lifecycle: global registration, sysfs control, userspace coordination through uevents, creation, lookup/refcounting, release, and forced stopping when the control daemon disappears.

## Sysfs and Uevents
Each lockspace is represented by a kobject under the `dlm` kset. Attributes include:
- `control`: `0` stops a lockspace, `1` starts it.
- `event_done`: written by userspace control daemon to complete group events.
- `id`: lockspace global id.
- `nodir`: enables no-directory mode.
- `recover_status`: current recovery status bits.
- `recover_nodeid`: current recovery node id for diagnostics.

`do_uevent()` emits online/offline kobject events and waits for `dlm_controld` to write `event_done`. `dlm_uevent()` adds the `LOCKSPACE=<name>` environment variable.

## Global State
The file maintains:
- `ls_count`: number of created lockspaces.
- `ls_lock`: serializes create/release and midcomms start/stop.
- `lslist` plus `lslist_lock`: global lockspace list and lookup/refcount protection.

Lookup helpers:
- `dlm_find_lockspace_global()`
- `dlm_find_lockspace_local()`
- `dlm_find_lockspace_device()`
- `dlm_put_lockspace()`

## Creation
`dlm_lockspace_init()` creates the `dlm` kset. `new_lockspace()` validates name/LVB length, requires the user daemon, checks cluster-name compatibility when recovery callbacks are enabled, reuses existing lockspaces unless `DLM_LSFL_NEWEXCL` is set, then allocates and initializes `struct dlm_ls`.

Initialization covers RSB hash table, LKB xarray, waiters/orphans, member lists, recovery queues, recovery buffer, scan timer, masters/directory-dump lists, callback workqueue, recoverd thread, sysfs kobject, userspace join uevent, initial recovery completion, and debugfs files.

`__dlm_new_lockspace()` starts global midcomms on the first lockspace and shuts it down if creation fails. `dlm_new_lockspace()` forces filesystem-user mode; `dlm_new_user_lockspace()` rejects softirq mode for userspace.

## Release
`lockspace_busy()` checks whether locks remain, depending on release option. `release_lockspace()` decrements create count or removes the final instance, sends leave uevents when appropriate, stops recoverd/callbacks/timers, deregisters the user device, clears members, purges requestqueue/recovery state, removes debugfs/sysfs, and queues delayed memory cleanup through `free_lockspace()` on `dlm_wq`.

`free_lockspace()` destroys remaining LKBs and RSBs after delayed teardown.

`dlm_release_lockspace()` validates release option, finds the lockspace, serializes release, decrements `ls_count`, and stops midcomms when the last lockspace is gone.

## Emergency Stop
`dlm_stop_lockspaces()` scans running lockspaces and calls `dlm_ls_stop()` if the userspace daemon has gone away, logging any lockspaces left stopped.

## Dependencies
Integrates with midcomms, recoverd, recovery, membership, config, memory allocation, user device, requestqueue, debugfs, AST callbacks, and lock engine timers.

## Risks and Notes
Lockspace creation and release cross kernel threads, sysfs, uevents, timers, midcomms, and userspace daemon state. The teardown order is deliberate: stop external activity first, remove from global list only after references drain, then free heavy state asynchronously.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/lockspace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/lockspace.h -->
# File Research: sources/os/linux/linux-stable/fs/dlm/lockspace.h

## Purpose
`lockspace.h` declares the lockspace lifecycle API and defines the private filesystem-user flag.

## Exports
- `DLM_LSFL_FS`: internal flag for kernel/filesystem users, enabling direct BAST/CAST callbacks.
- `dlm_lockspace_init()`
- `dlm_lockspace_exit()`
- `dlm_find_lockspace_global()`
- `dlm_find_lockspace_local()`
- `dlm_find_lockspace_device()`
- `dlm_put_lockspace()`
- `dlm_stop_lockspaces()`
- `dlm_new_user_lockspace()`

## Integration
Used by DLM initialization, user-device paths, message receive paths, and filesystem-facing lockspace creation. Kernel callers use the non-header-declared public `dlm_new_lockspace()` from the broader DLM interface, while this header exposes the internal user-lockspace constructor and lookup/refcount helpers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/lockspace.h -->
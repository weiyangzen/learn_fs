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

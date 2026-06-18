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

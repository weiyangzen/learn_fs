# File Research: sources/block-storage/lvm2/lib/locking/locking.c

## Purpose
Provides the generic LVM locking facade used by commands. It initializes file locking, applies command-mode policies such as `--readonly`, `--sysinit`, and `--ignorelockingfailure`, tracks held VG locks, coordinates signal/memlock behavior, and combines local file global locks with lvmlockd global locks.

## Main Responsibilities
- Holds the active `struct locking_type` backend and lock policy state.
- Tracks the number of VG locks held and whether any write VG lock has been acquired.
- Initializes file locking and records fallback behavior when initialization fails.
- Blocks signals while acquiring locks and keeps signals blocked while VG locks are held.
- Grants or rejects lock requests according to disabled locking, readonly mode, sysinit mode, ignore-locking-failure mode, and `global/metadata_read_only`.
- Updates `lvmcache` VG lock state after successful non-global locks.
- Provides global file-lock helpers for shared, exclusive, unlock, conversion, and nonblocking modes.
- Provides `lock_global` and `lock_global_convert`, which take the local file global lock and then the lvmlockd global lock.
- Provides `sync_local_dev_names`, which drops memlock and filesystem locks before VG unlock backup handling.

## Important Control Flow
`init_locking` reads `global/wait_for_locks`, records command flags, and calls `init_file_locking`. If file locking setup fails, `--sysinit` and `--ignorelockingfailure` allow the command to proceed in a readonly-like mode; otherwise initialization fails.

`lock_vol` is the main policy gate. It skips orphan VGs, forces nonblocking flags when blocking is disabled, copies the resource name safely, then handles disabled file locking, failed file-locking fallback, readonly/sysinit combinations, and `metadata_read_only`. Real backend locking happens through `_lock_vol`, after which non-global VG lock state is mirrored in `lvmcache`.

`_lockf_global` translates string modes `ex`, `sh`, and `un` into lock flags. It preserves `cmd->lockf_global_ex` so later process-each code does not accidentally downgrade an explicitly held exclusive file global lock.

## Dependencies
Depends on file-locking backend initialization, lvmlockd global locking, activation functions, command context policy flags, memlock and filesystem lock helpers, signal helpers, and `lvmcache` lock markers.

## Risk Notes
- `--readonly --sysinit` deliberately permits activation while refusing other write locks.
- Failed lock initialization with `--ignorelockingfailure` can still permit activation, so policy checks must stay aligned with command semantics.
- Unlock failure paths update lock counts differently from normal success paths; incorrect counts can leave signals blocked or unblocked at unsafe times.
- `lock_global` must unwind the file global lock if lvmlockd global lock acquisition fails.

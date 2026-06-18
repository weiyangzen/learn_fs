# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/zfs_debug.c

## Purpose

Implements the FreeBSD/OpenZFS in-kernel debug message buffer exposed through a raw kstat named `zfs.misc.dbgmsg`, plus low-level debug formatting helpers used by `dprintf()` and `SET_ERROR()`-style diagnostics.

## Main Data Structures

- `zfs_dbgmsg_t`
  - List node plus timestamp, allocation size, and flexible message buffer.
  - Stored in the global `zfs_dbgmsgs` list.
- Global state:
  - `zfs_dbgmsgs`: ordered list of retained debug messages.
  - `zfs_dbgmsg_size`: total allocated bytes currently retained.
  - `zfs_dbgmsgs_lock`: protects list and size.
  - `zfs_dbgmsg_maxsize`: tunable cap, default `4 << 20`.
  - `zfs_dbgmsg_kstat`: raw kstat handle.
  - `zfs_dbgmsg_enable`: module parameter advertised as enabling the debug log; this file defines it but the actual call-site gating is expected outside this file.

## Key Functions

- `zfs_dbgmsg_init()`
  - Creates the debug-message list and mutex.
  - Creates a virtual raw kstat named `zfs/dbgmsg/misc`.
  - Installs raw kstat callbacks for headers, row formatting, and cursor traversal.
- `zfs_dbgmsg_fini()`
  - Deletes the kstat if present.
  - Purges every retained message under lock.
  - Destroys the mutex.
- `__zfs_dbgmsg(char *buf)`
  - Emits DTrace probe `zfs__dbgmsg`.
  - Allocates a `zfs_dbgmsg_t`, records current time via `gethrestime_sec()`, copies the message, appends it to the list, and purges old entries until under `zfs_dbgmsg_maxsize`.
- `__dprintf(boolean_t dprint, const char *file, const char *func, int line, const char *fmt, ...)`
  - Formats `file:line:function(): message` into a fixed 1024-byte kernel allocation.
  - Strips directory prefixes from source filenames.
  - If `dprint` is true, strips one trailing newline.
  - Sends the final buffer into `__zfs_dbgmsg()`.
- `__set_error(...)`
  - When `zfs_flags & ZFS_DEBUG_SET_ERROR` is set, logs `error <errno>` through `__dprintf()`.

## Kstat Behavior

- `zfs_dbgmsg_headers()` prints `timestamp message`.
- `zfs_dbgmsg_data()` prints each retained message with its timestamp.
- `zfs_dbgmsg_addr()` advances through `zfs_dbgmsgs` using `ks_private` as cursor state.
- `zfs_dbgmsg_update()` treats a kstat write as a request to purge the whole log.

## Concurrency and Memory Notes

- All list traversal and purge operations are protected by `zfs_dbgmsgs_lock`.
- `zfs_dbgmsg_purge()` assumes the mutex is held.
- Messages are allocated with `KM_SLEEP`; logging can sleep.
- Purging subtracts each allocation’s stored `zdm_size`, avoiding recalculation.

## External Interfaces

- DTrace probe: `zfs-dbgmsg`.
- Sysctl/kstat access documented in comments as `kstat.zfs.misc.dbgmsg`.
- Module parameters:
  - `vfs.zfs.dbgmsg_enable`
  - `vfs.zfs.dbgmsg_maxsize`

## Notable Edge Cases

- If `kstat_create()` fails, debug logging still accumulates in the in-memory list, but there is no kstat export.
- `__dprintf()` truncates messages to the 1024-byte scratch buffer.
- A kstat write purges all retained entries without interpreting input.

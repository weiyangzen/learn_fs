# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_debug.c

## Purpose

Implements the in-kernel ZFS debug message buffer exposed through procfs/kstat and DTrace-style tracepoints.

## Data Model

`zfs_dbgmsg_t` is a variable-sized list node containing timestamp, allocation size, and message bytes. A global `procfs_list_t zfs_dbgmsgs` holds entries, with `zfs_dbgmsg_size` tracking total bytes and `zfs_dbgmsg_maxsize` defaulting to 4 MiB.

`zfs_dbgmsg_enable` controls whether callers should emit internal debug messages; the file registers it as a module parameter.

## Procfs Lifecycle

`zfs_dbgmsg_init()` installs `/proc/spl/kstat/zfs/dbgmsg` with show/header/clear callbacks. `zfs_dbgmsg_fini()` uninstalls it, purges all messages, and destroys the list. `zfs_dbgmsg_clear()` purges under the list lock.

`zfs_dbgmsg_show_header()` and `zfs_dbgmsg_show()` render `timestamp` and message columns through `seq_file`.

## Message Emission

`__set_error()` conditionally emits error diagnostics when `ZFS_DEBUG_SET_ERROR` is enabled in `zfs_flags`.

`__dprintf()` builds a bounded 1024-byte message containing current thread pointer, optional `dprintf:` prefix, basename, line, function, and formatted payload. It trims trailing newline for dprintf logs, fires `DTRACE_PROBE1(zfs__dprintf, ...)`, stores the message with `__zfs_dbgmsg()`, and frees the temporary buffer.

`__zfs_dbgmsg()` allocates a variable-sized message, timestamps it with `gethrestime_sec()`, adds it to the procfs list, updates total size, and purges oldest messages until under `zfs_dbgmsg_maxsize`.

# File Research: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_sysevent.c

FreeBSD sysevent bridge for ZFS zevents. It drains ZFS events and emits FreeBSD `devctl_notify()` notifications.

Key behavior:
- `log_sysevent()` serializes nvlist members into an `sbuf`, supporting booleans, integer scalars, strings, several integer arrays, and string arrays.
- If `FM_CLASS` starts with `ESC_ZFS_`, it maps the type to `misc.fs.zfs.<suffix>`.
- `sysevent_worker()` initializes a zevent cursor, repeatedly reads events with `zfs_zevent_next()`, waits when none are available, logs each event, and exits on `ESHUTDOWN`.
- Teardown intentionally avoids `zfs_zevent_destroy()` to avoid a race with `fm_fini()` destroying `zevent_lock`; it frees the cursor directly after draining.
- `ddi_sysevent_init()` starts the worker kernel thread under `zfskern/sysevent`.

Nested nvlists are noted but not recursively logged.

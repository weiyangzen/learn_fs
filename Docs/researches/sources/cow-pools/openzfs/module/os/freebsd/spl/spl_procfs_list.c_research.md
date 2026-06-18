# File Research: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_procfs_list.c

FreeBSD procfs-list compatibility implemented through raw kstats/sysctl output.

Key behavior:
- `seq_printf()` writes into a small `seq_file` buffer via `vsnprintf()`.
- `procfs_list_install()` initializes the list, lock, callbacks, and creates a virtual raw kstat.
- `procfs_list_addr()` iterates list elements and returns temporary iterator cookies for raw kstat output.
- `procfs_list_data()` calls the registered show callback and frees the iterator cookie.
- `procfs_list_update()` invokes the clear callback on write.
- `procfs_list_destroy()` asserts emptiness, deletes the kstat, destroys list and mutex.
- `procfs_list_add()` assigns monotonically increasing IDs and appends entries.

`procfs_list_uninstall()` is currently empty.

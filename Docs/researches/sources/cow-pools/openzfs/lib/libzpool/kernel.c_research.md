# File Research: sources/cow-pools/openzfs/lib/libzpool/kernel.c

Userland kernel-service emulation for libzpool. It provides hostid handling, debug print routing, panic/cmn_err behavior, cache-config import, and global initialization/teardown for subsystems normally provided by the kernel.

Key behavior:
- `zone_get_hostid()` returns the emulated process hostid.
- `dprintf_setup()` consumes `debug=...` argv entries or `ZFS_DEBUG`.
- `__dprintf()` either prints immediately or stores messages through `__zfs_dbgmsg()`.
- `panic()` and `vpanic()` log as panic and abort; `LIBZPOOL_PANIC_STOP=1` sends `SIGSTOP` first.
- `spa_config_load()` reads `spa_config_path` or `ZPOOL_CACHE_BOOT`, unpacks nvlist data, and creates SPA entries.
- `kernel_init()` initializes libspl, umem OOM behavior, hostid, taskqs, ICP, zstd, SPA, fletcher, and TSD keys.
- `kernel_fini()` tears these down.

ZFS onexit, zvol minor, zfsvfs rename, and SPA OS activation hooks are stubs for userland.

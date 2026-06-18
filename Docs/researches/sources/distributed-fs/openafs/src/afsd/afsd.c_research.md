# sources/distributed-fs/openafs/src/afsd/afsd.c

## Purpose

`afsd.c` is the common implementation of the OpenAFS client startup daemon. It parses command-line and `cacheinfo` configuration, computes cache sizing parameters, prepares and sanitizes the workstation cache, pushes configuration into the kernel cache manager through AFSOP syscalls, starts the required cache-manager daemons, and optionally starts user-space support helpers such as AFSDB lookup, background operation helpers, socket proxy handlers, and `rmtsys`.

## Important APIs, Types, and Globals

- Public entry points are `afsd_init()`, `afsd_parse(int argc, char **argv)`, and `afsd_run()`.
- Cache preparation helpers include `ParseCacheInfoFile()`, `PartSizeOverflow()`, `CheckCacheBaseDir()`, `SweepAFSCache()`, `CreateCacheFile()`, `GetVFileNumber()`, and `GetDDirNumber()`.
- Kernel setup is funneled through the private variadic `afsd_syscall()` and launch wrappers `fork_syscall()`, `fork_rx_syscall()`, and `fork_rx_syscall_wait()` where available.
- Important state includes `cacheBlocks`, `cacheFiles`, `cacheStatEntries`, `dCacheSize`, `vCacheSize`, `chunkSize`, `cacheBaseDir`, `afsd_cacheMountDir`, `confDir`, `rootVolume`, feature flags, `cache_dir_list`, `cache_dir_filelist`, `dir_for_V`, optional `inode_for_V`, and `struct afs_cacheParams cparams`.

## Control Flow

`afsd_init()` registers command syntax. `afsd_parse()` parses argv and runs `CheckOptions()`, which sets globals, handles immediate `-shutdown`, validates options, parses split-cache percentages, sets defaults, and reads `cacheinfo`.

`afsd_run()` opens cell configuration, loads the local cell, checks the mount point, auto-tunes cache parameters, validates the disk cache directory, seeds kernel Rx entropy, advises interface addresses, starts Rx services, optional AFSDB/socket-proxy helpers, performs `AFSOP_BASIC_INIT` and `AFSOP_CACHEINIT`, sweeps disk cache files when needed, pushes cell/cache/volume metadata to the kernel, applies feature syscalls, starts AFS/checkserver/background/truncation daemons, calls `AFSOP_GO`, mounts AFS, and optionally enables `rmtsys`.

## State and Persistence Behavior

Persistent filesystem state is the disk cache tree: `CacheItems`, `VolumeItems`, `CellItems`, `D<number>` directories, and `V<number>` cache files. The sweep creates missing files, moves cache files into balanced subdirectories, deletes unknown entries, chmods directories, and sets Darwin no-backup xattrs. Kernel-persistent state is established through AFSOP syscalls for cache parameters, cell information, interface addresses, cache files, and daemon behavior.

## Dependencies and Integration Points

The file depends on OpenAFS command parsing, cell configuration, AFS syscall opcodes, cache parameter structs, xplat utility macros, hcrypto entropy, POSIX filesystem/process APIs, and Darwin frameworks for optional event handling. Backend integration is through `afsd.h` functions such as `afsd_call_syscall()`, `afsd_mount_afs()`, `afsd_fork()`, and priority setters.

## Risks and Edge Cases

Fixed-size pathname buffers and `sprintf()` calls make long path handling risky. Cache sweeping deletes unknown entries, so a wrong `cacheBaseDir` can be destructive. `afsd_syscall_populate()` must stay synchronized with every AFSOP argument layout. Helper loops can retry forever after persistent kernel/config errors. `CreateCacheFile()` treats descriptor `0` as failure. Complex cache balancing has cross-platform inode/path fallback behavior that needs coverage.

## Test Signals

Test option parsing, cacheinfo parsing, memcache/disk-cache sizing, disk sweep creation/deletion/move/rebalance cases, syscall argument population with a mocked backend, startup syscall ordering, `-shutdown`, `-nomount`, AFSDB startup, and platform-specific `AFSOP_CACHEFILE` versus `AFSOP_CACHEINODE` behavior.

# sources/distributed-fs/ceph-client/fs/hpfs/Kconfig

Purpose: this Kconfig entry exposes Linux HPFS filesystem support as `CONFIG_HPFS_FS`.

Important settings: `config HPFS_FS` is a tristate named "OS/2 HPFS file system support". It depends on `BLOCK` and selects `BUFFER_HEAD` and `FS_IOMAP`, matching the implementation’s reliance on block devices, buffer-head mapping, mpage helpers, and iomap fiemap.

Control flow: kernel configuration determines whether HPFS is unavailable, built-in, or a module named `hpfs`. The help text explains that HPFS is used by OS/2/Warp hard disk partitions and points to `Documentation/filesystems/hpfs.rst`.

State and persistence: no runtime state is defined here, but enabling write support through the filesystem driver exposes persistent HPFS mutation paths in the implementation.

Dependencies and integration: the `Makefile` consumes `CONFIG_HPFS_FS` to build `hpfs.o`. `select FS_IOMAP` is required by `file.c` fiemap code, while `select BUFFER_HEAD` is required by almost every HPFS metadata mapper.

Risks: dependency changes can silently break build coverage. Removing `BLOCK` would be invalid because HPFS maps physical sectors. Dropping selected helpers would cause compile failures or missing feature paths.

Test signals: configure `n`, `m`, and `y`; build all three; verify the module name is `hpfs`; and run configuration dependency checks for architectures where block or buffer-head support may be optional.

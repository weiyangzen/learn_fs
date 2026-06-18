# File Research: sources/block-storage/parted/libparted/fs/hfs/hfs.c

HFS filesystem type registration module. It defines global block-cache pointers/counters used by HFS/HFS+ internals and registers three filesystem types: `hfs`, `hfs+`, and `hfsx`.

Each type’s `PedFileSystemOps` contains only a probe callback, implemented in `probe.c`: `hfs_probe`, `hfsplus_probe`, or `hfsx_probe`. Init and done functions register/unregister the three types.

The module itself contains no validation logic. It acts as the registry bridge between libparted’s filesystem framework and the HFS probe implementation.

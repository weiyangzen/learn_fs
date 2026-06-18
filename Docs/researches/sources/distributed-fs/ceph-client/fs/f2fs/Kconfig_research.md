# sources/distributed-fs/ceph-client/fs/f2fs/Kconfig

## Purpose

`fs/f2fs/Kconfig` defines the kernel configuration surface for F2FS. It controls whether F2FS is built, which optional features are compiled, and which compression, encryption, ACL, xattr, debug, fault-injection, iostat, and locking dependencies are selected.

## Important Config Symbols

`F2FS_FS` is the root tristate and depends on `BLOCK`. It selects buffer heads, NLS, CRC32, iomap support, encryption xattr support when needed, encryption algorithms, and compression library symbols according to selected algorithms. `F2FS_STAT_FS` enables debugfs status reporting. `F2FS_FS_XATTR` enables xattrs. `F2FS_FS_POSIX_ACL` depends on xattrs and selects `FS_POSIX_ACL`. `F2FS_FS_SECURITY` depends on xattrs and enables security labels. `F2FS_CHECK_FS` adds runtime consistency checking. `F2FS_FAULT_INJECTION` enables injected failures. `F2FS_FS_COMPRESSION` enables file compression. `F2FS_FS_LZO`, `F2FS_FS_LZORLE`, `F2FS_FS_LZ4`, `F2FS_FS_LZ4HC`, and `F2FS_FS_ZSTD` select algorithm support. `F2FS_IOSTAT` enables I/O statistics, and `F2FS_UNFAIR_RWSEM` enables unfair rwsem behavior when block cgroups are present.

## Control Flow

Kconfig dependency flow starts at `F2FS_FS`. ACL and security features are unavailable unless xattrs are enabled. Compression algorithms are unavailable unless `F2FS_FS_COMPRESSION` is enabled, and their selected library dependencies feed directly into `compress.c` compile-time branches. The default choices lean toward common F2FS functionality: status, xattrs, ACLs, and compression algorithms default to enabled once their parent feature is enabled.

## State and Persistence Behavior

This file does not persist filesystem runtime state, but it determines which on-disk features can be mounted or used by a built kernel. Enabling xattr, ACL, security, and compression changes which metadata features the filesystem can create or interpret. Compression algorithm selections influence whether existing compressed files using a given algorithm can be read.

## Dependencies and Integration Points

The symbols map directly to object inclusion in `Makefile` and to `#ifdef CONFIG_F2FS_*` blocks in F2FS source files such as `acl.c`, `xattr.c`, `compress.c`, `debug.c`, and `iostat.c`. Compression selections integrate with kernel LZO, LZ4, LZ4HC, and ZSTD libraries.

## Risks and Edge Cases

Configuration mismatches can produce kernels unable to access expected F2FS features. Disabling xattrs disables ACL and security labels. Disabling a compression algorithm can make files compressed with that algorithm unreadable by this build. Runtime checking and fault injection are useful for development but may affect performance or failure behavior if enabled unexpectedly.

## Test Signals

Build matrix tests should cover F2FS without xattrs, with xattrs but no ACL/security, with compression disabled, and with each compression algorithm combination. Kconfig dependency tests should verify that selected libraries and object files match enabled symbols and that invalid symbol combinations are not offered.

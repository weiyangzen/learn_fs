# sources/distributed-fs/ceph-client/include/linux/fs_dirent.h

Purpose: defines stable conversions between VFS/userspace directory entry file types and common filesystem on-disk file type values. It centralizes the low three-bit file type convention shared by many Linux filesystems.

Important APIs and types: `S_DT_SHIFT`, `S_DT()`, and `S_DT_MASK` derive dirent type bits from `umode_t`. `DT_*` constants describe userspace `getdents(2)`/`readdir(3)` values, while `FT_*` constants describe common on-disk file types. `fs_ftype_to_dtype()`, `fs_umode_to_ftype()`, and `fs_umode_to_dtype()` are implemented in `fs/fs_dirent.c`.

Control flow: filesystems convert inode modes to on-disk or userspace directory types when constructing directory entries, and convert stored `FT_*` values to `DT_*` when returning entries. Whiteouts are not stored as a separate on-disk type here and are exposed as character-device style directory entries by filesystems that use whiteouts.

State and persistence: the `FT_*` constants are persistent on-disk ABI for filesystems using this common layout, and the `DT_*` values are userspace ABI. The file deliberately warns that values must not change.

Dependencies and integration points: depends only on Linux stat and type definitions, but is included by superblock type definitions and filesystem directory code. Integration points include ext-like directory formats, VFS `filldir` paths, and compatibility with libc `dirent.h`.

Risks and test signals: risks are ABI/layout changes, confusing `DT_WHT` with persistent `FT_*`, and handling unknown/reserved bits incorrectly. Tests should cover all mode-to-type conversions, invalid on-disk values, whiteout exposure, and cross-filesystem directory listings.

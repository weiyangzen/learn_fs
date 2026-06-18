# sources/distributed-fs/ceph-client/fs/omfs/Kconfig

Purpose: defines the kernel configuration switch for SonicBlue Optimized MPEG File System support, covering Rio Karma and ReplayTV disks.

Important APIs and options: `config OMFS_FS` is a tristate option depending on `BLOCK`, selecting `BUFFER_HEAD` and `CRC_ITU_T`. The help text documents the module name `omfs` and positions the feature as device-specific filesystem support.

Control flow: no runtime control flow. Build selection controls whether the OMFS module or built-in filesystem is compiled.

State and persistence behavior: no filesystem state is stored here. The selected CRC and buffer-head dependencies enable runtime metadata checksum and block-buffer operations in `inode.c`, `dir.c`, `file.c`, and `bitmap.c`.

Dependencies and integration points: integrates with Kbuild and kernel configuration. `CRC_ITU_T` is required for OMFS inode header CRC generation, and `BUFFER_HEAD` is required by the implementation's `sb_bread`, `mark_buffer_dirty`, mpage, and block mapping paths.

Risks: dependency omissions would surface as build failures rather than runtime errors. The option does not depend on a specific architecture or endian mode because the code uses big-endian on-disk accessors.

Test signals: `CONFIG_OMFS_FS=y`, `m`, and `n` build coverage; module load/unload when built as `m`; and allmodconfig/allyesconfig coverage for selected dependencies.

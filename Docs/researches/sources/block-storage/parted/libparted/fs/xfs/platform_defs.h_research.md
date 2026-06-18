# File Research: sources/block-storage/parted/libparted/fs/xfs/platform_defs.h

Purpose: Local platform compatibility header imported from older XFS userspace code.

Content: Includes standard C/system headers, defines XFS scalar aliases such as `xfs_off_t`, `xfs_ino_t`, `xfs_dev_t`, `xfs_daddr_t`, and pointer-sized integer aliases `__psint_t`/`__psunsigned_t` based on configured pointer width. It also maps `ASSERT` to `assert` only under `DEBUG`.

Dependencies: Assumes glibc/endian/system type availability and configure-time width macros, here fixed to 32-bit long and 32-bit pointer.

Important details and risks: This is compatibility scaffolding for the imported XFS headers used by the simple probe; it is not a complete modern xfsprogs platform layer. The hard-coded pointer-size macros are notable if reused beyond the current narrow probe build context.

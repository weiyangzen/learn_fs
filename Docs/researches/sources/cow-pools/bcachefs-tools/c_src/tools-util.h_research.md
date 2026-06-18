# File Research: sources/cow-pools/bcachefs-tools/c_src/tools-util.h

- Header for common userspace utility helpers.
- Declares fatal/error helpers, signal handler installation, formatted allocation, stat, sysfs-style file readers, blkid check, prompt helper, and CRC32C.
- Provides `xmalloc`, `xopenat`, `xioctl`, and `xclose` fail-fast wrappers.
- Renames `crc32c` to `bch_crc32c` to avoid static-link conflicts with libblkid.

# sources/distributed-fs/ceph-client/fs/ufs/swab.h

`swab.h` centralizes endian conversion for UFS on-disk integer types. Runtime conversion is selected from `UFS_SB(sb)->s_bytesex`, which `super.c` establishes during magic-number probing.

It defines `BYTESEX_LE` and `BYTESEX_BE`, plus inline converters for `__fs64`, `__fs32`, and `__fs16`: `fs64_to_cpu()`, `cpu_to_fs64()`, `fs32_to_cpu()`, `cpu_to_fs32()`, `fs16_to_cpu()`, and `cpu_to_fs16()`. In-place arithmetic helpers `fs32_add()`, `fs32_sub()`, `fs16_add()`, and `fs16_sub()` update filesystem-endian counters using Linux little/big-endian add primitives.

The file has no independent persistence, but callers use it whenever they read or write superblocks, cylinder groups, inode fields, directory entry lengths, and free-space counters. Its only significant dependency is `UFS_SB()` plus Linux endian helpers. The main risk is bypassing these wrappers or using them before `s_bytesex` is initialized. The comments explicitly assume UFS variants are either big-endian or little-endian. Test signals are clean mount/read/write/statfs on both endian image variants and fsck-compatible metadata after mutations.

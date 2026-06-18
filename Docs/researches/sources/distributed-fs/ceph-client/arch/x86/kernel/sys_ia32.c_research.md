# sources/distributed-fs/ceph-client/arch/x86/kernel/sys_ia32.c

## Purpose
`sys_ia32.c` provides IA32 compatibility syscall wrappers on x86-64, converting 32-bit ABI arguments and structures into native kernel calls for large-file offsets, stat64, mmap, and clone.

## Important APIs, Types, And Functions
Wrappers include `ia32_truncate64`, `ia32_ftruncate64`, `ia32_pread64`, `ia32_pwrite64`, `ia32_fadvise64_64`, `ia32_readahead`, `ia32_sync_file_range`, `ia32_fadvise64`, and `ia32_fallocate`. IA32 emulation also defines `cp_stat64()`, stat64 wrappers, `struct mmap_arg_struct32`, `ia32_mmap`, and `ia32_clone`.

## Control Flow
Most functions combine high/low 32-bit words into 64-bit offsets or lengths and call native `ksys_*` helpers. `cp_stat64()` translates `kstat` to the i386 `stat64` ABI in a user-write window. `ia32_mmap()` copies the six-argument block and validates page-aligned offset. `ia32_clone()` maps backwards i386 clone arguments into `kernel_clone_args`.

## State, Persistence, Dependencies, Integration
No persistent state is owned. Dependencies include compat syscall macros, VFS/stat helpers, native `ksys_*`, user namespace uid/gid conversion, user access, and clone internals. IA32 syscall tables use these for ABI-mismatched syscalls.

## Risks And Test Signals
Endian and high/low composition mistakes corrupt large offsets. `stat64` layout must match i386. Clone TID/TLS/signal semantics must match the backwards ABI. Test IA32 large-file operations beyond 4 GiB, stat64 large inode/dev values, mmap argument blocks, bad offsets, and clone with TLS and TID pointers.

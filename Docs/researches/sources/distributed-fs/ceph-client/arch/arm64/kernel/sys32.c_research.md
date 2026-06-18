## sources/distributed-fs/ceph-client/arch/arm64/kernel/sys32.c

### Purpose
`sys32.c` implements AArch32 compat syscall wrappers and builds the compat syscall table used when 32-bit tasks issue SVC on ARM64.

### Important APIs, Types, And Functions
It defines compat wrappers for `aarch32_statfs64`, `aarch32_fstatfs64`, `aarch32_mmap2`, `aarch32_pread64`, `aarch32_pwrite64`, `aarch32_truncate64`, `aarch32_ftruncate64`, `aarch32_readahead`, `aarch32_fadvise64_64`, `aarch32_sync_file_range2`, `aarch32_fallocate`, and `compat_sys_call_table`.

### Control Flow
The wrappers normalize ARM OABI-compatible statfs64 sizes, convert `mmap2` 4 KiB units to page units after alignment validation, reconstruct split 64-bit arguments according to kernel endianness, and delegate to generic `ksys_*` or `kcompat_*` helpers. The table maps compat syscall numbers to `__arm64_*` wrappers, defaulting to `__arm64_sys_ni_syscall`.

### State, Persistence, And Dependencies
State changes are delegated to generic file, VM, and filesystem syscalls. This file itself owns only table initialization.

### Integration Points
It is used by `do_el0_svc_compat` in `syscall.c`, generic compat syscall helpers, AArch32 signal-return entries, and generated `asm/syscall_table_32.h`.

### Risks
Endian-sensitive split-argument reconstruction can corrupt offsets or lengths. The ARM statfs64 ABI quirk is compatibility-sensitive. `mmap2` page-shift handling must be correct for non-4K kernels.

### Test Signals
Run 32-bit userspace syscall suites on 4K/16K/64K page kernels, big- and little-endian builds where applicable, large-file I/O tests, statfs64 ABI compatibility tests, and compat signal-return tests.

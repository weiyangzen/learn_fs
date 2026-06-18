<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/linux32.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/linux32.c

### Purpose
`linux32.c` implements 32-bit compatibility syscall wrappers for 64-bit MIPS kernels. It reconstructs split 64-bit arguments using ABI endianness rules and delegates to native kernel syscall helpers.

### Important APIs, Types, And Functions
Key wrappers include `sys32_truncate64`, `sys32_ftruncate64`, `sys32_llseek`, `sys32_pread`, `sys32_pwrite`, `sys32_personality`, `sys32_readahead`, `sys32_sync_file_range`, `sys32_fadvise64_64`, and `sys32_fallocate`. The central helper macro is `merge_64()`, which differs for `__MIPSEB__` and `__MIPSEL__`.

### Control Flow
Each syscall wrapper receives 32-bit ABI argument words, merges high/low halves into a 64-bit offset or length where needed, and calls the common helper such as `ksys_truncate`, `ksys_ftruncate`, `sys_llseek`, `ksys_pread64`, `ksys_pwrite64`, or `ksys_fallocate`. `sys32_personality()` translates between `PER_LINUX32` and `PER_LINUX` on input and output to preserve 32-bit user ABI behavior.

### State, Persistence, And Dependencies
The wrappers do not maintain persistent state except via delegated syscalls. They depend on compat syscall ABI definitions, uaccess, filesystem helpers, personality flags, and correct MIPS endian argument ordering.

### Integration Points
This file is linked into MIPS compat syscall tables and used by 32-bit user programs running on a 64-bit kernel. It integrates with VFS, mm, ipc, networking includes, and generic compat infrastructure.

### Risks
Wrong `merge_64()` ordering silently corrupts offsets and lengths. The dummy padding arguments must match the o32 syscall ABI; changing prototypes can break syscall table calling conventions. Personality translation must preserve legacy user-space expectations.

### Test Signals
Run 32-bit compat tests for large-file truncate/ftruncate, llseek, pread/pwrite beyond 4 GiB, sync_file_range, fadvise64_64, fallocate, readahead, and personality transitions on both big-endian and little-endian MIPS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/linux32.c -->

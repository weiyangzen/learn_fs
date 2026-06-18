# sources/distributed-fs/ceph-client/arch/powerpc/kernel/sys_ppc32.c

## Purpose
Implements 32-bit PowerPC syscall wrappers whose 64-bit arguments are split across constrained register pairs. This supports both native PPC32 and compat calls on PPC64.

## Important APIs, Types, and Functions
- `PPC32_SYSCALL_DEFINE*` maps to native `SYSCALL_DEFINE*` or compat `COMPAT_SYSCALL_DEFINE*`.
- Wrappers include `ppc_pread64`, `ppc_pwrite64`, `ppc_readahead`, `ppc_truncate64`, `ppc_ftruncate64`, `ppc32_fadvise64`, `ppc_sync_file_range2`, and native PPC32 `ppc_fallocate`.
- `merge_64(high, low)` reconstructs 64-bit offsets/lengths.

## Control Flow and State
Each syscall wrapper decodes split arguments, discards ABI padding registers where needed, and calls the generic `ksys_*` implementation.

## State and Persistence Behavior
No local persistent state. Effects are those of the delegated filesystem/memory syscalls.

## Dependencies and Integration Points
Depends on syscall ABI tables, `asm/syscalls.h`, compat syscall infrastructure, and generic kernel syscall helpers.

## Risks
Wrong register pairing silently targets the wrong file offset or length. Compat/native macro differences must match `ARCH_HAS_SYSCALL_WRAPPER` and table generation.

## Test Signals
Run 32-bit userspace on 32-bit and 64-bit kernels for large-file pread/pwrite, truncate/ftruncate, fallocate, fadvise, readahead, and sync_file_range2 with offsets above 4 GiB.

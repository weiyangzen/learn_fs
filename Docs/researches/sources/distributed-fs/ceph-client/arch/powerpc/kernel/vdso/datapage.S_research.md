# sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/datapage.S

## Purpose
Provides vDSO accessors for the PowerPC vDSO architecture data page: available syscall bitmap and timebase frequency.

## Important APIs, Types, And Functions
Exports `__kernel_get_syscall_map(unsigned int *syscall_count)` and `__kernel_get_tbfreq(void)`. It uses `get_datapage`, `CFG_SYSCALL_MAP32`, `CFG_SYSCALL_MAP64`, `CFG_TB_TICKS_PER_SEC`, and `NR_syscalls`.

## Control Flow
`__kernel_get_syscall_map` loads the arch data page, returns a pointer to the 32-bit or 64-bit syscall map, and optionally stores `NR_syscalls` through the caller's pointer. `__kernel_get_tbfreq` returns the 64-bit timebase frequency, using `r3/r4` for 32-bit ABI return and `r3` for 64-bit.

## State And Persistence
Reads shared vDSO data populated by the kernel at boot and updated as needed. It does not modify state.

## Dependencies And Integration Points
Depends on `vdso_setup_syscall_map` in `vdso.c`, generic vDSO data placement, PowerPC ABI return conventions, and the linker scripts that export these functions.

## Risks And Edge Cases
The syscall bitmap ordering is big-bit-first within 32-bit words, unlike native kernel bitops. 32-bit callers rely on correct high/low return register handling for the timebase frequency.

## Test Signals
Userspace can compare the syscall map against known implemented syscalls and compare `__kernel_get_tbfreq` with kernel-exposed timebase frequency. ABI tests should run under 32-bit and 64-bit tasks.

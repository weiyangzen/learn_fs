# sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/gettimeofday.S

## Purpose
Provides assembly wrappers for PowerPC vDSO time functions, calling generic C vDSO implementations while satisfying PowerPC stack, TOC, and error conventions.

## Important APIs, Types, And Functions
Exports `__kernel_gettimeofday`, `__kernel_clock_gettime`, `__kernel_clock_gettime64` on 32-bit, `__kernel_clock_getres`, `__kernel_clock_getres_time64` on 32-bit, and `__kernel_time`. The `cvdso_call` macro obtains `vdso_u_time_data`, saves LR and 64-bit TOC, and handles error conversion where needed.

## Control Flow
Each exported wrapper creates two minimum stack frames, passes the vDSO time data pointer in the correct argument register, calls its `__c_kernel_*` helper, restores saved registers, clears SO, and for integer-returning functions sets SO and negates negative error codes. `__kernel_time` uses a variant that does not treat the returned time value as an errno status.

## State And Persistence
Reads the kernel-updated vvar time data page and optionally writes caller-provided result structures. It does not persist software state.

## Dependencies And Integration Points
Depends on generic C vDSO time helpers included via the Makefile, PowerPC `get_datapage`, ABI-specific timespec layouts, and exported linker-script symbol versions used by libc.

## Risks And Edge Cases
The wrapper must preserve TOC and LR and provide unwind-safe CFI. 32-bit time64 and old 32-bit timespec variants must call the matching C helper. Error/SO behavior is part of userspace ABI.

## Test Signals
Run vDSO time selftests comparing against syscalls for supported clock ids, invalid clock ids, null result pointers, 32-bit compat time64 behavior, and ABI unwind through vDSO frames.

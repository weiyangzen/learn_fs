# sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/sigtramp32.S

## Purpose
Provides 32-bit PowerPC signal and realtime-signal return trampolines in the vDSO, plus `.eh_frame` unwind descriptions for signal frames.

## Important APIs, Types, And Functions
Exports `__kernel_sigtramp32` and `__kernel_sigtramp_rt32`. The trampolines issue `__NR_sigreturn` and `__NR_rt_sigreturn`. It defines DWARF helper macros `cfa_save`, `rsave`, `vsave_msr*`, `vsave`, `EH_FRAME_GEN`, `EH_FRAME_FP`, and `EH_FRAME_VMX`.

## Control Flow
Signal handlers return into the trampoline, which loads the proper syscall number in `r0` and executes `sc`. Preceding NOPs widen unwind coverage for tools that subtract one from return addresses. The `.eh_frame` section describes where GPRs, LR, CR, FP registers, and optional VMX registers can be found via the saved `pt_regs` pointer in the signal frame.

## State And Persistence
The trampoline itself has no mutable state. It relies on the kernel-created user signal frame and `pt_regs` layout.

## Dependencies And Integration Points
Depends on PowerPC 32-bit signal-frame layouts, syscall numbers, DWARF register numbering, optional `CONFIG_ALTIVEC`, vDSO linker exports `VDSO_sigtramp32` and `VDSO_sigtramp_rt32`, and libc/unwinder signal-frame recognition.

## Risks And Edge Cases
Unwind offsets are ABI-sensitive and differ between plain and realtime signal frames. VMX unwind expressions depend on MSR bits and saved VMX area layout. Any mismatch breaks debuggers, profilers, exception unwinders, and signal return.

## Test Signals
Run signal handling tests for 32-bit tasks, `sigreturn` and `rt_sigreturn`, GDB/libunwind backtraces through signal frames, Altivec register unwinding, and `readelf --debug-dump=frames` validation.

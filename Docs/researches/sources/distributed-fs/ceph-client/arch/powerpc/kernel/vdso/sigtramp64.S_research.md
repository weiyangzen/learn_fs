# sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/sigtramp64.S

## Purpose
Provides the 64-bit PowerPC realtime signal trampoline in the vDSO and associated unwind metadata for signal frames.

## Important APIs, Types, And Functions
Exports `__kernel_start_sigtramp_rt64` and `__kernel_sigtramp_rt64`. The first calls the signal handler via `bctrl`; the second adjusts the stack by `__SIGNAL_FRAMESIZE`, invokes `__NR_rt_sigreturn`, and has `.eh_frame` metadata built from the same family of GPR, FP, and VMX DWARF expression macros as the 32-bit file.

## Control Flow
The kernel jumps to `__kernel_start_sigtramp_rt64`; the handler returns indirectly to `__kernel_sigtramp_rt64`, which performs the realtime signal-return syscall. Extra aligned words mimic the historical stack trampoline layout for older unwinders. The FDE describes register locations through a saved `pt_regs` pointer.

## State And Persistence
No mutable state. Runtime behavior depends on the signal frame constructed by the kernel and on userland returning through the prescribed trampoline.

## Dependencies And Integration Points
Depends on 64-bit PowerPC signal ABI, `__SIGNAL_FRAMESIZE`, syscall numbers, DWARF register numbering, optional Altivec save areas, and the linker script symbol `VDSO_sigtramp_rt64`.

## Risks And Edge Cases
The split trampoline entry is ABI-sensitive because libc uses `__kernel_sigtramp_rt64` as the return address for frame identification. Endian-specific CR offsets and VMX pointer indirection must match `pt_regs` and vector-save layouts.

## Test Signals
Signal tests in 64-bit tasks, unwinder/GDB backtraces through signal handlers, Altivec signal-frame unwind checks, and `readelf` verification of the FDE and exported trampoline symbols provide coverage.

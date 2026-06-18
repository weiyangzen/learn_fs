## sources/distributed-fs/ceph-client/arch/mips/kernel/signal_o32.c

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/signal_o32.c` implements legacy and realtime signal frames for the MIPS o32 ABI on 64-bit kernels. It uses `struct sigcontext32` and compat user structures while sharing the common FP save/restore machinery through ABI-specific offsets.

### Important APIs, Types, And Functions
Frame types are `struct sigframe32`, `struct ucontext32`, and `struct rt_sigframe32`. Core helpers are `setup_sigcontext32()`, `restore_sigcontext32()`, `setup_frame_32()`, `setup_rt_frame_32()`, `sys32_sigreturn()`, and `sys32_rt_sigreturn()`. The ABI descriptor is `mips_abi_32`, with `__NR_O32_restart_syscall`, compat sigcontext offsets, and `vdso_image_o32`.

### Control Flow
Frame setup obtains an aligned user frame with `get_sigframe()`, copies GPRs, HI/LO, optional DSP accumulators, protected FP context, compat sigmask, and optional compat siginfo/ucontext. It then places handler arguments in `$a0-$a2`, sets `$sp`, `$ra`, `$25`, and EPC. Return paths validate the frame on `$sp`, copy back the compat mask, restore registers and FP state with `restore_sigcontext32()`, restore altstack for realtime frames, and transfer to `syscall_exit`.

### State, Persistence, And Dependencies
State is the user-visible o32 signal ABI: frame padding, argument-save slots, compat signal mask conversion, `struct sigcontext32` offsets, and o32 VDSO sigreturn locations. Runtime state includes the current thread register frame, DSP registers, FPU/MSA context, blocked mask, and altstack. Dependencies include `asm/compat-signal.h`, `asm/dsp.h`, `asm/sim.h`, `asm/syscalls.h`, `signal-common.h`, and native protected FP helpers from `signal.c`.

### Integration Points
The ABI descriptor is used by native `signal.c` dispatch for o32 tasks. This file pairs with `signal32.c` for compat sigaction/sigsuspend and with `vdso.c` for the o32 VDSO image. It also integrates with DSP and FPU context management in `traps.c`.

### Risks
o32 layout is especially sensitive because old user programs depend on the legacy frame and argument-save area. DSP fields must only be touched when the CPU supports DSP. Compat mask conversion and handler pointer sizes must remain exact. `restore_sigcontext32()` changes control registers from user memory, so malformed frames must be caught before returning to user mode.

### Test Signals
Exercise legacy and realtime o32 handlers, `sigreturn` and `rt_sigreturn`, alternate stacks, DSP register preservation, FPU/MSA preservation through compat offsets, bad sigreturn frames, old one-word signal masks, and restart syscall number behavior.

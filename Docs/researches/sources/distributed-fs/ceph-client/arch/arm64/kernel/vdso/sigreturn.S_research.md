## sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso/sigreturn.S

### Purpose
`vdso/sigreturn.S` provides the native AArch64 VDSO signal-return trampoline `__kernel_rt_sigreturn` used when userspace does not provide `SA_RESTORER`.

### Important APIs, Types, And Functions
It defines `__kernel_rt_sigreturn`, issues `mov x8,#__NR_rt_sigreturn` followed by `svc #0`, includes a deliberate leading `nop`, and emits AArch64 feature notes. CFI directives are intentionally disabled.

### Control Flow
Signal-handler return branches to the trampoline, the trampoline loads the rt_sigreturn syscall number into `x8`, enters the kernel with SVC, and never returns normally because the kernel restores the interrupted context.

### State, Persistence, And Dependencies
No writable state exists. The code sequence is ABI-visible to unwinders and debuggers.

### Integration Points
Mapped by `vdso.c`, exported by `vdso.lds.S`, and relied on by glibc/libgcc/libunwind/GDB signal unwinding heuristics and kernel signal delivery.

### Risks
Changing the instruction sequence, adding BTI through normal function macros, or re-enabling incomplete CFI can break unwinding or signal return. The leading NOP exists for unwinders that subtract one from return IP.

### Test Signals
Run signal handling and unwinding tests with GDB, libgcc, libunwind, pthread cancellation, BTI builds, and VDSO symbol inspection.

# sources/distributed-fs/ceph-client/arch/arm64/include/asm/ptrace.h
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/ptrace.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/ptrace.h` Defines arm64 exception register layout, processor-state constants, compat ptrace mappings, syscall sentinel state, and register accessor helpers. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
CurrentEL_* and INIT_PSTATE_* constants, AArch32 PSR bits, NO_SYSCALL, struct pt_regs, in_syscall(), forget_syscall(), user/compat mode predicates, regs_irqs_disabled(), user_stack_pointer(), regs_get_register(), pt_regs_read/write_reg(), regs_return_value(), regs_get_kernel_argument(), valid_user_regs(), instruction_pointer(), frame_pointer(), profile_pc(). The file is 365 lines / 9532 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Exception entry stores user_pt_regs as the prefix of pt_regs plus orig_x0, syscallno, PMR, SDEI TTBR, and stackframe metadata. Accessors decode offsets, sign-extend compat returns, and hide architectural register 31 as XZR for instruction emulation.

### State, Persistence, And Dependencies
State is per-exception stack pt_regs. It persists only while handling a trap/syscall/signal/ptrace stop but is user-visible through ptrace and signal frames. Depends on cpufeature, uapi ptrace, GIC priority definitions, stacktrace frame metadata, bug/types; integrates with syscall tracing, audit, seccomp, signal delivery, ptrace, kprobes, traps, stack unwinding, and scheduler register display.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
pt_regs layout is ABI and assembly critical; wrong compat PSR conversion or return sign-extension breaks 32-bit tasks; PMR/IRQ predicates affect lockdep and interrupt state accounting.

### Test Signals
Run ptrace, signal, syscall tracing/audit/seccomp, compat, kprobes, stacktrace, and irq-priority masking tests; verify static_assert alignment.

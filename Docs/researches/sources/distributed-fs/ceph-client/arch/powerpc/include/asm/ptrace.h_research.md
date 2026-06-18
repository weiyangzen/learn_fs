# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ptrace.h

Purpose: This header defines the kernel PowerPC `pt_regs` stack-frame ABI and helper functions used by syscall tracing, exception handling, probes, stack inspection, and user register access.

Important APIs/types/functions: `struct pt_regs` overlays `struct user_pt_regs` with named GPR/NIP/MSR/CTR/LR/XER/CCR/orig/result/trap/DAR/DSISR fields plus config-specific SOFTE/MQ, PPR/exit/KUAP/AMR/IAMR padding, and BookE MAS/SRR/CSRR/DSRR fields. It defines stack frame sizes for 32/64-bit and ELF ABI variants, redzone sizes, signal frame sizes, `profile_pc`, syscall trace entry/leave declarations, return-register mutation helpers, `instruction_pointer`, `user_stack_pointer`, `user_mode`, `force_successful_syscall_return`, `current_pt_regs`, trap flag helpers, syscall success/return value helpers, recoverability helpers around `MSR_RI`, single-step capability macros, register query APIs, `regs_get_register`, stack bounds helpers, `regs_get_kernel_stack_nth`, and `regs_get_kernel_argument`.

Control flow: Exception and syscall entry code saves volatile state into `pt_regs`; helpers mutate return NIP/MSR and invalidate PACA saved return copies when needed. Syscall tracing inspects traps, computes success/error return values, and can force no-error handling. Kprobes/ftrace read registers by offset and extract up to eight kernel arguments.

State and persistence: `pt_regs` lives on the kernel stack for an exception/syscall frame. Trap low bits encode flags such as no-restart. Return MSR/NIP updates are persistent until exception return. Book3S 64-bit updates clear `local_paca` SRR/HSRR validity caches.

Dependencies and integration points: It includes UAPI ptrace layout, register definitions, asm constants, PACA, thread info, and kernel stack helpers. It is ABI-coupled to assembly offsets, ptrace userspace layout, syscall tracing, kprobes, ftrace, signal delivery, and exception return.

Risks and test signals: Field order and size are stack/ptrace ABI and must remain aligned. `MAX_REG_OFFSET` excludes fields past `dsisr`, so trace users must handle inaccessible offsets. Syscall success differs for SCV versus classic syscall. Tests include ptrace register tests, syscall tracing, signal delivery, kprobe/ftrace argument extraction, stack unwinding, SCV/classic syscall return semantics, and BookE/Book3S build variants.

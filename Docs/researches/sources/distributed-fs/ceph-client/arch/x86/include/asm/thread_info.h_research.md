<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/thread_info.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/thread_info.h

Purpose: defines low-level x86 per-thread flags/status and kernel stack padding used by entry, scheduler, syscall, and context-switch code. Important content includes `TOP_OF_KERNEL_STACK_PADDING`, `struct thread_info`, `INIT_THREAD_INFO`, supported TIF declarations, x86-specific TIF bits, `_TIF_WORK_CTXSW*` masks, `STACK_WARN`, `arch_within_stack_frames()`, `TS_COMPAT`, `TS_I386_REGS_POKED`, and `in_ia32_syscall()`.

Control flow: entry and scheduler code inspect TIF masks to decide return-to-user work, speculation updates, FPU loading, I/O bitmap switching, CPUID/TSC restrictions, and single/block stepping. Stack validation uses frame pointers to check whether copies stay within one stack frame. Compat syscall code marks 32-bit syscall state in `status`.

State and persistence: `thread_info` lives with each task and stores flags, syscall work flags, synchronous status, and current CPU on SMP. Dependencies include generic TIF infrastructure, page/thread size, entry assembly offsets, frame pointers, compat syscall code, and stackleak/usercopy validation.

Risks: bit assignments and masks are entry ABI; wrong padding breaks `pt_regs` placement on 32-bit/FRED; stack-frame checks can produce false positives/negatives. Test signals include syscall return work, context-switch mitigation flags, compat syscall status, hardened usercopy stack checks, FRED builds, and 32-bit vm86/SYSENTER corner cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/thread_info.h -->

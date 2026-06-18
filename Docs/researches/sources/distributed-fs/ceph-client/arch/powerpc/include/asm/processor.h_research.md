# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/processor.h

Purpose: This header defines PowerPC processor and thread state visible to core kernel code: task/thread register state, floating point/vector/SPE/TM state, debug state, initial thread setup, task register accessors, idle hooks, prefetch helpers, alignment emulation hooks, and VMX usercopy entry points.

Important APIs/types/functions: Key definitions include FPR/VSX layout macros, default PPR setup, PREP/CHRP legacy platform constants, `start_thread`, `struct thread_fp_state`, `struct thread_vr_state`, `struct debug_reg`, and the large `struct thread_struct`. `thread_struct` stores kernel stack pointer, saved regs, BookE exception scratch, page directory/RTAS/KUAP fields, debug registers, FP/Altivec/VSX/SPE/TM checkpointed state, KVM pointers, DSCR/FSCR/TIDR, EBB/perf state, and DEXCR state depending on config. Other APIs include `INIT_THREAD`, `task_pt_regs`, `KSTK_EIP`, `KSTK_ESP`, prctl helpers for FPEXC/endian/unaligned/DEXCR, FP/VR load-store functions, `spin_begin`, `spin_cpu_relax`, `spin_end`, stack validation helpers, `prefetch`, `prefetchw`, idle stop functions, `fix_alignment`, math emulation functions, and VMX copy helpers.

Control flow: Scheduler and fork/exec code initialize `thread_struct`, context-switch code uses the saved FP/vector/SPE/TM flags and state, ptrace/prctl code reads or sets per-task modes, idle code selects platform stop/nap paths, and exception handling uses alignment/math emulation and stack validation helpers.

State and persistence: `thread_struct` is persistent per task and is the owner for lazy-loaded processor facilities, debug registers, transactional checkpoint state, DSCR inheritance, DEXCR-on-exec behavior, and saved register pointers. `INIT_THREAD` defines boot task initial state.

Dependencies and integration points: It includes VDSO processor definitions, `reg.h`, thread info, ptrace, hardware breakpoints, task-size headers, KVM, perf/hw breakpoint, MMU, idle, VMX/VSX/SPE, transactional memory, KUAP/KUEP, and BookE/Book3S variants.

Risks and test signals: Layout and alignment are ABI-sensitive for context switch and assembly offsets. Lazy facility flags must match save/restore code or user state can leak/corrupt. TM checkpoint state is especially sensitive. Tests include context-switch stress with FP/Altivec/VSX/SPE/TM, ptrace/prctl mode tests, hardware breakpoints, stack unwinding validation, idle/resume, alignment emulation, and 32/64-bit build variants.

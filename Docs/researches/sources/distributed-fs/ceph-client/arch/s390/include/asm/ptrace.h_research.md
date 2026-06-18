# sources/distributed-fs/ceph-client/arch/s390/include/asm/ptrace.h

Purpose: This header defines s390 PSW bit encodings, `pt_regs` layout, PER debug structures, ptrace flags, and register accessor helpers.

Important APIs/types/functions: `PIF_*` flags, 32-bit and 64-bit PSW masks, `struct psw_bits`, `psw32_t`, `struct pt_regs`, `struct per_regs`, `struct per_event`, `struct per_struct_kernel`, PER masks, pt_regs flag helpers, `update_cr_regs()`, single/block-step support, `profile_pc`, `user_mode()`, `regs_return_value()`, instruction pointer helpers, register name/offset queries, stack pointer helpers, `regs_get_register()`, kernel stack/argument readers, and `regs_set_return_value()` are exposed.

Control flow: Exception, syscall, tracing, and ptrace code save user-visible registers in `pt_regs`, inspect PSW bits for user/kernel mode and IRQ state, expose registers by offset/name, and use PER structures for branch/store/ifetch/transaction debug events.

State and persistence: Persistent state is on task kernel stacks in `pt_regs` during entry/exit and in per-thread PER debug structures. Flags annotate syscall, adjusted PSW, guest fault, and ftrace-full-reg states.

Dependencies and integration points: It depends on UAPI ptrace layouts, thread info, TPI info, storage-key constants, and generic profiling/ptrace consumers.

Risks and test signals: The `pt_regs` and PSW layouts are ABI-sensitive for signals, ptrace, BPF, perf, ftrace, and KVM. Tests should include ptrace register get/set, syscall tracing, single/block step, PER events, signal frames, ftrace full regs, and BPF/perf register access.

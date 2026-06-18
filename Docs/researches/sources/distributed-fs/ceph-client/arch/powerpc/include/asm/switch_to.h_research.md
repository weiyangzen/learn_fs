<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/switch_to.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/switch_to.h

Purpose: Declares PowerPC context-switch and lazy processor-state restore hooks.

Important APIs/types/functions: `__switch_to`, `_switch`, `switch_to` macro, debug register switch, math/vector/VSX/SPE/TM restore helpers, and `flush_all_to_thread()`. Source-visible declarations include: #define _ASM_POWERPC_SWITCH_TO_H; struct thread_struct;; struct task_struct;; struct pt_regs;; extern struct task_struct *__switch_to(struct task_struct *,; struct task_struct *);; #define switch_to(prev, next, last) ((last) = __switch_to((prev), (next))); extern struct task_struct *_switch(struct thread_struct *prev,.

Control flow: scheduler switches task_struct/thread state, then lazy restore paths reload math/vector/debug/TM state as needed. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: per-thread CPU extended state persists in `thread_struct` and hardware registers. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/sched.h>, #include <asm/reg.h>. Integrated with scheduler, ptrace, signal, KVM, debug registers, FPU/Altivec/VSX/SPE, and transactional memory.

Risks: lazy restore and flush ordering are correctness-critical for ptrace, signal frames, and context isolation. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 133 lines, 3230 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/switch_to.h -->

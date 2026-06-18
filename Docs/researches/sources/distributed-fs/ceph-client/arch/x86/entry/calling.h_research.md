<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/calling.h -->
# sources/distributed-fs/ceph-client/arch/x86/entry/calling.h

Purpose: This assembly header defines x86 entry calling conventions, register save/restore macros, PTI CR3 switching helpers, speculation mitigation helpers, stack erasure hooks, percpu base loading, and thunk generation for both 64-bit and 32-bit entry code.

Important APIs/types/functions: Major macros include `PUSH_REGS`, `CLEAR_REGS`, `PUSH_AND_CLEAR_REGS`, `POP_REGS`, `SWITCH_TO_KERNEL_CR3`, `SWITCH_TO_USER_CR3_NOSTACK`, `SWITCH_TO_USER_CR3_STACK`, `SAVE_AND_SWITCH_TO_KERNEL_CR3`, `PARANOID_RESTORE_CR3`, `IBRS_ENTER`, `IBRS_EXIT`, `FENCE_SWAPGS_USER_ENTRY`, `FENCE_SWAPGS_KERNEL_ENTRY`, `STACKLEAK_ERASE_NOCLOBBER`, `SAVE_AND_SET_GSBASE`, `STACKLEAK_ERASE`, `LOAD_CPU_AND_NODE_SEG_LIMIT`, `GET_PERCPU_BASE`, and `THUNK`. Constants define PTI page-table and PCID mask bits.

Control flow: Consumers expand these macros in syscall, interrupt, exception, and thunk paths. Register macros construct or tear down `pt_regs` frames. PTI macros inspect and mutate CR3, including PCID no-flush behavior and per-CPU user PCID flush masks. IBRS and swapgs macros insert alternative-patched speculation barriers depending on CPU features and mitigation config. Thunk macros preserve argument registers around C calls and return through the architecture's safe return sequence.

State and persistence: The macros manipulate architectural state: general registers, stack frames, CR3, MSR_IA32_SPEC_CTRL, GS base, percpu offsets, and optional stackleak state. Persistent state touched indirectly includes per-CPU TLB state and speculation-control shadow variables.

Dependencies and integration points: It depends on jump labels, unwind hints, CPU feature alternatives, page types, percpu definitions, asm offsets, processor flags, ptrace ABI offsets, MSR helpers, and nospec branch macros. It is included by `entry.S`, `entry_32.S`, and 64-bit entry files.

Risks and test signals: This header is central to entry safety; offset or mitigation mistakes can corrupt pt_regs, return on the wrong CR3, leak registers to speculation, or break unwind metadata. Tests should include objtool validation, PTI on/off boots, PCID and non-PCID systems, IBRS and swapgs mitigation permutations, stackleak builds, SMP and !SMP builds, and syscall/interrupt stress with unwinding enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/calling.h -->

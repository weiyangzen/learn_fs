## sources/distributed-fs/ceph-client/arch/s390/include/asm/stacktrace.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/stacktrace.h` is a s390 stack walking
helpers in the s390 ceph-client Linux source snapshot. It has 261 lines and 8086 bytes; exported
UAPI contract: no.

### Important APIs, Types, And Functions
stack-frame layouts, stack type classification, inline stack pointer helpers, and call-with-return-
address assembly macros
Important macros/constants: `_ASM_S390_STACKTRACE_H`, `current_frame_address()`, `CALL_FMT_0`, `CALL_FMT_1`, `CALL_FMT_2`, `CALL_FMT_3`, `CALL_FMT_4`, `CALL_FMT_5`, `CALL_CLOBBER_5`, `CALL_CLOBBER_4`, `CALL_CLOBBER_3`, `CALL_CLOBBER_2`, `CALL_CLOBBER_1`, `CALL_CLOBBER_0`, `CALL_LARGS_0(...)`, `CALL_LARGS_1(t1, a1)`, `CALL_LARGS_2(t1, a1, t2, a2)`, `CALL_LARGS_3(t1, a1, t2, a2, t3, a3)`, `CALL_LARGS_4(t1, a1, t2, a2, t3, a3, t4, a4)`, `CALL_LARGS_5(t1, a1, t2, a2, t3, a3, t4, a4, t5, a5)`; plus 21 more.
Important types/layouts: `stack_frame_user`, `stack_frame_vdso_wrapper`, `perf_callchain_entry_ctx`, `pt_regs`, `stack_info`, `task_struct`, `stack_frame`, `stack_type`.
Important declarations or inline helpers: `arch_stack_walk_user_common`, `get_stack_info`, `current_frame_address`, `asm`, `volatile`, `on_stack`, `get_stack_pointer`.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
generic stacktrace, perf callchains, user stack walking, unwinder, ftrace, and exception stacks.
Direct include dependencies detected here: `linux/stacktrace.h`, `linux/uaccess.h`,
`linux/ptrace.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for generic stacktrace, perf callchains, user
stack walking, unwinder, ftrace, and exception stacks. For UAPI files, the integration point also
includes headers_install and userspace programs compiled against the exported layout.

### Risks
frame-layout mismatches can hide callchain frames or unwind into invalid memory

### Test Signals
perf callchains, live stack traces, kprobes/ftrace, IRQ/NMI stack unwinding, and user unwinds

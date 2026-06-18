# sources/distributed-fs/ceph-client/arch/mips/include/asm/ptrace.h

## sources/distributed-fs/ceph-client/arch/mips/include/asm/ptrace.h

### Purpose
`ptrace.h` defines MIPS saved exception/syscall register layout and helper APIs used by ptrace, kprobes, stack unwinding, profiling, syscall tracing, and die/oops handling.

### Important APIs, Types, And Functions
The key type is `struct pt_regs`, including saved syscall args for 32-bit, GPRs, CP0 status/cause/EPC/bad address, HI/LO, optional SmartMIPS ACX, and optional Octeon MTM/MTP registers. Helpers include `kernel_stack_pointer`, `instruction_pointer_set`, `regs_query_register_offset`, `regs_get_register`, `regs_within_kernel_stack`, `regs_get_kernel_stack_nth`, `ptrace_getregs`, `ptrace_setregs`, FP/watch ptrace APIs, `user_mode`, `is_syscall_success`, `regs_return_value`, `instruction_pointer`, `exception_ip`, `syscall_trace_enter`, `syscall_trace_leave`, `die`, `die_if_kernel`, `current_pt_regs`, and user-stack pointer accessors.

### Control Flow
Exception and syscall entry code saves registers into `pt_regs`. Ptrace and tracing code reads or writes that frame. Return-value helpers interpret MIPS syscall convention (`regs[7]` as error indicator). Fatal paths call `die_if_kernel` when a trap occurred outside user mode.

### State, Persistence, Dependencies, And Integration
State is the current exception frame on the kernel stack and optional architecture register blocks. Dependencies include compiler/linkage/types, ISA dependencies, page/thread info, and UAPI ptrace definitions. Integration is with `arch/mips/kernel/ptrace.c`, syscall tracing, signal delivery, stack dump, perf/profile PC collection, and seccomp/audit paths.

### Risks
The struct layout is coupled to assembly and `regoffset_table`; adding a register without updating offset users breaks ptrace. `current_pt_regs` depends on kernel-stack geometry. Error-return interpretation must stay aligned with syscall entry/exit code.

### Test Signals
Run ptrace register get/set tests across ABI variants, syscall tracing/seccomp tests, stack dump/oops tests, kprobes/perf sampling, and Octeon/SmartMIPS builds when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/ptrace.h -->

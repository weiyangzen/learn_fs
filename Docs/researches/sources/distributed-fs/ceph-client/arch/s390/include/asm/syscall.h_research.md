## sources/distributed-fs/ceph-client/arch/s390/include/asm/syscall.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/syscall.h` is a syscall register accessors
in the s390 ceph-client Linux source snapshot. It has 156 lines and 4017 bytes; exported UAPI
contract: no.

### Important APIs, Types, And Functions
helpers to read/write syscall numbers, arguments, return/error values, rollback state, audit
architecture, and vdso sigreturn recognition
Important macros/constants: `_ASM_SYSCALL_H`, `SYSCALL_FMT_0`, `SYSCALL_FMT_1`, `SYSCALL_FMT_2`, `SYSCALL_FMT_3`, `SYSCALL_FMT_4`, `SYSCALL_FMT_5`, `SYSCALL_FMT_6`, `SYSCALL_PARM_0`, `SYSCALL_PARM_1`, `SYSCALL_PARM_2`, `SYSCALL_PARM_3`, `SYSCALL_PARM_4`, `SYSCALL_PARM_5`, `SYSCALL_PARM_6`, `SYSCALL_REGS_0`, `SYSCALL_REGS_1`, `SYSCALL_REGS_2`, `SYSCALL_REGS_3`, `SYSCALL_REGS_4`; plus 3 more.
Important types/layouts: `task_struct`, `pt_regs`.
Important declarations or inline helpers: `asm`, `volatile`, `syscall_get_nr`, `syscall_set_nr`, `syscall_rollback`, `syscall_get_error`, `syscall_get_return_value`, `syscall_set_return_value`, `syscall_get_arguments`, `syscall_set_arguments`, `syscall_get_arch`, `arch_syscall_is_vdso_sigreturn`.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
ptrace, seccomp, audit, syscall tracing, restart handling, and compat mode. Direct include
dependencies detected here: `uapi/linux/audit.h`, `linux/sched.h`, `linux/err.h`, `asm/ptrace.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for ptrace, seccomp, audit, syscall tracing,
restart handling, and compat mode. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
wrong register mapping breaks tracing, seccomp, restart, and userspace ABI behavior

### Test Signals
ptrace/seccomp/audit tests, syscall restart, compat syscalls, and vdso sigreturn cases

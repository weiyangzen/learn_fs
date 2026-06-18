<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/ptrace.h

Purpose: defines SH ptrace request numbers and FDPIC/DSP selectors.

Important APIs/types/functions: `PTRACE_GETREGS`, `SETREGS`, `GETFPREGS`, `GETFDPIC`, DSP requests, and `PT_*` addresses.

Control flow: ptrace syscall switches on these request IDs to copy register/process metadata.

State and persistence: state is traced task register/FDPIC state manipulated elsewhere.

Dependencies/integration: integrates debuggers, strace, gdb, and arch ptrace code.

Risks: request-number drift breaks debugger compatibility.

Test signals: run gdb/ptrace register get/set tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/ptrace.h -->

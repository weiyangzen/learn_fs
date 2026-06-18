# sources/distributed-fs/ceph-client/arch/x86/include/asm/user_32.h

Purpose: native i386 legacy `struct user`, register, and FPU layouts used by ptrace and traditional core dumps.

Important APIs/types/functions: `struct user_i387_struct`, `struct user_fxsr_struct`, `struct user_regs_struct`, and `struct user`.

Control flow: no executable flow; core dump and ptrace code serialize/deserialize these structures.

State/persistence: describes one-page UPAGE-style core metadata plus data/stack sizing information, legacy and FXSR FPU state, segment registers, debug registers, process command, signal, and register pointer metadata.

Dependencies/integration: depends on page definitions. Integrated with i386 ptrace requests, GDB legacy core format expectations, and FPU register access.

Risks/test signals: this is ABI-stable historical layout. Test native i386 builds, GDB core reading, PTRACE_GETREGS/SETREGS, PTRACE_GETFPREGS/GETFPXREGS, debug registers, and segment register round trips.

# sources/distributed-fs/ceph-client/arch/x86/include/asm/user_64.h

Purpose: native x86_64 legacy `struct user`, register, and FPU layouts for ptrace and core dumps.

Important APIs/types/functions: `struct user_i387_struct`, `struct user_regs_struct`, and `struct user`.

Control flow: no runtime flow; layouts are consumed by ptrace/core dump paths.

State/persistence: serialized state includes 64-bit FXSAVE-compatible FPU fields, all general-purpose registers including r8-r15, segment/base fields, data/stack/text sizes, start addresses, signal, debug registers, error code, and fault address.

Dependencies/integration: depends on arch types and page definitions. Integrated with native x86_64 ptrace, ELF core dumping, GDB/crash tooling, and register note generation.

Risks/test signals: field order and width are ABI-sensitive. Test native ptrace register access, x86_64 core dumps under GDB, FP/SSE register notes, debug registers, and faulting process core metadata for `error_code` and `fault_address`.

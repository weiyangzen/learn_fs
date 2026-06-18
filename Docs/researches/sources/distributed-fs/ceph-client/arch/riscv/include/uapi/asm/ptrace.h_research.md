<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/ptrace.h

Purpose: Defines user-visible RISC-V ptrace register structures and regset constants.

Important APIs/types/functions: Defines `struct user_regs_struct`, floating-point state structs, vector state headers/data structs, NT regset constants, and alignment/size metadata.

Control flow: Ptrace, core dump, and signal tooling copy these structs between kernel and userspace.

State and persistence: User ABI state includes GPR/FPR/vector register files and regset note formats.

Dependencies and integration points: Used by debuggers, core dumps, signal context, KVM core register ABI, and libc/sysroot headers.

Risks: Layout changes break debuggers, core files, checkpoint/restore, and signal tooling.

Test signals: ptrace regset selftests, gdb/core dump tests, vector regset tests, and RV32/RV64 ABI checks.

Source read size: 169 lines, 4120 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/ptrace.h -->

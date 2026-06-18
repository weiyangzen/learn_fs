<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/seccomp.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/seccomp.h

Purpose: Connects RISC-V syscall numbering to the generic seccomp implementation.

Important APIs/types/functions: Includes `asm/unistd.h` and `asm-generic/seccomp.h`; it defines no custom filtering helpers.

Control flow: No runtime flow in this header; generic seccomp uses the architecture syscall ABI.

State and persistence: No state is stored here.

Dependencies and integration points: Used by seccomp, syscall tracing, and audit paths.

Risks: Risk is primarily include/ABI drift if syscall numbers or compat handling diverge from generic expectations.

Test signals: Seccomp filter selftests, syscall user-dispatch, audit, and compat syscall filtering on RV64.

Source read size: 20 lines, 504 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/seccomp.h -->

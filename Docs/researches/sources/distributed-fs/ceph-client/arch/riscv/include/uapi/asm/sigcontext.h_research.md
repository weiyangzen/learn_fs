<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/sigcontext.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/sigcontext.h

Purpose: Defines the RISC-V signal context ABI for saved user register state.

Important APIs/types/functions: Defines `struct sigcontext` containing user GPRs and floating/vector extension state references.

Control flow: Signal delivery writes this structure to the user signal frame; sigreturn validates and restores it.

State and persistence: Per-signal-frame persistent ABI state until sigreturn.

Dependencies and integration points: Used by signal.c, compat signal code, libc, debuggers, and checkpoint/restore.

Risks: Layout or extension-state mistakes can corrupt restored user context or break old binaries.

Test signals: Signal selftests, altstack, FPU/vector signal tests, sigreturn fuzzing, and libc ABI checks.

Source read size: 41 lines, 948 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/sigcontext.h -->

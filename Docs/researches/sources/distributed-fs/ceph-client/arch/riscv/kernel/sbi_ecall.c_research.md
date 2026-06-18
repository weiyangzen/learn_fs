<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/sbi_ecall.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/sbi_ecall.c

Purpose: Provides the low-level SBI ecall wrappers used by the higher-level SBI client code and tracepoints.

Important APIs/types/functions: Defines exported `__sbi_base_ecall()` and `__sbi_ecall()`.

Control flow: The wrappers load SBI extension/function IDs and up to six arguments into the RISC-V calling convention, execute `ecall`, collect error/value return registers, and emit SBI tracepoints around the call.

State and persistence: No global state; all state is passed through registers and returned as `long` or `struct sbiret`.

Dependencies and integration points: Used by `sbi.c` for every SBI operation; depends on `<asm/sbi.h>` ABI definitions and `trace/events/sbi.h`.

Risks: Register constraint mistakes corrupt firmware calls. Tracepoint arguments must not perturb call ABI or clobbers.

Test signals: SBI base probe at boot, tracepoint-enabled boot, all higher-level SBI operations, and compiler build coverage across RV32/RV64.

Source read size: 48 lines, 1319 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/sbi_ecall.c -->

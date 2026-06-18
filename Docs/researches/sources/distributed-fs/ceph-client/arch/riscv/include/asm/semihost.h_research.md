<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/semihost.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/semihost.h

Purpose: Declares RISC-V semihosting support used for early debug/firmware-style host calls.

Important APIs/types/functions: Provides semihosting trap encoding constants and `semihosting_enabled()`/call declarations depending on config.

Control flow: Runtime code probes or checks enablement before issuing semihosting break sequences; disabled configs compile out.

State and persistence: No durable kernel state beyond semihosting enablement policy.

Dependencies and integration points: Integrates with early console/debug paths and trap handling.

Risks: Executing semihosting traps on unsupported systems can raise illegal-instruction or breakpoint exceptions.

Test signals: QEMU semihosting boot, disabled-config build, earlycon/debug output, and trap handling tests.

Source read size: 26 lines, 596 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/semihost.h -->

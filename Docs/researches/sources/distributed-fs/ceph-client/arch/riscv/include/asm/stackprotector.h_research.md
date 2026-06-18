<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/stackprotector.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/stackprotector.h

Purpose: Defines architecture hook for stack canary initialization.

Important APIs/types/functions: Provides `boot_init_stack_canary()` as a no-op or architecture-specific bridge to generic stack protector setup.

Control flow: Called during early boot/task setup when stack protector is enabled.

State and persistence: State is per-task/global stack canary stored outside this header.

Dependencies and integration points: Integrates with compiler stack-protector instrumentation and `task_struct.stack_canary` offset generation.

Risks: Missing canary initialization weakens stack-smash detection or causes false positives.

Test signals: STACKPROTECTOR builds, boot, fork/exec, and stack protector fault injection.

Source read size: 22 lines, 589 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/stackprotector.h -->

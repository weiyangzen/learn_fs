<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/scs.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/scs.h

Purpose: Provides shadow-call-stack assembly macros for RISC-V task switch and entry code.

Important APIs/types/functions: Defines `scs_load_current`, `scs_save_current`, and no-op variants depending on `CONFIG_SHADOW_CALL_STACK`.

Control flow: When enabled, assembly loads/stores the per-task shadow call stack pointer from `thread_info`; otherwise macros assemble away.

State and persistence: Persists each task shadow-call-stack pointer in `thread_info.scs_sp`.

Dependencies and integration points: Depends on generated asm offsets and integrates with entry, switch_to, and compiler SCS instrumentation.

Risks: Wrong offset or missing save/restore corrupts return-address protection and can crash on context switch.

Test signals: SCS-enabled boot, context-switch stress, ftrace/interrupt nesting, and objdump checks for SCS macro expansion.

Source read size: 53 lines, 1090 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/scs.h -->

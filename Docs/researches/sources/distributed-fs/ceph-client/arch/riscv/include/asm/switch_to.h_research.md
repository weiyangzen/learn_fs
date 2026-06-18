<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/switch_to.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/switch_to.h

Purpose: Defines RISC-V task context switching hooks for GPR, FPU, vector, envcfg, shadow call stack, and user CFI state.

Important APIs/types/functions: Key APIs are `__switch_to()`, `switch_to()`, `__switch_to_aux()`, `fstate_save()/restore()`, `riscv_v_vstate_save/restore()` integration, and per-task CSR helpers.

Control flow: The scheduler saves current extended state, switches callee-saved GPRs in assembly, restores next task extended/CSR state, and updates shadow-call-stack/user-CFI state when enabled.

State and persistence: Persistent state is `thread_struct` register/FPU/vector/envcfg/SUM/user-CFI/SCS content.

Dependencies and integration points: Integrates with scheduler, entry assembly, FPU/vector code, asm offsets, SCS, and user CFI.

Risks: Context switch bugs corrupt registers across tasks or leak FPU/vector/CFI state.

Test signals: Scheduler stress, FPU/vector context tests, user CFI tests, SCS builds, preemption, and SMP migration.

Source read size: 128 lines, 3400 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/switch_to.h -->

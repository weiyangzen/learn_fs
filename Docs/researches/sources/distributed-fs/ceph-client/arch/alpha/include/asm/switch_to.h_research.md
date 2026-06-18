<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/switch_to.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/switch_to.h

**Purpose:** Defines Alpha's task switch macro around the low-level `alpha_switch_to` routine and MMU context post-switch check.

**Important APIs/types/functions:** `alpha_switch_to` declaration and `switch_to(P,N,L)` macro.

**Control flow:** The macro passes the physical address of the next task's PCB to PAL-aware switch code, stores the returned previous task in `L`, then runs `check_mmu_context` to finish deferred ASN work.

**State and persistence behavior:** Mutates CPU current task, PCB state, and MMU context side effects. No file-persistent state.

**Dependencies and integration points:** Depends on `task_thread_info`, `virt_to_phys`, `mmu_context.h`, and low-level assembly switch code.

**Risks:** Skipping `check_mmu_context` would leave SMP ASN locks/deferred reloads unresolved. Wrong PCB physical address corrupts context switch state.

**Test signals:** Scheduler stress, SMP context-switch tests, fork/exec workloads, and MMU context validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/switch_to.h -->

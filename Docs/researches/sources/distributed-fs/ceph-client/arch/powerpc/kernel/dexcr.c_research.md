<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/dexcr.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/dexcr.c

## Purpose
`dexcr.c` implements per-task userspace controls for the PowerPC Dynamic Execution Control Register on ISA 3.1 processors. It supports querying and changing selected DEXCR aspects through prctl and records on-exec state in the task thread.

## Important APIs, Types, And Functions
Key functions are `init_task_dexcr()`, `prctl_to_aspect()`, `get_dexcr_prctl()`, and `set_dexcr_prctl()`. Editable aspects are `DEXCR_PR_IBRTPD`, `DEXCR_PR_SRAPD`, and `DEXCR_PR_NPHIE`; `DEXCR_PR_SBHE` is queryable but not user-editable here.

## Control Flow
Early init stores the boot task's current DEXCR into `current->thread.dexcr_onexec` when `CPU_FTR_ARCH_31` is present. `prctl_to_aspect()` maps Linux `PR_PPC_DEXCR_*` selectors to bit masks. Get reports whether an aspect is editable, currently set in SPRN_DEXCR, and set in the task's on-exec mask. Set validates aspect editability, mutually exclusive set/clear controls, on-exec controls, and the `NPHIE` privilege rule, then updates both the hardware DEXCR and `task->thread.dexcr_onexec`.

## State And Persistence
State lives in the current CPU's DEXCR SPR and in `task_struct.thread.dexcr_onexec`, which persists across exec policy transitions for the task. It is not filesystem-persistent.

## Dependencies And Integration Points
It integrates with the PowerPC prctl implementation, task thread state, capability checks, CPU feature detection, and low-level DEXCR restore/exec code elsewhere.

## Risks
Allowing unprivileged clearing of `NPHIE` on exec is explicitly blocked to protect setuid hash-check behavior. Direct SPR writes affect the running thread immediately; scheduler save/restore must remain consistent. Unsupported selectors return `-ENODEV`.

## Test Signals
Prctl tests should cover get/set/clear, set-onexec/clear-onexec, invalid masks, non-editable `SBHE`, `CAP_SYS_ADMIN` enforcement for `NPHIE`, and no-op behavior on non-ISA-3.1 CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/dexcr.c -->

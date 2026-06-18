<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/suspend.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/suspend.h

Purpose: Declares CPU suspend, hibernation, and SBI HSM suspend interfaces for RISC-V.

Important APIs/types/functions: Defines `struct suspend_context`, `cpu_suspend()`, `__cpu_suspend_enter()`, resume entry points, CSR save/restore, hibernation image restore functions, and SBI suspend helpers.

Control flow: Suspend saves GPR/CSR context, calls a platform finisher, and resumes through low-level restore paths; hibernation uses separate image restore entry points.

State and persistence: Persistent suspend state includes saved callee registers, status/ie/tvec/scratch/envcfg CSRs, hibernation page backup entries, and `in_suspend`.

Dependencies and integration points: Integrates with SBI HSM/SUSP, PM core, hibernate assembly, CPU hotplug, and CSR definitions.

Risks: Incomplete CSR/register save or invalid non-retentive suspend handling corrupts resumed kernels.

Test signals: s2idle/system suspend, hibernation, CPU hotplug around suspend, SBI HSM platforms, and resume path fault injection.

Source read size: 65 lines, 1929 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/suspend.h -->

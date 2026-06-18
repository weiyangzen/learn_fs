# sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/mpc85xx_pm_ops.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/mpc85xx_pm_ops.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/mpc85xx_pm_ops.c

### Purpose
QorIQ/MPC85xx power-management operations used by SMP hotplug and timebase synchronization on non-CoreNet 85xx systems.

### Important APIs, Types, And Functions
Key functions are the PM ops in `mpc85xx_pm_ops`: CPU prepare/die, IRQ mask, and `freeze_time_base`. `mpc85xx_setup_pmc()` finds compatible GUTS nodes such as `fsl,mpc8572-guts`, `fsl,p1020-guts`, `fsl,p1021-guts`, `fsl,p1022-guts`, `fsl,p1023-guts`, `fsl,p2020-guts`, and `fsl,bsc9132-guts`, maps registers, and assigns global `qoriq_pm_ops`.

### Control Flow
`mpc85xx_smp_init()` calls this helper when the CoreNet RCPM path is not enabled. Later SMP code invokes the registered callbacks during CPU bring-up, hot-unplug, and synchronized timebase transfer.

### State, Persistence, And Dependencies
State is the static mapped GUTS pointer and global `qoriq_pm_ops`. It persists for kernel lifetime but is not durable. Dependencies include FSL GUTS layout, OF matching, and SMP PM callers.

### Integration Points
This file plugs PM register operations into the generic 85xx SMP logic in `smp.c`.

### Risks
Wrong GUTS matching or bit programming can break hotplug, timebase freeze, or interrupt masking. The static mapping assumes one matching controller.

### Test Signals
Boot matching systems, exercise secondary CPU start, CPU offline/online, kexec where relevant, and verify timebase synchronization remains monotonic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/mpc85xx_pm_ops.c -->

# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/fsl_pm.h

Purpose: Declares Freescale/QorIQ power-management modes and operation callbacks used by RCPM and platform sleep/deep-sleep code.

Important APIs, types, and functions: Defines e500 phase values, platform sleep levels, `FSL_PM_SLEEP`, `FSL_PM_DEEP_SLEEP`, `struct fsl_pm_ops`, global `qoriq_pm_ops`, and `fsl_rcpm_init()`. Operations cover IRQ mask/unmask, CPU enter/exit state, CPU up/die hooks, platform sleep entry, timebase freeze, IP-block power retention, and supported mode discovery.

Control flow: Platform initialization calls `fsl_rcpm_init()`, installs `qoriq_pm_ops`, and later CPU idle/hotplug/suspend paths invoke callbacks around state transitions and device power-retention decisions.

State and persistence: The header defines callback state only. Actual state is held by platform PM drivers and hardware registers; sleep settings persist only while the hardware remains powered/configured.

Dependencies and integration points: Integrates MPIC interrupt masking, CPU hotplug, suspend, timebase handling, and QorIQ RCPM support.

Risks: Callback ordering is critical: masking interrupts, freezing timebase, and powering IP blocks at the wrong point can break wakeup or time accounting. A null or partially populated `qoriq_pm_ops` must be handled by callers.

Test signals: Suspend and deep-sleep entry/exit, CPU hotplug through `cpu_die`/`cpu_up_prepare`, wake interrupt masking, timebase continuity, and mode discovery on boards with different RCPM revisions.

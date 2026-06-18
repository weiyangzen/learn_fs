# sources/distributed-fs/ceph-client/arch/arm/mach-milbeaut/platsmp.c

Purpose: Milbeaut M10V SMP and suspend support using a small SMP SRAM mailbox.

Important APIs/types/functions: Defines `m10v_smp_ops`, `m10v_boot_secondary()`, `m10v_smp_init()`, optional hotplug `m10v_cpu_die()`/`m10v_cpu_kill()`, `m10v_pm_ops`, `m10v_die()`, `m10v_pm_enter()`, and late `m10v_pm_init()`.

Control flow: SMP prepare maps `socionext,milbeaut-smp-sram`, logs boot CPU affinity, and fills four mailbox words with `KERNEL_UNBOOT_FLAG`. Boot resolves the logical CPU MPIDR to a hardware CPU id, writes `secondary_startup` physical address to that CPU mailbox, and sends a wakeup IPI. Hotplug die disables the GIC CPU interface, flushes coherency, and WFI; kill restores the mailbox flag. PM standby executes WFI; suspend-to-mem enters CPU PM, calls `cpu_suspend()` with `m10v_die()`, sets up reboot mappings, and jumps via physical `cpu_reset` to `cpu_resume` after wake.

State and persistence: Global state is mapped `m10v_smp_base` and a temporary `phys_reset` function pointer. Hardware state is the SMP SRAM mailbox and GIC CPU interface during hotplug/suspend.

Dependencies and integration points: Depends on DT SMP SRAM node, MPIDR affinity mapping, ARM SMP/hotplug/suspend frameworks, GIC CPU interface, idmap setup, and `socionext,milbeaut-evb` root compatible for PM registration.

Risks: Only four CPUs are supported. The code logs but otherwise ignores cluster for boot routing. Missing SRAM mapping makes SMP boot fail with `-ENXIO`. Suspend resume path is low-level and depends on physical reset/resume addresses being valid.

Test signals: Boot all CPUs on M10V, test CPU hotplug, standby and mem suspend on `socionext,milbeaut-evb`, and verify mailbox flags around offline/online.

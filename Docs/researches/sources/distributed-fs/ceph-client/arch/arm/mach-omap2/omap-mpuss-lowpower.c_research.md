<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-mpuss-lowpower.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-mpuss-lowpower.c

## Purpose
`omap-mpuss-lowpower.c` implements OMAP4/OMAP5 MPUSS CPU low-power entry, hotplug powerdown, SAR RAM setup, CPU wakeup-address programming, SCU/L2 context preparation, and early kexec-safe CPU1 startup-address setup.

## Important APIs, Types, and Functions
Public APIs include `omap4_enter_lowpower()`, `omap4_hotplug_cpu()`, `omap4_mpuss_init()`, `omap4_get_cpu1_ns_pa_addr()`, and `omap4_mpuss_early_init()`. Important structs are `struct omap4_cpu_pm_info` and `struct cpu_pm_ops`. Internal helpers include `set_cpu_wakeup_addr()`, `scu_pwrst_prepare()`, `mpuss_clear_prev_logic_pwrst()`, `cpu_clear_prev_logic_pwrst()`, `l2x0_pwrst_prepare()`, `save_l2x0_context()`, and `enable_mercury_retention_mode()`.

## Control Flow
Early init maps SAR RAM and writes CPU1 wakeup physical address for kexec safety. Main MPUSS init initializes per-CPU SAR offsets, looks up CPU and MPU powerdomains, clears previous-state registers, saves L2 context, selects OMAP4-specific suspend/resume/hotplug ops, and handles OMAP5 retention setup. Low-power entry validates the requested state, computes context save level, programs CPU powerdomain next/logic state, enters cpuidle RCU state if requested, writes wakeup address and SCU/L2 SAR data, then calls `cpu_suspend()` or WFI. Hotplug programs a terminal CPU state and does not return when CPU off succeeds.

## State and Persistence Behavior
State includes `sar_base`, per-CPU SAR address pointers, `old_cpu1_ns_pa_addr`, CPU/MPUSS powerdomain next/previous states, L2 saved registers, and SAR scratch values used by ROM/restore code. No filesystem persistence exists, but SAR RAM preserves resume-critical values across low-power transitions.

## Dependencies and Integration Points
It depends on CPU suspend, SCU, L2X0, virtualization boot mode, OMAP PRCM/PRM registers, SAR layout, secure/non-secure startup symbols, powerdomain helpers, and SoC revision/erratum checks. It integrates directly with `cpuidle44xx.c`, `omap-hotplug.c`, `omap-smp.c`, `omap-headsmp.S`, and `omap4-common.c`.

## Risks
This is suspend/hotplug critical. Wrong SAR offsets, wakeup addresses, powerdomain state programming, or context-save levels can hang resume, corrupt cache/GIC state, or wake CPU1 into the wrong kernel after kexec. Erratum gates for OMAP4430 ES1 and CPU OSWR must remain conservative.

## Test Signals
Stress cpuidle, CPU hotplug, suspend/resume, and kexec on OMAP4/OMAP5. Verify CPU1 wakeup address preservation, SAR contents, L2 context restore, no GIC/timer loss, and powerdomain previous states matching requested idle levels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-mpuss-lowpower.c -->

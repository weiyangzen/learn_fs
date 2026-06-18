# sources/distributed-fs/ceph-client/arch/arm/mach-bcm/platsmp-brcmstb.c

Purpose: implements Broadcom STB/Brahma-B15 SMP boot and CPU hotplug power control.

Important APIs/types/functions: power-zone bit definitions, per-CPU software state helpers, `pwr_ctrl_*()` register helpers, `brcmstb_cpu_power_on()`, `brcmstb_cpu_boot()`, `brcmstb_boot_secondary()`, optional `brcmstb_cpu_die()` and `brcmstb_cpu_kill()`, and `brcmstb_smp_ops`.

Control flow: prepare finds `brcm,brcmstb-smpboot`, maps `syscon-cpu` and `syscon-cont`, and records register offsets. Boot checks if CPU is powered, powers memory/clock/isolation zones if needed, writes the reset vector to the HIF control block, and deasserts reset. Hotplug death flushes coherency and waits in WFI; kill waits for software state to clear and powers the CPU zone down.

State and persistence: mapped syscon pointers and register offsets are global. Per-CPU software state is cache-synchronized because dying CPUs may have disabled coherency. Hardware power-zone state persists.

Dependencies and integration: uses OF phandles, ARM v7 coherency helpers, `secondary_startup`, `smp_operations`, jiffies timeouts, and Broadcom STB DT bindings.

Risks: panics on power-state timeout are deliberate because partial CPU power transitions are unrecoverable. CPU0 power-off is refused. Cache-synchronized software state is fragile but necessary around hotplug.

Test signals: SMP boot with `brcm,brahma-b15` CPU method, CPU hotplug online/offline loops, timeout-free power-zone polling, and validation of required syscon phandles.

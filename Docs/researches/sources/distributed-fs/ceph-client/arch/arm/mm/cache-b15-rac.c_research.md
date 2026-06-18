# sources/distributed-fs/ceph-client/arch/arm/mm/cache-b15-rac.c

Purpose: manages the Broadcom Brahma-B15/B53 read-ahead cache (RAC), wrapping ARMv7 whole-cache maintenance so operations that are not transparent to the RAC first disable and flush it.

Important APIs/types/functions: key state includes `b15_rac_base`, `rac_lock`, `rac_config0_reg`, `rac_flush_offset`, and `b15_rac_flags` with `RAC_ENABLED` and `RAC_SUSPENDED`. Important functions/macros include `__b15_rac_disable`, `__b15_rac_flush`, `b15_rac_disable_and_flush`, `__b15_rac_enable`, `BUILD_RAC_CACHE_OP`, `b15_flush_kern_cache_all`, `b15_rac_enable`, reboot notifier `b15_rac_reboot_notifier`, CPU hotplug callbacks `b15_rac_dying_cpu` and `b15_rac_dead_cpu`, syscore suspend/resume hooks, and `b15_rac_init`.

Control flow: `arch_initcall` locates the BIU control device-tree node, maps registers, chooses the B15 or B53 flush register from CPU compatibility, registers reboot/hotplug/syscore hooks, verifies RAC starts disabled, enables RAC for possible CPUs, and sets `RAC_ENABLED`. Wrapped cache operations disable and flush RAC under `rac_lock`, call the normal `v7_flush_*` operation, and restore RAC. Hotplug disables RAC before a CPU exits coherency and re-enables it after death; reboot and suspend force a suspended path.

State and persistence: MMIO register mapping and RAC enable bits are runtime global state. `rac_config0_reg` stores the last configuration across hotplug/suspend. Notifier and syscore registrations persist until shutdown.

Dependencies and integration points: depends on device-tree compatible `brcm,brcmstb-cpu-biu-ctrl` and CPU nodes `brcm,brahma-b15` or `brcm,brahma-b53`. It integrates with ARMv7 cache routines, CPU hotplug states, reboot notifier chain, syscore PM, and cache flush call patching through the exported `b15_flush_*` wrappers.

Risks: RAC must be disabled for set/way and all-cache operations that are not transparent; failure causes stale data or instruction fetches. Hotplug/reboot ordering is delicate because RAC spans CPUs and coherency domain exit. The implementation warns and refuses more than four CPUs even though B53 comments mention octo-core flush offset, so platform assumptions must match hardware support.

Test signals: boot on B15/B53 platforms, validate DT matching and register offset, run cache coherency and DMA tests with RAC enabled, exercise `flush_cache_all`, CPU hotplug offline/online, kexec/reboot, and suspend/resume, and confirm no RAC MMIO access occurs before successful mapping.

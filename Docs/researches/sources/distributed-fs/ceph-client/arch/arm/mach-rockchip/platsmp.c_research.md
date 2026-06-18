# sources/distributed-fs/ceph-client/arch/arm/mach-rockchip/platsmp.c

Purpose: Rockchip ARM SMP bring-up and CPU hotplug support.

Important APIs/types/functions: key routines are `rockchip_smp_prepare_cpus()`, `rk3036_smp_prepare_cpus()`, `rockchip_boot_secondary()`, `rockchip_smp_prepare_sram()`, `rockchip_smp_prepare_pmu()`, `pmu_set_power_domain()`, `rockchip_get_core_reset()`, `rockchip_cpu_kill()`, and `rockchip_cpu_die()`. Registers CPU methods for `rockchip,rk3036-smp` and `rockchip,rk3066-smp`.

Control flow: prepare maps SRAM, locates PMU regmap when present, enables SCU on Cortex-A9 or counts cores from L2CTLR otherwise, powers down nonboot cores, and copies the trampoline into SRAM for A9. Booting a CPU powers its domain, then either relies on SRAM trampoline or writes BootROM mailbox values and sends `sev`.

State and persistence: global PMU/SRAM/SCU mappings, `ncores`, and `has_pmu` hold platform state. Hardware power domains and reset lines are mutated.

Dependencies and integration points: depends on DT nodes for SRAM, PMU, SCU, CPU resets, syscon regmaps, ARM SCU/cache helpers, reset controller, and generic SMP.

Risks: some error paths leak mappings or leave partial state but happen at init. Busy-wait power-domain polling has no timeout. A typo-like mailbox value `0xDEADBEAF` is hardware ABI. Reset controls are optional for Cortex-A9 but mandatory for other cores.

Test signals: CPU online/hotplug on rk3036 and rk3066/rk3188 families, DT missing-node failures, PMU power-domain status, and cache/SRAM trampoline validation.

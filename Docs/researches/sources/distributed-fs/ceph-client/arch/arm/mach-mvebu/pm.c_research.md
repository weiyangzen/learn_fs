<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/pm.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/pm.c

Purpose: Generic MVEBU suspend implementation. It saves boot information, copies low-level powerdown code to SRAM, invokes `cpu_suspend`, coordinates board SDRAM powerdown, and registers `platform_suspend_ops`.

Important APIs/types/functions: Important routines include `mvebu_pm_powerdown`, `mvebu_internal_reg_base`, `mvebu_pm_store_armadaxp_bootinfo`, `mvebu_pm_store_bootinfo`, `mvebu_enter_suspend`, `mvebu_pm_enter`, and `mvebu_pm_suspend_init`.

Control flow, state, and persistence: The suspend path persists resume metadata in SRAM or SoC-specific registers, sets the boot address to resume code, saves internal register base information, and calls board PM entry before executing the low-power sequence.

Dependencies and integration points: Important routines include `mvebu_pm_powerdown`, `mvebu_internal_reg_base`, `mvebu_pm_store_armadaxp_bootinfo`, `mvebu_pm_store_bootinfo`, `mvebu_enter_suspend`, `mvebu_pm_enter`, and `mvebu_pm_suspend_init`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include ARM `cpu_suspend`, SRAM helpers, PMSU/system controller, MBUS/internal register windows, and board-level PM callbacks. Risks include wrong SRAM copy size/address, incomplete bootinfo for newer SoCs, and resume failure after memory-controller changes. Test standby/mem suspend, resume on Armada XP/38x, invalid suspend state rejection, and early-init failures.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 267 lines, 6299 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/pm.c -->

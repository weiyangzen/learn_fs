# sources/distributed-fs/ceph-client/drivers/soc/bcm/brcmstb/pm/pm-mips.c

Purpose: MIPS-specific Broadcom STB suspend, deep standby, and power-off orchestration. It maps AON, SRAM, DDR PHY, MEMC arbiter, and timer blocks, installs `platform_suspend_ops`, and provides S2, S3, and S5 control paths around low-level assembly.

Important APIs and functions: `brcmstb_pm_init()` is an `arch_initcall`; `brcmstb_pm_enter()` handles `PM_SUSPEND_STANDBY` and `PM_SUSPEND_MEM`; `brcmstb_pm_s5()` becomes `pm_power_off`; `brcmstb_pm_s2()` prepares the six-word argument block for `brcm_pm_do_s2()`; `brcmstb_pm_s3()` saves CP0 state, MEMC RTS registers, flushes TLB/cache, and calls `brcm_pm_do_s3()`. `brcm_pm_save_cp0_context()` and `brcm_pm_restore_cp0_context()` preserve generic and Broadcom CP0 registers.

Control flow: init maps required OF nodes and bails out with cleanup on mapping failures. S2/S3 both start with `brcmstb_pm_handshake()`, redirect exception vectors to warm restart, run the selected low-power helper, then restore normal interrupt vector behavior. S3 writes a magic value and reentry address into AON SRAM, inhibits DDR reset pulses, saves register context, enters deep standby, then reinitializes CPU/TLB state and restores saved context after wake.

State and persistence: global `ctrl` holds MMIO mappings and MEMC count. S3 persists warm-boot metadata in AON SRAM and saves CP0/MEMC state on the stack for restoration. S5 clears the S3 magic so the next boot is cold.

Dependencies and integration: depends on BMIPS CP0 helpers, `bmips_cpu_setup()`, `BMIPS_WARM_RESTART_VEC`, OF-compatible AON/DDR/timer nodes, assembly helpers in `s2-mips.S` and `s3-mips.S`, and Linux suspend core.

Risks and test signals: high-risk areas include raw physical pointer truncation to `u32`, fixed MEMC0 arbiter assumptions for RTS restore, IRQ/vector state during wake, and hardware timing races covered by the 3 ms handshake delay. Test signals include standby/mem suspend cycles, S5 power-off, warm-boot magic behavior, DDR resume stability, and no leaks from failed MMIO mapping paths.

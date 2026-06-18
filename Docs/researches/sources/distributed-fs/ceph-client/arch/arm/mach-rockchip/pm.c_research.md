# sources/distributed-fs/ceph-client/arch/arm/mach-rockchip/pm.c

Purpose: Rockchip RK3288 suspend-to-RAM setup, low-power mode programming, and resume boot data preparation.

Important APIs/types/functions: defines `struct rockchip_pm_data`, `rk3288_suspend_init()`, `rockchip_suspend_init()`, `rk3288_suspend_enter()`, `rk3288_suspend_prepare()`, `rk3288_suspend_finish()`, `rk3288_slp_mode_set()`, `rk3288_slp_mode_set_resume()`, `rockchip_lpmode_enter()`, `rk3288_config_bootdata()`, and suspend ops `rk3288_suspend_ops`.

Control flow: init finds PMU-compatible data, maps boot SRAM, obtains PMU/SGRF/GRF regmaps, copies `rockchip_slp_cpu_resume` into boot RAM, configures resume boot data, and installs suspend ops. Suspend prepare programs low-power mode registers; enter calls `cpu_suspend()` with `rockchip_lpmode_enter()`, which flushes caches and executes WFI; finish restores saved PMU/SGRF settings.

State and persistence: globals cache boot RAM mapping/physical address, regmaps, and saved PMU/SGRF register values. It writes fast-boot address, wakeup sources, oscillator/PLL counters, SIDDQ USB PHY bits, and power-mode controls.

Dependencies and integration points: depends on DT PMU node, syscon regmaps, SRAM region, assembly resume code in `sleep.S`, ARM `cpu_suspend`, regulator suspend framework, and `rockchip.c` machine init.

Risks: suspend register sequences are SoC-specific and can break resume. Boot RAM copy and physical address must be correct. USB PHY SIDDQ manipulation and oscillator disable decisions have board-level side effects.

Test signals: RK3288 suspend/resume, wake from GPIO/ARM interrupt, boot RAM code checksum/size, regulator suspend integration, and register restore checks after resume.

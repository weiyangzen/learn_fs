# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm3xxx.c

## Purpose
Implements OMAP3 PRM support: reset-source mapping, voltage controller/processor access, PRCM IRQ setup, IO wake chain reconfiguration, PM register initialization, IVA idling, powerdomain operations, and late IO-wakeup IRQ registration.

## APIs, Flow, And State
Exports `omap3_prm_vcvp_read/write/rmw()`, `omap3xxx_prm_init()`, `omap3xxx_prm_clear_global_cold_reset()`, `omap3_prm_save_scratchpad_contents()`, and `omap3_prm_init_pm()`. Static flow maps reset status to standard reset IDs, checks/clears VP TXDONE bits, performs DPLL3 reset for reboot, reads pending PRM IRQs as enabled-and-status bits, saves/restores IRQ masks for suspend, and clears module wake IRQs by temporarily enabling clocks until wake bits clear. PM init programs wake enables/group selects, clears reset flags, idles IVA2, and resets the modem block. IO-chain paths differ for pre-ES3.1 and later hardware. `omap3_pwrdm_operations` adds previous-state reads, hardware SAR, and OMAP3-specific memory previous-state mapping.

## Dependencies And Integration
Depends on SoC feature detection, VP/voltage code, powerdomain/clockdomain, OMAP2/3 PRM/CM access, OMAP3 register bits, and device tree IRQ lookup for `ti,omap3-prm`. Registers `omap3xxx_prm_ll_data` and optionally a chained PRCM IRQ handler.

## Risks And Test Signals
Wake status clearing manipulates module clocks and has USBHOST special handling; mistakes can lose wake events or alter clock state. IO-chain timing can warn on latch timeout. IVA idling touches an accelerator that may be absent but clock-active. Test signals are OMAP3 off-mode, IO wake interrupt delivery, VP transaction completion, DSS low-power retention, reset-source reads, and absence of `powerdomain waited too long` logs.

# sources/distributed-fs/ceph-client/drivers/bus/ti-sysc.c

## Purpose
`ti-sysc.c` is the Texas Instruments interconnect target wrapper driver. It discovers a module wrapper from devicetree, maps its revision/SYSCONFIG/SYSSTATUS registers, manages clocks and reset lines, configures idle and standby modes, applies SoC/module quirks, and then populates the child devices behind the wrapper.

## Important APIs, Types, And Functions
The central state is `struct sysc`, which stores register offsets, mapped module base, clocks, reset control, capabilities, runtime PM state, saved `sysconfig`, and quirk callbacks. `struct sysc_capabilities`, `struct sysc_regbits`, and the OF match table describe register layouts for OMAP2, OMAP4, timers, SmartReflex, McASP, USB host, MCAN, and PRUSS variants. Key flows are `sysc_probe()`, `sysc_init_module()`, `sysc_runtime_resume()`, `sysc_runtime_suspend()`, `sysc_reset()`, `sysc_enable_module()`, `sysc_disable_module()`, and `of_platform_populate()` of children.

## Control Flow
Probe allocates `struct sysc`, initializes global SoC data, reads match data and DT quirks, parses child ranges and named register resources, maps the register window, parses masks and idle modes, initializes legacy platform data, applies early address/register quirks, skips disabled or reserved modules, gets/prepares clocks, gets optional reset control, and initializes the hardware. Module initialization denies clockdomain idle, enables optional and main clocks, optionally deasserts reset, reads revision, applies revision quirks, runs legacy init if needed, enables the module, and optionally soft-resets it. After runtime PM is enabled, children are populated unless the module is reserved; delayed work later balances clocks/runtime references for no-idle or no-reset-on-init cases.

## State And Persistence
Persistent hardware state is the wrapper register programming: idle modes, reset state, clocks, and child device availability. Driver state includes `ddata->enabled`, saved `sysconfig` for context-loss detection, delayed idle work, and SoC-global disabled/restored module lists protected by `sysc_soc->list_lock`. Context-loss recovery may re-enable, reset, and restore `sysconfig` via a CPU PM notifier for modules tagged with `SYSC_QUIRK_REINIT_ON_CTX_LOST`.

## Dependencies And Integration Points
The driver integrates with OF address parsing, platform bus population, clk and clkdev, reset controller, PM runtime, generic PM domains through parent buses, CPU PM notifiers, and legacy `ti_sysc_platform_data` callbacks. A platform bus notifier adds parent clocks to child devices as they appear. It also consumes TI devicetree binding flags such as `ti,sysc-mask`, `ti,syss-mask`, `ti,sysc-midle`, `ti,sysc-sidle`, and no-idle/no-reset quirks.

## Risks And Edge Cases
Register-offset validation is critical because this driver can touch wrapper registers before children bind. Quirk detection relies on base address, offsets, and revision masks; stale DT data can select wrong reset or idle behavior. Runtime PM sequencing must keep clockdomain idle denied while clocks/registers are being manipulated. The delayed idle path intentionally leaves modules active for early console or no-reset cases and must balance usage counts exactly once. Reset polling has special handling when timekeeping is suspended. The DSS, I2C, RTC, watchdog, OTG, SGX, and PRUSS quirks write child/module-specific registers, so regressions can be hardware-specific and hard to catch in generic boot tests.

## Test Signals
Useful signals are successful boot and child population on representative OMAP/AM/DRA SoCs, runtime suspend/resume cycles for child devices, system suspend/resume with context loss, CPU cluster idle exit on AM335x GPMC/OTG, correct early console behavior with no-idle/no-reset flags, DT validation for register ranges and clock names, and absence of reset timeout warnings.

# sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdns3-imx.c

Purpose: Provides the NXP i.MX glue layer around the Cadence USB3 controller, handling non-core registers, clocks, child `cdns,usb3` population, wakeup configuration, and platform-specific low-power transitions.

Important APIs, types, and functions: `struct cdns_imx` stores the device, non-core MMIO base, clock bulk array, and child platform device pointer. `cdns_imx_noncore_init` validates PHY clock, asserts/deasserts reset bits, straps OTG mode, disables overcurrent, and enables host/device interrupts. `cdns_imx_probe/remove` manage resources, clocks, child population, and runtime PM. `cdns_imx_platform_suspend` is exported through `cdns3_platform_data` and handles host-mode D1/D0 transitions. PM callbacks handle runtime clock gating and system power-loss recovery.

Control flow: Probe maps non-core registers, duplicates and obtains required clocks (`lpm`, `bus`, `aclk`, `ipg`, `core`), enables them, initializes wrapper registers, populates children with platform data, and enables runtime PM. During host suspend, it writes xHCI PMCSR to D1, selects mdctrl clock, polls wrapper/clock/PHY request bits, and enables wakeups. Resume reverses wakeups, returns xHCI to D0, clears RXDET P3, restores clocks, and waits for OTG readiness.

State and persistence behavior: Runtime state is only `struct cdns_imx`, clock enable state, PM state, and wrapper registers. System resume checks reset bits to detect power loss and reinitializes non-core registers when needed.

Dependencies and integration points: Uses OF platform population, Linux clock bulk APIs, runtime/system PM, MMIO polling, Cadence `core.h`, and `cdns3_platform_data.platform_suspend`. Compatible string is `fsl,imx8qm-usb3`; it creates a child compatible with `cdns,usb3`.

Risks: Suspend/resume touches xHCI and OTG registers through child `struct cdns`, so ordering with core role/PM state is important. Poll timeouts are warnings in several low-power paths, which may leave marginal hardware states. The constant `DEVU3_WAEKUP_EN` appears misspelled but is used as a bit name. Power-loss recovery depends on reset-mask values in wrapper registers.

Test signals: i.MX probe/remove, child creation, runtime suspend/resume clock toggling, host-mode system suspend with wake enabled/disabled, resume after power loss, OTG role transitions, and timeout injection for PHY clock valid and mdctrl/lpm/otg-ready polls.

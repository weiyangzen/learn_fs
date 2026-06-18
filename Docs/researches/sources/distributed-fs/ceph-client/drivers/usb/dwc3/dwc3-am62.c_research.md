# sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-am62.c

## Purpose
`dwc3-am62.c` is the TI AM62 USB wrapper glue driver. It configures TI-specific USBSS registers, PHY PLL reference clock selection through syscon, an i2409 PHY workaround, VBUS divider selection, mode-valid signaling, wakeup configuration, and parent PM before populating the child DWC3 core.

## Important APIs, Types, and Functions
The private type is `struct dwc3_am62`, storing wrapper MMIO, USB2 reference clock, syscon offset/rate code, optional PHY MMIO, VBUS divider flag, and last wakeup status. Key functions are `phy_syscon_pll_refclk()`, `dwc3_ti_init()`, `dwc3_ti_probe()`, `dwc3_ti_remove()`, `dwc3_ti_suspend_common()`, and `dwc3_ti_resume_common()`. The driver matches `ti,am62-usb`.

## Control Flow
Probe maps USBSS registers, gets the `ref` clock, converts its rate to a TI rate-code table entry, optionally maps PHY registers for the i2409 LDO reference workaround, reads `ti,vbus-divider`, and calls `dwc3_ti_init()`. Initialization programs syscon core voltage/refclk fields, applies the PLL LDO workaround when possible, sets VBUS divider selection, enables the ref clock, and sets `USBSS_MODE_VALID`. Probe then enables runtime PM, populates child devices, marks the wrapper wake-capable, enables wakeup, and starts autosuspend.

Suspend configures wake sources based on current operational mode in `USBSS_CORE_STAT`: host uses linestate/overcurrent wake, device uses VBUS/session-valid wake. It clears wake status, writes a debug sentinel to detect context loss, and disables the ref clock. Resume checks the sentinel; if context was lost it reruns full TI init, otherwise it restores debug config and reenables the ref clock, disables wake config, and records wakeup status.

## State and Persistence Behavior
Driver state is live only in `struct dwc3_am62`. Hardware wrapper state may be lost across suspend; the debug config sentinel determines whether to reinitialize. `wakeup_stat` retains the last wake reason after resume for possible diagnostics but is not exported here.

## Dependencies and Integration Points
The driver depends on platform MMIO resources, clk, syscon/regmap, OF child population, runtime PM, pinctrl consumer headers, and the DWC3 child core. It does not embed `struct dwc3`; it creates child devices via `of_platform_populate()`.

## Risks
Unsupported ref clock rates fail probe. If optional PHY MMIO mapping fails, the i2409 workaround is skipped with a warning, which may affect affected silicon. Wake configuration is mode-dependent and can cause missed or spurious wakeups if wrapper operational mode is stale. Remove clears mode-valid but does not explicitly disable the ref clock outside PM state transitions.

## Test Signals
Check probe with every supported reference clock rate, `ti,syscon-phy-pll-refclk` programming, optional PHY-resource absence, child DWC3 creation, runtime autosuspend, host/device wake from system suspend, context-loss reinitialization path, mode-valid bit clear on remove, and wakeup status capture after resume.

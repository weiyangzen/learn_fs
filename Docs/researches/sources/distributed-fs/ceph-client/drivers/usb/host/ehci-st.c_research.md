# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-st.c

## Purpose
STMicroelectronics EHCI platform glue for `st,st-ehci-300x`. It manages multiple clocks, optional 48 MHz rate programming, power and soft resets, a generic PHY, pinctrl sleep/default states, a packet-buffer threshold register, and shared EHCI registration.

## Important APIs, types, and functions
`struct st_ehci_platform_priv` stores three general clocks, `clk48`, power/reset controls, and PHY. `st_ehci_platform_reset()` writes a 128-byte IN/OUT threshold to `AHB2STBUS_INSREG01`, sets caps with `pdata->caps_offset`, and calls `ehci_setup()`. `st_ehci_platform_power_on()` and `power_off()` sequence resets, clocks, and PHY. Probe/remove plus `st_ehci_suspend()`/`st_ehci_resume()` own lifecycle.

## Control flow
Probe creates the HCD, installs default platform data, gets required PHY, enumerates OF clocks, optionally gets `clk48`, gets optional shared power and soft-reset controls, powers on, maps MMIO, and calls `usb_add_hcd()`. Power-on deasserts power then soft reset, sets `clk48` to 48 MHz if present, enables clocks, initializes and powers on PHY. Suspend calls `ehci_suspend()`, powers down, and selects pinctrl sleep. Resume selects default pinctrl, powers on, and calls `ehci_resume()`.

## State and persistence behavior
State lives in private clock/reset/PHY handles and default platform data. Hardware state includes reset lines, clock enables, PHY power, pinctrl state, and threshold register configuration.

## Dependencies and integration points
Depends on clock, reset, PHY, pinctrl PM, OF, DMA/HCD core, `usb_ehci_pdata`, and EHCI shared code. It matches `st,st-ehci-300x`.

## Risks and edge cases
Probe error handling after successful `power_on()` jumps to clock cleanup without explicitly calling `power_off()`, so failures after power-on should be reviewed for resource state. `power_off()` asserts resets before powering off/exiting PHY, which must match hardware requirements. Optional reset controls may be NULL and must be accepted by reset APIs.

## Test signals
Probe with all clocks and without `clk48`, reset-defer paths, PHY power failures, threshold register programming, suspend/resume pinctrl transitions, remove after active traffic, and failure after power-on are high-value signals.

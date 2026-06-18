# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-sh.c

## Purpose
SuperH EHCI platform driver. It defines a direct `hc_driver`, maps platform resources, optionally enables SuperH USB interface/function clocks, and registers the shared EHCI core.

## Important APIs, types, and functions
`struct ehci_sh_priv` stores optional `iclk`/`fclk` and the HCD pointer. `ehci_sh_reset()` sets caps to `hcd->regs` and calls `ehci_setup()`. `ehci_hcd_sh_probe()`, `ehci_hcd_sh_remove()`, and `ehci_hcd_sh_shutdown()` provide lifecycle. `ehci_sh_hc_driver` lists common EHCI callbacks directly.

## Control flow
Probe obtains IRQ, creates the HCD, maps MMIO, allocates private state, gets optional `usb_fck` and `usb_ick`, enables both clocks, calls `usb_add_hcd()`, enables wakeup, stores drvdata, and returns. Remove removes the HCD, releases it, and disables clocks. Shutdown calls the HCD shutdown callback if installed.

## State and persistence behavior
State is in `ehci_sh_priv`, HCD/EHCI structures, clock-enable state, and MMIO registers. There is no suspend/resume device PM wrapper in this file, though the `hc_driver` includes bus suspend/resume when built with PM.

## Dependencies and integration points
Depends on platform resources, clock framework, USB HCD core, and common EHCI callbacks available because this file is included in or built with the EHCI core context. It registers under platform name `sh_ehci`.

## Risks and edge cases
It calls `clk_enable()` on optional clocks that may be `NULL`; this relies on common clock API tolerance. `devm_kzalloc()` state stores the HCD, but the HCD itself is manually owned. No DMA mask is set here, so platform setup must provide one if required.

## Test signals
Probe with both clocks, one clock, and no clocks; IRQ/mapping failures; root-hub enumeration; shutdown; remove; and clock enable/disable balance are useful tests.

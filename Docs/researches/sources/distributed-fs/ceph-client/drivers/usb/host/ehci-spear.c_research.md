# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-spear.c

## Purpose
ST SPEAr SoC EHCI platform glue. It sets a 32-bit DMA mask, manages a required USB host clock, maps registers starting at zero, registers the HCD, and wires simple suspend/resume to the common EHCI helpers.

## Important APIs, types, and functions
`struct spear_ehci` stores the clock in EHCI private storage. `spear_ehci_hcd_drv_probe()` and remove own lifecycle. `ehci_spear_drv_suspend()` and `ehci_spear_drv_resume()` call common EHCI PM. `spear_overrides` adds private space to the generated `hc_driver`.

## Control flow
Probe checks USB disabled state, gets IRQ, coerces 32-bit DMA, gets the clock, creates the HCD, maps MMIO, records resources, stores the clock in private state, sets caps to `hcd->regs`, enables the clock, and calls `usb_add_hcd()`. Remove removes the HCD, disables the clock, and releases the HCD.

## State and persistence behavior
The only private state is the clock pointer. Runtime state is held by HCD/EHCI core and the enabled clock. Register state persists in the controller until reset or power gating.

## Dependencies and integration points
Depends on OF platform matching (`st,spear600-ehci`), clock framework, DMA mapping, PM ops, and shared EHCI core. Uses `usb_hcd_platform_shutdown`.

## Risks and edge cases
Clock acquisition is mandatory. Like other minimal glue, it assumes caps at offset zero and no reset/PHY sequencing. Failure paths must balance clock enable and HCD ownership.

## Test signals
SPEAr DT probe, DMA mask setup, clock failure/defer, suspend/resume, remove, shared IRQ operation, and root-hub enumeration are the main tests.

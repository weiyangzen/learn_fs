# sources/distributed-fs/ceph-client/drivers/usb/host/ohci-spear.c

## Purpose

`ohci-spear.c` is ST SPEAr platform OHCI glue. It is a compact driver that supplies a clock-backed platform wrapper around the generic OHCI core.

## Important APIs, Types, and Functions

`struct spear_ohci` stores the interface clock. Important functions are `spear_ohci_hcd_drv_probe()`, `spear_ohci_hcd_drv_remove()`, `spear_ohci_hcd_drv_suspend()`, and `spear_ohci_hcd_drv_resume()`. It defines `ohci_spear_hc_driver`, `spear_ohci_id_table`, and platform driver `spear_ohci_hcd_driver`.

## Control Flow

Probe gets IRQ, coerces a 32-bit DMA mask, obtains the clock, creates an HCD with extra private clock storage, maps MMIO, enables the clock, and calls `usb_add_hcd()`. Remove removes the HCD, disables the clock, and releases the HCD. Suspend waits for state-change quiet time, calls `ohci_suspend()`, and disables the clock. Resume re-enables the clock and calls `ohci_resume()`.

## State and Persistence Behavior

Runtime state is the HCD, mapped registers, and a single clock pointer in private data. Clock state is the only platform-specific hardware state managed here. There is no persistence.

## Dependencies and Integration Points

It depends on platform bus, OF match `st,spear600-ohci`, clock framework, DMA mask setup, platform MMIO/IRQ resources, and generic OHCI `ohci_init_driver()` callbacks.

## Risks and Test Signals

Risks include ignored `clk_prepare_enable()` return in probe/resume, no reset or PHY handling, no `usb_disabled()` check until module init, and simple PM ordering. Test signals include SPEAr DT probe, clock enable/disable observation, enumeration, suspend/resume with device wakeup policy, and failure cleanup before/after HCD allocation.

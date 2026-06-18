# sources/distributed-fs/ceph-client/drivers/usb/host/ohci-omap.c

## Purpose

`ohci-omap.c` is legacy OMAP1 OHCI platform glue. It handles OMAP clocks, optional OTG transceiver handoff, board-specific power and overcurrent setup, GPIO-backed port power, and platform PM around the generic OHCI core.

## Important APIs, Types, and Functions

`struct ohci_omap_priv` stores `usb_host_ck`, `usb_dc_ck`, and optional power/overcurrent GPIOs. Important functions are `omap_ohci_clock_power()`, `start_hnp()`, `ohci_omap_reset()`, `ohci_hcd_omap_probe()`, `ohci_hcd_omap_remove()`, `ohci_omap_suspend()`, and `ohci_omap_resume()`.

## Control Flow

Probe validates legacy resources, creates an HCD with extra private data, obtains optional GPIOs and the two clocks, maps registers, gets the IRQ, and calls `usb_add_hcd()`. The overridden reset path configures OTG if requested, enables clocks, invokes board reset hooks, calls `ohci_setup()`, sets remote-wakeup-connected state for OTG/RWC boards, applies OMAP OSK/Nokia770 root-hub policy, and powers transceivers or GPIOs. Suspend calls `ohci_suspend()` then disables clocks; resume re-enables clocks and calls `ohci_resume()`.

## State and Persistence Behavior

State lives in HCD private clock/GPIO pointers, `hcd->usb_phy`, OHCI root-hub registers, and board platform data callbacks. Power and mux state is hardware-backed and survives until explicit board or clock changes.

## Dependencies and Integration Points

It depends on OMAP1 SoC headers, legacy platform data `struct omap_usb_config`, OMAP mux and OTG registers, optional USB OTG PHY APIs, GPIO descriptors, clocks, and platform resources. It registers platform name `ohci`.

## Risks and Test Signals

Risks include legacy board conditionals, OTG handoff failure, missing unwind after some reset failures, global OMAP register assumptions, unused overcurrent GPIO, and power polarity differences. Test signals include OMAP OSK and Nokia770 boot, OTG HNP on configured port, clock enable/disable through PM, platform transceiver callbacks, GPIO power toggling, and root-hub descriptor power-budget behavior.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-atmel.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-atmel.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/host/ehci-atmel.c` is the Atmel/AT91 platform wrapper for the common EHCI host controller core. It wires clocks, MMIO, IRQ, HSIC mode setup, suspend/resume, and platform-driver registration around `ehci_init_driver()`. The source was read as a complete 251-line file.

## Important APIs, Types, and Functions

`struct atmel_ehci_priv` holds interface and USB clocks plus a `clocked` flag in EHCI private storage. Important functions are `atmel_start_clock()`, `atmel_stop_clock()`, `atmel_start_ehci()`, `atmel_stop_ehci()`, `ehci_atmel_drv_probe()`, `ehci_atmel_drv_remove()`, `ehci_atmel_drv_suspend()`, and `ehci_atmel_drv_resume()`. The driver uses `ehci_atmel_drv_overrides.extra_priv_size` and registers `ehci_atmel_driver`.

## Control Flow

Module init initializes a copy of the generic EHCI `hc_driver` and registers the platform driver. Probe checks `usb_disabled()`, gets IRQ, coerces 32-bit DMA mask, creates the HCD, maps MMIO, obtains `ehci_clk` and `usb_clk`, sets `ehci->caps` to the mapped base, enables both clocks, calls `usb_add_hcd()`, enables wakeup, and, when DT PHY mode is HSIC, writes the HSIC enable bit to instruction register 8. Remove removes the HCD, releases it, and stops clocks. PM suspend calls `ehci_suspend()` then stops clocks; resume starts clocks and calls `ehci_resume()`.

## State and Persistence Behavior

State is limited to the HCD, the two clocks, and the `clocked` boolean. Hardware register state is initialized by the common EHCI setup and one optional HSIC instruction-register write. No persistent storage exists.

## Dependencies and Integration Points

The wrapper depends on platform resources, OF matching `atmel,at91sam9g45-ehci`, clock framework names `ehci_clk` and `usb_clk`, `of_usb_get_phy_mode()`, and the common EHCI core. It exposes standard USB host behavior through `usb_add_hcd()`.

## Risks and Edge Cases

Clock enable errors are not individually unwound inside `atmel_start_clock()`, so failed clock preparation could leave asymmetric state. HSIC mode is configured only after `usb_add_hcd()`, so regressions could appear if the core expects that bit earlier. Suspend/resume assumes clocks and EHCI state remain coherent across system sleep.

## Test Signals

Build with `USB_EHCI_HCD_AT91`, probe an AT91 EHCI node with both clocks, exercise HSIC and non-HSIC DT modes, run high-speed enumeration and transfers, and verify suspend/resume with wakeup-enabled root hub.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-atmel.c -->

# sources/distributed-fs/ceph-client/drivers/usb/host/ohci-ps3.c

## Purpose

`ohci-ps3.c` is PS3 system-bus glue for the OHCI controller behind the Cell/Spider platform. It opens hypervisor devices, creates PS3 DMA/MMIO/IRQ resources, applies PS3-specific big-endian and root-hub setup, and registers the generic OHCI core.

## Important APIs, Types, and Functions

Important functions are `ps3_ohci_hc_reset()`, `ps3_ohci_hc_start()`, `ps3_ohci_probe()`, `ps3_ohci_remove()`, `ps3_ohci_driver_register()`, and `ps3_ohci_driver_unregister()`. It defines `ps3_ohci_hc_driver` and `ps3_ohci_driver`.

## Control Flow

Probe checks firmware support, opens the HV device, creates DMA and MMIO regions, sets up an I/O IRQ, sets a 32-bit DMA mask, creates the HCD, requests and maps MMIO, stores HCD drvdata, and calls `usb_add_hcd()`. Reset marks MMIO big-endian and runs `ohci_init()`. Start preprograms root-hub descriptor A/B for Spider quirks, then calls `ohci_run()`. Remove shuts down OHCI, removes the HCD, unmaps/releases regions, destroys IRQ, frees DMA/MMIO regions, and closes the HV device.

## State and Persistence Behavior

State is held by PS3 system-bus device regions, virtual IRQ, HCD, and OHCI quirk flags. Hardware state is mediated by PS3 hypervisor resources and OHCI registers. No persistent data is written.

## Dependencies and Integration Points

It depends on PS3 firmware feature detection, `ps3_system_bus`, LV1 region helpers, PS3 IRQ setup, DMA region APIs, and the OHCI core included by `ohci-hcd.c`.

## Risks and Test Signals

Risks include hypervisor resource failure unwinding, `BUG_ON()` on unexpected DMA-region failure, nonfatal `request_mem_region()` failure followed by later release, big-endian MMIO assumptions, and shutdown using remove semantics. Test signals include PS3 firmware-gated registration, successful region/IRQ creation, root-hub power timing, USB enumeration on PS3, and full remove/shutdown cleanup.

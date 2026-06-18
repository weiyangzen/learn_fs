# sources/distributed-fs/ceph-client/drivers/usb/host/ssb-hcd.c

## Purpose
`ssb-hcd.c` is Sonics Silicon Backplane glue for Broadcom USB host cores. It enables SSB USB cores, applies Broadcom-specific workarounds, and creates child `ohci-platform` and, for USB 2.0 cores, `ehci-platform` devices. The actual USB scheduling and root-hub behavior are delegated to the generic OHCI/EHCI platform drivers.

## Important APIs, Types, And Functions
The main private type is `struct ssb_hcd_device`, holding child OHCI/EHCI platform-device pointers and the enable flags needed for resume. `ssb_hcd_init_chip()` enables the SSB core and sets host mode for USB11 host/device cores. `ssb_hcd_usb20wa()` and `ssb_hcd_5354wa()` program undocumented Broadcom registers for USB 2.0 PHY/core reset sequencing and BCM5354 revision 2 failures. `ssb_hcd_create_pdev()` allocates a platform device, attaches MEM/IRQ resources and empty EHCI/OHCI platform data, and registers it. `ssb_hcd_probe()` validates supported embedded chip families, sets a 32-bit DMA mask, initializes the chip, and creates the child HCD devices. Remove, shutdown, suspend, and resume disable or re-enable the SSB core.

## Control Flow
The SSB bus matches Broadcom USB11 hostdev, USB11 host, and USB20 host cores. Probe rejects non-0x4700/0x5300 embedded chips, sets DMA constraints, allocates `ssb_hcd_device`, and enables the core. It reads address-match data from `SSB_ADMATCH0`; USB20 maps the first 0x800 bytes to OHCI and the next 0x800 bytes to EHCI, while USB11 uses the advertised size. If EHCI creation fails, OHCI is unregistered before returning. Remove unregisters children, then disables the SSB device.

## State And Persistence Behavior
No state persists beyond device lifetime. Runtime state is child platform-device ownership plus the SSB enable flags used on PM resume. Hardware state is reset on probe, shutdown, suspend, and remove through `ssb_device_enable()`/`ssb_device_disable()` and direct SSB register writes.

## Dependencies And Integration Points
The file integrates with the SSB bus, platform-device core, DMA mask APIs, and generic OHCI/EHCI platform HCDs. It relies on Broadcom SSB register definitions and address-match helpers. The child device names (`ohci-platform`, `ehci-platform`) must match corresponding platform drivers. The code also conditionally depends on `CONFIG_SSB_DRIVER_MIPS` for a BCM5354 workaround.

## Risks And Edge Cases
The Broadcom workarounds use fixed offsets and bit masks, so they depend on core revisions matching expectations. The code comments note that USB11 host/device cores are always attached as host OHCI; there is no client-mode branch. Suspend disables the SSB core, while resume only calls `ssb_device_enable()` and does not repeat all USB20 workaround writes, which may be relevant if hardware loses more state than expected. Error paths must keep child platform devices balanced.

## Test Signals
Probe should create OHCI for USB11 and both OHCI/EHCI for USB20. Resource ranges should be non-overlapping and IRQ shared with the SSB core IRQ. Runtime tests should include hub/device enumeration behind both child HCDs, remove/unregister, system suspend/resume, and BCM5354 rev2 hardware if available.

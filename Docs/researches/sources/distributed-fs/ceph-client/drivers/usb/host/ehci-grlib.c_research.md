<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-grlib.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-grlib.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/host/ehci-grlib.c` is the Aeroflex Gaisler GRLIB GRUSBHC EHCI platform driver, typically used on LEON/GRLIB SoCs. It provides a static EHCI `hc_driver`, OF resource/IRQ mapping, endian detection, and platform-driver glue. The source was read as a complete 177-line file.

## Important APIs, Types, and Functions

The central object is `ehci_grlib_hc_driver`, a full `struct hc_driver` table pointing at common EHCI callbacks such as `ehci_irq`, `ehci_setup`, `ehci_run`, `ehci_stop`, `ehci_shutdown`, `ehci_urb_enqueue()`, `ehci_hub_control()`, and PM bus callbacks. Driver entry points are `ehci_hcd_grlib_probe()` and `ehci_hcd_grlib_remove()`, with OF matches by name `GAISLER_EHCI` and `01_026`.

## Control Flow

Probe rejects disabled USB, converts OF address to a resource, forces a DMA mask pointer for `usb_create_hcd()`, creates the HCD, parses and maps IRQ, maps MMIO, sets `ehci->caps`, reads `hc_capbase`, and if the version is not the known GRUSBHC value `0x0100`, enables big-endian MMIO, descriptor, and capbase handling. It then calls `usb_add_hcd()` and enables device wakeup. Remove removes the HCD, disposes the IRQ mapping, and releases the HCD.

## State and Persistence Behavior

State is the HCD/EHCI instance, mapped IRQ, mapped MMIO, and endian flags. No persistent storage exists.

## Dependencies and Integration Points

The file depends on OF address/IRQ helpers, platform devices, and common EHCI functions supplied because it is included into `ehci-hcd.c` for SPARC LEON builds. It integrates with LEON/GRLIB device-tree style matching by OF node name.

## Risks and Edge Cases

Endian detection assumes `HCIVERSION == 0x0100` identifies one byte order and any other value means big-endian operation. IRQ mapping returns zero on failure and must be disposed on later errors. The file is conditionally included by `ehci-hcd.c`, so standalone build assumptions are invalid.

## Test Signals

Test on LEON/GRLIB hardware or emulation for both detected endian paths, OF resource/IRQ failure paths, HCD add/remove, root-hub enumeration, and wakeup-capable suspend/resume when PM is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-grlib.c -->

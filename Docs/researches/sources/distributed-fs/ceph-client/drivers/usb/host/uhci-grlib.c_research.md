# sources/distributed-fs/ceph-client/drivers/usb/host/uhci-grlib.c

## Purpose
`uhci-grlib.c` is UHCI bus glue for the GRLIB GRUSBHC controller on SPARC/LEON systems. It maps Open Firmware resources, detects controller endianness, configures the shared UHCI engine for MMIO and possible big-endian descriptors, and registers a platform driver named `grlib-uhci`.

## Important APIs, Types, And Functions
`uhci_grlib_init()` is the HCD `.reset` callback. It probes `USBPORTSC1` to detect byte-swapped MMIO and descriptor format, counts root-hub ports, assigns generic reset/check callbacks, and calls shared `check_and_reset_hc()`. `uhci_grlib_hc_driver` reuses UHCI core operations for IRQ, start, stop, URB enqueue/dequeue, endpoint disable, frame number, and root-hub control. `uhci_hcd_grlib_probe()` parses OF address and IRQ, creates the HCD, maps registers with `devm_ioremap_resource()`, stores `uhci->regs`, and calls `usb_add_hcd()`. Remove disposes the IRQ mapping and releases the HCD.

## Control Flow
The platform driver matches OF names `GAISLER_UHCI` and `01_027`. Probe validates USB is enabled, obtains MMIO resource and IRQ from the device tree, gives the platform device a coherent DMA mask, creates the HCD, maps registers, and starts the shared UHCI stack. During HCD reset, endian probing occurs before port counting. Shutdown calls `uhci_hc_died()` without locking to quiesce DMA and interrupts for kexec-like consumers.

## State And Persistence Behavior
No persistent state is kept. Runtime state includes mapped registers, IRQ mapping, and UHCI private flags (`big_endian_mmio`, `big_endian_desc`, reset callbacks, root-port count). Hardware state is reset through the shared generic UHCI reset path. Remove tears down the HCD and IRQ mapping.

## Dependencies And Integration Points
This file depends on OF address/IRQ APIs, platform devices, GRLIB naming conventions, and the shared UHCI implementation included by `uhci-hcd.c`. It depends on `CONFIG_USB_UHCI_BIG_ENDIAN_MMIO` and `CONFIG_USB_UHCI_BIG_ENDIAN_DESC` support in `uhci-hcd.h` for endian-correct register and descriptor access.

## Risks And Edge Cases
Endianness detection assumes `USBPORTSC1` bit 7 is always one and bit 15 is zero; bad hardware state could mis-detect and corrupt all descriptor/register access. The probe manually sets `dma_mask`, which may hide missing DMA binding detail. IRQ disposal must match successful `irq_of_parse_and_map()`. This glue has no clock/reset-control handling; it assumes firmware/platform already prepared the controller.

## Test Signals
Tests should verify OF matching, resource mapping, IRQ delivery, correct endian detection on both little and big endian GRUSBHC variants, root-port enumeration, URB traffic, remove, and shutdown quiescence. Debugfs UHCI schedule output should show valid descriptor pointers after endian probing.

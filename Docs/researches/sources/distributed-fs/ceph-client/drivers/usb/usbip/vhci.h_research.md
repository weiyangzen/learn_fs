# sources/distributed-fs/ceph-client/drivers/usb/usbip/vhci.h

## Purpose

`vhci.h` declares internal state and helper contracts for the USB/IP virtual host controller. It models virtual root-hub ports, in-flight local URBs, pending unlink requests, and high-speed/superspeed paired HCDs.

## Important APIs, Types, and Functions

`struct vhci_device` stores the remote device ID, speed, root-hub port, common `usbip_device`, transmit/receive submit lists, unlink lists, and TX waitqueue. `struct vhci_priv` is attached to `urb->hcpriv` and maps local URBs to USB/IP sequence numbers. `struct vhci_unlink` tracks unlink request sequence and target submit sequence. `struct vhci` stores platform device and paired HS/SS HCDs; `struct vhci_hcd` stores per-HCD port status, resume timeout, sequence counter, and virtual devices.

## Control Flow

The header defines how VHCI maps global port IDs to platform devices and root-hub ports, how HCD private memory is interpreted, and how RX/TX/sysfs/HCD files call each other.

## State and Persistence Behavior

All state is runtime-only and initialized per virtual controller during HCD start. Configured port/controller counts are compile-time constants from Kconfig.

## Dependencies and Integration Points

It depends on USB HCD structures, common USB/IP definitions, sysfs attributes, and list/spinlock/waitqueue primitives. It is the internal ABI for VHCI module objects.

## Risks and Test Signals

Risks include pointer arithmetic in `vdev_to_vhci_hcd()`, Kconfig port count assumptions, list ownership invariants, and sequence number wrap behavior. Test signals include multi-controller attach/detach, HS versus SS routing, unlink list cleanup, and compile coverage with varied Kconfig counts.

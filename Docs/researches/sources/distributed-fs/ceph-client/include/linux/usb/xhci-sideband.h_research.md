# sources/distributed-fs/ceph-client/include/linux/usb/xhci-sideband.h

## Purpose
This header defines xHCI sideband support for clients that need direct endpoint/event ring buffers or secondary interrupters alongside the normal USB host driver.

## Important APIs, types, and functions
Key types are `xhci_sideband_type`, `xhci_sideband_notify_type`, `xhci_sideband_event`, and `xhci_sideband`. APIs register/unregister sideband clients, add/remove/stop endpoints, obtain endpoint/event buffers, check HCD support, create/remove interrupters, query interrupter IDs, and notify endpoint ring free events.

## Control flow, state, and persistence
Clients register against a USB interface with a notification callback. The sideband layer brokers selected endpoint rings and event buffers from xHCI, supports interrupter allocation, and sends lifecycle notifications. State is runtime xHCI/USB endpoint ownership and scatter-gather buffer metadata.

## Dependencies and integration points
It depends on scatterlists, USB core, and USB HCD structures. It integrates with xHCI internals and device-specific sideband consumers such as display or accelerator paths.

## Risks and test signals
Risks include endpoint ownership races, freeing rings while sideband users still hold buffers, mismatch between HCD support and client registration, and interrupt teardown ordering. Tests should cover register/unregister, endpoint add/remove/stop, interrupter allocation, buffer lifetime, and disabled-config no-op notification.

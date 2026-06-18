# sources/distributed-fs/ceph-client/drivers/usb/usbip/vudc.h

## Purpose

`vudc.h` declares internal structures for the USB/IP virtual USB device controller. VUDC lets a machine act as a USB gadget whose USB traffic is transported over USB/IP.

## Important APIs, Types, and Functions

`struct vep` wraps a virtual endpoint, descriptor, request queue, halt/wedge flags, and ep0 setup flags. `struct vrequest` wraps gadget requests. `struct urbp` associates a USB/IP URB with a virtual endpoint and sequence. `struct tx_item` queues submit or unlink responses. `struct transfer_timer` tracks transfer pacing. `struct vudc` contains the gadget, gadget driver, platform device, cached device descriptor, common `usbip_device`, endpoint array, URB queue, TX queue/lock, main lock, address/status, and connection flags.

## Control Flow

The header defines the contracts among VUDC sysfs, RX, TX, transfer timer, and device/gadget files. Endpoint requests queued by gadget drivers are matched with USB/IP URBs by the RX/transfer code and returned by TX.

## State and Persistence Behavior

All state is runtime-only per virtual UDC platform device. Descriptor caching, pullup, connected, and endpoint request queues are reset by disconnect/reset paths.

## Dependencies and Integration Points

It depends on USB gadget APIs, USB/IP common core, platform devices, timers, sysfs groups, and list/spinlock primitives.

## Risks and Test Signals

Risks include endpoint/request queue invariants, address/status synchronization, timer state transitions, and consistency with VUDC files not in this work item. Test signals include gadget bind/unbind, endpoint enable/disable, request queue/dequeue, USB/IP attach, reset/disconnect, and transfer timer behavior.

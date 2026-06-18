# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/dummy_hcd.c

## Purpose

`dummy_hcd.c` implements the Linux dummy USB host plus gadget emulator. It creates paired platform devices: a host-controller side visible to USB host drivers and a gadget-controller side visible to gadget function drivers. USB traffic is simulated in software, allowing gadget and host code to be developed and tested without physical USB hardware. Isochronous transfers are explicitly unsupported.

## Important APIs, Types, And Functions

Module parameters `is_super_speed`, `is_high_speed`, and `num` select emulated speed capabilities and number of controller pairs. `struct dummy` is the shared state object containing gadget endpoints, address, callback usage count, gadget object, current gadget driver, device status, interrupt/callback flags, pullup/suspend state, and HCD pointers. `struct dummy_hcd` stores root-hub state, hrtimer, port status, active/resume state, current emulated device, queued URBs, and SuperSpeed stream configuration.

The gadget-side endpoint ops are `dummy_enable()`, `dummy_disable()`, request allocation/free, queue/dequeue, halt, and wedge. Gadget ops include frame number, wakeup, self-powered, pullup, UDC start/stop, speed setting, and async callback gating. Host-side HCD ops include URB enqueue/dequeue, hub status/control, bus suspend/resume, and stream allocation/free.

## Control Flow

Initialization allocates HCD and UDC platform devices, one shared `struct dummy` per pair, registers HCD and UDC platform drivers, adds HCD devices first, verifies their probe created required HCD state, then adds UDC devices. UDC probe initializes the embedded gadget, builds fixed and configurable endpoints, sets max speed, initializes EP0, and calls `usb_add_gadget_udc()`.

When a gadget driver binds, UDC core calls `dummy_udc_start()` to store the driver and reset device status. Pullup changes update `dum->pullup`, recalculate root-hub port state, and poll root-hub status. Root-hub control requests power, reset, suspend, resume, and query the single emulated port.

Host URBs are wrapped, linked to the HCD endpoint, appended to `urbp_list`, and processed by `dummy_timer()`. The timer scans queued URBs, finds the matching gadget endpoint, handles EP0 setup packets, then uses `transfer()` to copy bytes between host URB buffers/SG lists and gadget request buffers. Gadget completions use `usb_gadget_giveback_request()`, and host completions use `usb_hcd_giveback_urb()`.

## State And Persistence

All state is in memory. `port_status`, `old_status`, `active`, `old_active`, `resuming`, and `rh_state` emulate root-hub transitions. `dum->devstatus` tracks standard device features. Endpoint state tracks descriptors, halted/wedged flags, stream enablement, setup stage, request queues, and last I/O time. `callback_usage` plus `ints_enabled` emulates interrupt callback quiescing for unbind.

## Dependencies And Integration Points

The file integrates with both USB gadget core and USB HCD framework: `usb_add_gadget_udc()`, `usb_gadget_udc_reset()`, `usb_create_hcd()`, `usb_add_hcd()`, URB link/giveback helpers, root-hub polling, and platform APIs. It also supports SuperSpeed streams with a compact 16-stream limit.

## Risks

The emulator is approximate. Isochronous transfers always fail. Interrupt timing may poll too fast. Bandwidth accounting is simplified. It uses one shared spinlock and drops it around callbacks, requiring rescan logic. The small single-request FIFO optimization can expose ordering differences from real hardware. Root-hub speed/link-state emulation must keep USB2/USB3 compatibility straight.

## Test Signals

Useful tests include loading with different speed parameters and `num`, verifying UDC and root hub creation, binding common gadget functions, enumeration, standard control requests, bulk/interrupt IN and OUT transfers, endpoint halt/wedge behavior, URB unlink, scatterlist transfers, SuperSpeed stream validation, suspend/resume, remote wakeup, and module unload after active queues.

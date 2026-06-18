# sources/distributed-fs/ceph-client/drivers/usb/host/isp116x-hcd.c

## Purpose
`isp116x-hcd.c` is a USB 1.1 HCD for Philips/NXP ISP116x host controllers. It manages memory-mapped command/data register access, packs/unpacks ATL FIFO RAM transfer descriptors, schedules control/bulk/interrupt URBs, implements a two-port root hub interface, supports debugfs register dumps, and handles platform probe/remove and optional PM.

## Important APIs, Types, and Functions
- FIFO/PTD pipeline: `write_ptddata_to_fifo()`, `read_ptddata_from_fifo()`, `pack_fifo()`, `unpack_fifo()`, `preproc_atl_queue()`, `postproc_atl_queue()`, `start_atl_transfers()`, and `finish_atl_transfers()`.
- HCD operations: `isp116x_urb_enqueue()`, `isp116x_urb_dequeue()`, `isp116x_endpoint_disable()`, `isp116x_get_frame()`, `isp116x_reset()`, `isp116x_start()`, `isp116x_stop()`, `isp116x_bus_suspend()`, and `isp116x_bus_resume()`.
- IRQ/root hub: `isp116x_irq()`, `isp116x_hub_status_data()`, `isp116x_hub_control()`, `root_port_reset()`, and `isp116x_hub_descriptor()`.
- Platform/debug: `isp116x_probe()`, `isp116x_remove()`, debugfs show/create/remove helpers.

## Control Flow
Probe maps two 16-bit I/O resources for address and data, creates the HCD, initializes the async list and platform delay hooks, and calls `usb_add_hcd()`. Reset performs software reset and waits for clock-ready. Start validates chip ID, configures FIFO sizes, hardware interrupt polarity/triggering, root hub power/overcurrent policy, remote wakeup, frame interval, interrupt masks, operational state, and initially disables ports to avoid enumeration races.

URB enqueue rejects isochronous transfers, allocates endpoint state outside the spinlock, links the URB, initializes endpoint PID/toggle/maxpacket, schedules async endpoints on `async` or periodic interrupt endpoints in a balanced periodic tree, and starts ATL transfers. The scheduler builds an active endpoint chain for the current frame, respecting periodic load and async byte-time limits, then writes PTDs and payload into ATL FIFO. IRQ disables uP interrupts, acknowledges sources, finishes ATL FIFO when done, handles OHCI-like root hub events and unrecoverable errors, restarts transfers, and restores interrupt enable state. Completion analyzes PTD condition codes, handles short/control underruns, toggles, retries, zero packets, and calls `finish_request()` to give back URBs.

## State and Persistence Behavior
State lives in `struct isp116x`: register bases, platform data, interrupt masks, cached root hub descriptors/status, async list, periodic load/tree, frame index, active ATL chain, FIFO byte counters, and `atl_finishing`. Each endpoint stores PTD, PID state, error count, packet length/data pointer, periodic branch/load, and async list node. No disk persistence exists; debugfs exposes live register/state snapshots.

## Dependencies and Integration Points
The file depends on `isp116x.h` register/PTD definitions, Linux USB HCD APIs, platform data from `linux/usb/isp116x.h`, platform resources, debugfs, timers, PM, and platform-specific delay callbacks unless configured otherwise.

## Risks and Test Signals
Risks include lack of isochronous support, strict register access timing requirements, FIFO packing alignment/endian mistakes, active URB dequeue waiting for IRQ, periodic bandwidth accounting errors, reset timing quirks, and child devices requiring longer port resets. Test signals include usbtest 1-14 noted in comments, control/bulk/interrupt traffic at full/low speed, short packet and zero-packet behavior, periodic load saturation, root hub two-port feature requests, remote wakeup/suspend/resume, debugfs reads while running/suspended, and fault injection for chip ID, clock-ready timeout, IRQ, and resource mapping.

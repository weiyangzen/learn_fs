# sources/distributed-fs/ceph-client/drivers/usb/host/ohci-hcd.c

## Purpose

`ohci-hcd.c` is the main USB 1.1 Open Host Controller Interface core. It owns the generic `hc_driver` operations, controller setup/start/stop, interrupt handling, watchdog recovery, suspend/resume entry points, and module registration for several built-in bus glue drivers.

## Important APIs, Types, and Functions

Primary exported entry points are `ohci_setup()`, `ohci_init_driver()`, `ohci_restart()`, `ohci_suspend()`, and `ohci_resume()`. Core callbacks include `ohci_urb_enqueue()`, `ohci_urb_dequeue()`, `ohci_endpoint_disable()`, `ohci_get_frame()`, `ohci_start()`, `ohci_stop()`, and `ohci_irq()`. It includes `ohci-hub.c`, `ohci-dbg.c`, `ohci-mem.c`, and `ohci-q.c`, so those helpers are compiled as part of the core implementation.

## Control Flow

Bus glue creates a `usb_hcd`, maps registers, and calls the generic reset/start callbacks. `ohci_init()` handles BIOS/SMM ownership handoff, disables interrupts, discovers root-hub ports, allocates HCCA and descriptor pools, and creates debugfs files. `ohci_run()` resets the controller, programs HCCA, frame timing, control/bulk heads, root-hub power policy, enables root-hub polling, enters `OHCI_USB_OPER`, and enables interrupts. URB submission allocates `urb_priv` plus TDs, schedules the endpoint if idle, computes isochronous frame placement, then delegates TD construction to `td_submit_urb()`. IRQ handling reads enabled interrupt bits, handles unrecoverable errors, root-hub status changes, resume detect, done-head writeback, and unlink work until all pending enabled bits are drained.

## State and Persistence Behavior

Persistent runtime state is `struct ohci_hcd`, including register base, HCCA DMA buffer, control/bulk/periodic ED schedule, done-list pointers, pending URBs, EDs in use, root-hub state, frame timing, quirk flags, watchdog counters, and debugfs state. Hardware register state is reinitialized on start/restart/resume and forcibly reset on shutdown. No file-backed persistence exists.

## Dependencies and Integration Points

The file depends on USB core HCD APIs, DMA mapping, dma pools or local memory pools, debugfs, PCI quirk helpers, timers, workqueues, and OHCI register definitions from `ohci.h`. It integrates with bus glue through `ohci_init_driver()` overrides and with root hub logic through `ohci_hub_status_data()` and `ohci_hub_control()`.

## Risks and Test Signals

Risks include BIOS/SMM takeover timeouts, incorrect root-hub power/overcurrent firmware data, fragile hardware reset timing, lost done-head writebacks, frame counter stalls, late isochronous URBs, and quirk interactions across PCI/platform builds. Test signals include USB 1.1 enumeration, URB enqueue/dequeue across all pipe types, root-hub connect/disconnect interrupts, forced unlink paths, suspend/resume with remote wakeup, watchdog recovery on missing WDH, and module init/exit across enabled bus glue variants.

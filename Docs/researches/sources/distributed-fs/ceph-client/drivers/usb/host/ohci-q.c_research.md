# sources/distributed-fs/ceph-client/drivers/usb/host/ohci-q.c

## Purpose

`ohci-q.c` is the OHCI transfer scheduler and completion engine. It creates endpoint descriptors, schedules control/bulk/interrupt/iso EDs, builds TD chains for URBs, processes hardware done lists, handles endpoint halts, unlinks EDs/URBs safely, and gives URBs back to USB drivers.

## Important APIs, Types, and Functions

Important helpers include `urb_free_priv()`, `finish_urb()`, `balance()`, `periodic_link()`, `ed_schedule()`, `periodic_unlink()`, `ed_deschedule()`, `ed_get()`, `start_ed_unlink()`, `td_fill()`, `td_submit_urb()`, `td_done()`, `ed_halted()`, `add_to_done_list()`, `update_done_list()`, `finish_unlinks()`, `takeback_td()`, `process_done_list()`, and `ohci_work()`.

## Control Flow

URB enqueue obtains or creates an ED, schedules it if idle, and calls `td_submit_urb()`. TD submission builds transfer descriptors by pipe type: control setup/data/status, bulk/interrupt 4 KiB chunks with optional zero packet, and one TD per isochronous packet. Periodic EDs are balanced into the 32-branch schedule tree by frame load, while control and bulk EDs form tail-linked lists. Hardware completion writes a done-head chain; `update_done_list()` converts DMA TDs through the hash table and normalizes halted EDs; `process_done_list()` computes lengths/status and completes URBs. Unlink requests deschedule EDs, wait at least until the next frame, patch TD chains, finish unlinked URBs, then either idle or reschedule the ED.

## State and Persistence Behavior

The file mutates ED state (`IDLE`, `OPER`, `UNLINK`), TD lists, pending URB list, done-list pointers, periodic load accounting, endpoint toggle carry, HCD bandwidth counters, AMD quirk state for isochronous traffic, and control/bulk/periodic hardware schedule registers. No durable persistence exists.

## Dependencies and Integration Points

It depends on `ohci-mem.c` allocation/hash helpers, `ohci.h` descriptor formats, USB core URB/endpoint APIs, DMA addresses prepared by HCD glue, `usb_calc_bus_time()`, AMD PCI quirk helpers, and `ohci_irq()`/watchdog calls into `update_done_list()` and `ohci_work()`.

## Risks and Test Signals

Risks include schedule-tree load bugs, races while hardware sees EDs being unlinked, short-read and halt recovery corner cases, isochronous late-frame handling, data-toggle preservation during unlink, done-list hash corruption, and reentrant completion callbacks. Test signals include bulk SG transfers, control requests with/without data, interrupt bandwidth limits, isochronous ASAP and late URBs, URB cancellation storms, endpoint disable waiting paths, and injected TD error condition codes.

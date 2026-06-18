# sources/distributed-fs/ceph-client/drivers/usb/host/uhci-q.c

## Purpose
`uhci-q.c` is the UHCI transfer scheduler and completion engine. It allocates TDs and QHs, builds TD chains for control/bulk/interrupt/isochronous URBs, links QHs into the UHCI frame/skeleton schedule, manages bandwidth and full-speed bandwidth reclamation, handles URB dequeue, scans completed transfers, maps TD errors to Linux statuses, and gives URBs back to usbcore.

## Important APIs, Types, And Functions
Public-to-core callbacks are `uhci_urb_enqueue()` and `uhci_urb_dequeue()`. Allocation helpers include `uhci_alloc_td()`, `uhci_free_td()`, `uhci_alloc_qh()`, `uhci_free_qh()`, `uhci_alloc_urb_priv()`, and `uhci_free_urb_priv()`. Submit paths are `uhci_submit_control()`, `uhci_submit_common()`, `uhci_submit_bulk()`, `uhci_submit_interrupt()`, and `uhci_submit_isochronous()`. Completion paths are `uhci_result_common()`, `uhci_result_isochronous()`, `uhci_scan_qh()`, and `uhci_scan_schedule()`. Schedule maintenance includes `uhci_activate_qh()`, `uhci_unlink_qh()`, `uhci_make_qh_idle()`, `link_interrupt()`, `link_async()`, ISO frame-list insertion/removal helpers, and FSBR helpers.

## Control Flow
Enqueue links the URB to usbcore, allocates per-URB state, finds or creates an endpoint QH, builds the correct TD sequence, adds the URB to the QH queue, and activates the QH if it can run immediately. Control TDs include SETUP, data, status, and a new dummy TD. Bulk and interrupt TDs support scatter-gather, zero-length packet termination, data toggle management, and interrupt-on-complete. ISO TDs are inserted directly into frame-list slots rather than through hardware QHs. Dequeue marks an URB unlinked, removes ISO TDs early, and unlinks the QH so hardware has time to stop referencing descriptors. Schedule scans walk skeleton lists, detect advancement/timeouts, collect TD results, perform toggle fixups after short/error/dequeued transfers, give back completed URBs, release bandwidth, and eventually move unlinked QHs to idle.

## State And Persistence Behavior
All state is in `struct uhci_hcd`, `struct uhci_qh`, `struct uhci_td`, and `struct urb_priv`. Hardware-visible state is DMA descriptors in pools and the frame list. Software state tracks queue membership, dummy/post TDs, QH state, unlink frame, bandwidth reservations, FSBR state, last ISO frame, and toggle fixup needs. No state persists after HCD stop; descriptors are freed or recycled through pools.

## Dependencies And Integration Points
The queue engine depends on usbcore URB/endpoint APIs, DMA mappings already prepared by usbcore, UHCI descriptor/register definitions, timers, root-hub timer for forced scans, and the `uhci_up_cachep` slab from module init. It is included by `uhci-hcd.c`, so it directly calls shared core functions and is called by interrupt/root-hub polling paths.

## Risks And Edge Cases
This file carries most UHCI correctness risk. Hardware asynchronously updates descriptors, so memory barriers and `READ_ONCE()` accessors matter. QHs must remain unlinked for more than one frame before becoming idle. Short transfers require careful TD pruning and data-toggle repair. Old Intel controllers may leave QH elements pointing at inactive completed TDs; `uhci_advance_check()` advances them manually. FSBR modifies async skeleton links and must be timed out carefully. ISO scheduling can fail if too far in the future or if frames fall behind. Error unwinds must avoid freeing active dummy TDs.

## Test Signals
Test all transfer types, scatter-gather bulk, control short reads, `URB_SHORT_NOT_OK`, `URB_ZERO_PACKET`, ISO ASAP and non-ASAP scheduling, interrupt bandwidth exhaustion, dequeues before and during execution, endpoint disable waits, stuck queue recovery, FSBR enable/timeout, and controller stop with pending URBs. Debugfs schedule checks are useful for detecting QH/TD link mismatches.

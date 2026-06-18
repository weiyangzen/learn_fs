# sources/distributed-fs/ceph-client/drivers/usb/host/fhci-sched.c

## Purpose
`fhci-sched.c` is the FHCI transaction scheduler and interrupt engine. It converts queued ED/TD work into per-frame packets, enforces frame byte/time limits, handles SOF/timer/USB events, detects connect/disconnect, and schedules the tasklet that gives completed URBs back to the USB core.

## Important APIs, Types, and Functions
- Scheduler: `fhci_schedule_transactions()`, `scan_ed_list()`, `add_packet()`, `rotate_frames()`, and `fhci_flush_all_transmissions()`.
- Completion: `fhci_transaction_confirm()`, `process_done_list()`, `fhci_transfer_confirm_callback()`.
- Interrupts/events: `fhci_irq()`, `fhci_frame_limit_timer_irq()`, `sof_interrupt()`, `fhci_device_connected_interrupt()`, and `fhci_device_disconnected_interrupt()`.
- URB construction: `fhci_queue_urb()` builds EDs and TD chains for all supported pipe types.

## Control Flow
Each SOF starts or transmits the current frame, arms the GTM frame-limit timer, and asks the scheduler to fill remaining frame budget. Scheduling scans iso, interrupt, control, then bulk lists. `add_packet()` computes packet length/data pointer/toggle, rejects work when byte or time budget is exhausted, obtains a packet object, handles dummy receive buffers, adds the TD to the frame list, and submits the hardware transaction. Hardware completion eventually calls `fhci_transaction_confirm()`, which removes the matching frame TD, copies dummy IN data, classifies NAK/errors/shorts, updates toggles and lengths, and moves complete TDs to the done list. The tasklet drains the done list and gives back URBs or continues deletion/halt cleanup.

Connection IRQ flow reads GPIO line state, programs QE clock for low/full speed, sets low-speed mode bits, updates virtual hub status/change flags, computes max bytes per frame, and enables the port. Disconnect clears connection state, stops SOF, enables IDLE detection, and sets the virtual hub connection-change bit.

## State and Persistence Behavior
Primary state includes `actual_frame` fields (`frame_num`, `total_bytes`, `frame_status`, TD list), endpoint lists by transfer type, ED scheduling state, TD retry counters, port status, virtual hub fields, interrupt masks, and the FHCI tasklet. State is volatile; consistency depends on the FHCI spinlock plus explicit IRQ disable/enable around the tasklet and hardware descriptor access.

## Dependencies and Integration Points
This file sits between USB HCD URBs, FHCI queue/memory helpers, `fhci-tds.c` hardware descriptor operations, QE clock and timer APIs, GPIO bus-state sampling, and virtual root hub updates. It also depends on Linux tasklets and IRQ handling.

## Risks and Test Signals
Risks include frame-budget miscalculation, stale actual-frame TDs requiring flush, race-prone interrupt masking inside interrupt context, a FIXME around iso frame-counter rollover, NAK/retry behavior that can affect bulk fairness, and disconnect during in-flight hardware transactions. Test signals include heavy mixed iso/interrupt/control/bulk traffic, frame-limit timer expiry, MSF aborts, NAK storms, repeated short IN packets, low-speed/full-speed connect detection, unplug during active transfer, and tasklet completion under concurrent unlink.

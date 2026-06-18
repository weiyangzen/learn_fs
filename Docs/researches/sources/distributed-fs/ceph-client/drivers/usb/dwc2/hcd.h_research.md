# sources/distributed-fs/ceph-client/drivers/usb/dwc2/hcd.h

## Purpose

`hcd.h` is the host-mode interface and state contract for the DWC2 host controller driver. It declares the software representations of host channels, URB wrappers, queue heads, queue transfer descriptors, transaction types, transaction translator accounting, frame helpers, root-hub/HCD entry points, and descriptor-DMA hooks used by `hcd.c`, `hcd_ddma.c`, interrupt handling, and queue scheduling code.

## Important APIs, types, and functions

- `struct dwc2_host_chan` models one hardware host channel and stores endpoint address/direction/type/speed, max packet, PID, transfer buffer/DMA positions, split transaction metadata, halt flags, descriptor-DMA metadata, interrupt snapshot, QH ownership, and list links.
- `struct dwc2_hcd_pipe_info` stores normalized endpoint data copied from Linux USB pipe/endpoint descriptors.
- `struct dwc2_hcd_iso_packet_desc` mirrors per-packet isochronous offset, length, actual length, and status for DWC2's internal URB wrapper.
- `struct dwc2_hcd_urb` wraps a Linux URB with DWC2-owned fields including buffer/setup DMA, length, actual length, status, error count, interval, flags, pipe info, and flexible isochronous packet descriptors.
- `enum dwc2_control_phase` tracks control transfer phase: setup, data, status.
- `enum dwc2_transaction_type` communicates whether scheduling found periodic, non-periodic, both, or no work.
- `struct dwc2_tt` stores DWC2-specific transaction-translator refcounting and low-speed/full-speed periodic bitmaps in `usb_tt->hcpriv`.
- `struct dwc2_hs_transfer_time` describes high-speed schedule time slices used by periodic scheduling.
- `struct dwc2_qh` stores static endpoint scheduling state and dynamic QTD/channel ownership: endpoint type/direction/speed, toggles, ping state, split state, host/device bus time, intervals, next active frame, descriptor-DMA list state, TT information, timers, and scheduling flags.
- `struct dwc2_qtd` stores transfer-local state: control phase, in-process bit, data toggle, split/isoc progress, error/NAK counters, descriptor counts, URB pointer, QH pointer, and list link.
- Inline helpers provide HCD conversion, safe `HPRT0` read-modify-write setup, pipe classification, debug filtering, frame arithmetic with rollover, core interrupt masking/status, URB status accessors, isochronous descriptor accessors, bandwidth accessors, and QTD unlink/free.
- Exported/prototyped functions include host init/remove, channel cleanup/halt/DDMA transfer start, transaction select/queue, QH/QTD management from `hcd_queue.c`, descriptor DMA QH lifecycle and completion, interrupt handling, stop, B-host detection, dump, data-toggle save, TT info management, speed lookup, and completion.

## Control flow

The header defines the dataflow between Linux USB URBs and hardware channel programming. A Linux URB is represented by `dwc2_hcd_urb`, attached to a `dwc2_qtd`, linked under a `dwc2_qh`, and eventually assigned to a `dwc2_host_chan`. QH/QTD scheduling functions decide when work is eligible; `hcd.c` binds QHs to channels and programs registers; interrupt and DDMA completion code update QTD/URB state and free or requeue QHs.

Frame helpers are used throughout periodic scheduling and descriptor DMA to compare frame numbers modulo the hardware frame counter. The `dwc2_tt` and periodic bitmap fields support full/low-speed traffic through high-speed transaction translators by reserving low-speed schedule slices per TT/port.

## State and persistence behavior

The types in this header define nearly all host-mode persistent state outside `struct dwc2_hsotg`. `dwc2_host_chan` persists per-channel hardware ownership and transfer progress until cleanup or release. `dwc2_qh` persists endpoint-level scheduling state across multiple URBs. `dwc2_qtd` persists one URB's progress until completion/dequeue. `dwc2_hcd_urb` persists the DWC2 view of a Linux URB and is freed at giveback or dequeue.

The header also codifies pointer ownership conventions: endpoint `hcpriv` points to a `dwc2_qh`, Linux URB `hcpriv` points to a `dwc2_hcd_urb`, `dwc2_hcd_urb->qtd` points to its QTD, QTDs live on `qh->qtd_list`, and channels point back to their active QH. Descriptor-DMA state is held in QH descriptor list fields and mirrored into the channel at assignment.

## Dependencies and integration points

`hcd.h` depends on DWC2 register constants and core structures from `core.h`/included compilation units, Linux USB endpoint and URB definitions, kernel list/timer/hrtimer types, DMA address types, and USB speed/endpoint constants.

It is the shared contract among:

- `hcd.c` for HCD registration, URB, channel, root-hub, and power-management operations.
- `hcd_ddma.c` for descriptor-list allocation, frame-list programming, descriptor scanning, and DDMA transfer completion.
- `hcd_queue.c` for QH/QTD scheduling and periodic reservation.
- Interrupt handling for `dwc2_handle_hcd_intr()`, channel interrupt masking, halt statuses, and data-toggle save.

## Risks and edge cases

- Bitfield widths in `dwc2_host_chan` assume USB and DWC2 register field limits; widening endpoint, address, packet, PID, or speed values without adjusting them could truncate state.
- Frame arithmetic helpers rely on modulo assumptions (`FRLISTEN_64_SIZE`, `HFNUM_MAX_FRNUM`) and are critical for rollover-safe scheduling.
- `dwc2_hcd_qtd_unlink_and_free()` only unlinks and frees the QTD; callers must handle URB wrapper cleanup, completion, and QH deactivation correctly.
- Debug helper behavior changes under `CONFIG_USB_DWC2_DEBUG_PERIODIC`, which can significantly increase log volume.
- The header exposes many functions implemented elsewhere; mismatched assumptions about locking are a risk because several prototypes require callers to hold or not hold `hsotg->lock` as documented in implementation comments rather than encoded in types.

## Test signals

Compile-time coverage is a major signal: this header ties together many translation units and will expose prototype/type drift. Runtime signals include stable endpoint `hcpriv` lifecycle, correct URB `hcpriv` cleanup, no frame rollover scheduling regressions in periodic traffic, correct TT refcount allocation/free for hubs, and absence of use-after-free or double-cleanup when channel/QH/QTD ownership changes during dequeue, disconnect, or descriptor-DMA completion.

# sources/distributed-fs/ceph-client/drivers/usb/dwc2/hcd_ddma.c

## Purpose

`hcd_ddma.c` implements host-mode descriptor DMA support for the DWC2 controller. It allocates and frees QH descriptor lists, manages the periodic frame list, initializes descriptor rings for control/bulk/interrupt/isochronous transfers, starts descriptor-DMA channels, scans completed descriptors from interrupt context, updates DWC2 URB/QTD state, gives completed URBs back to the USB core, and releases or requeues host channels.

## Important APIs, types, and functions

- Descriptor and frame index helpers:
  - `dwc2_frame_list_idx()` maps frame numbers to the 64-entry periodic frame list.
  - `dwc2_desclist_idx_inc()` / `dwc2_desclist_idx_dec()` wrap descriptor indexes using high-speed isochronous or generic descriptor-list sizes.
  - `dwc2_max_desc_num()` chooses descriptor-list capacity based on endpoint type and speed.
  - `dwc2_frame_incr_val()` converts QH interval to frame-list increment.
  - `dwc2_frame_to_desc_idx()` maps frame-list index to descriptor index, using 8-descriptor alignment for high-speed isochronous endpoints.
- Allocation and lifecycle:
  - `dwc2_desc_list_alloc()` allocates a DMA descriptor list from the generic or high-speed isochronous kmem cache, maps it for DMA, and allocates the `n_bytes` side array.
  - `dwc2_desc_list_free()` unmaps/frees descriptor memory and `n_bytes`.
  - `dwc2_frame_list_alloc()` / `dwc2_frame_list_free()` allocate/map/free the host periodic frame list.
  - `dwc2_per_sched_enable()` / `dwc2_per_sched_disable()` program `HFLBADDR` and `HCFG_PERSCHEDENA`.
  - `dwc2_hcd_qh_init_ddma()` initializes DDMA fields for a QH and enables periodic scheduling on the first periodic QH.
  - `dwc2_hcd_qh_free_ddma()` frees DDMA QH resources, releases still-assigned channels, and tears down the frame list when appropriate.
- Periodic frame list:
  - `dwc2_update_frame_list()` enables/disables channel bits in the 64-entry frame list based on QH interval, syncs it to the device, and computes channel `schinfo`.
  - `dwc2_calc_starting_frame()` and `dwc2_recalc_initial_desc_idx()` choose a safe initial isochronous descriptor index by skipping current/near-current frames to avoid hardware racing newly activated descriptors.
- Descriptor initialization:
  - `dwc2_fill_host_isoc_dma_desc()` fills one isochronous descriptor, records original byte count, marks it active, advances QTD isochronous progress, and sets IOC at URB boundaries.
  - `dwc2_init_isoc_dma_desc()` activates a bounded set of isochronous descriptors from queued QTDs, handles descriptor-list fullness, and sets IOC on the last activated descriptor.
  - `dwc2_fill_host_dma_desc()` fills one non-isoc descriptor for control/bulk/interrupt traffic, splits large transfers at hardware limits, rounds IN transfers to packet boundaries, handles SETUP descriptors, and advances channel DMA/length state.
  - `dwc2_init_non_isoc_dma_desc()` builds a descriptor chain across one or more QTDs, marks active descriptors in hardware-safe order, and sets IOC/EOL/A on the final descriptor.
- Start/completion:
  - `dwc2_hcd_start_xfer_ddma()` chooses initialization logic by endpoint type, updates the frame list for periodic endpoints, and starts the channel through `dwc2_hc_start_transfer_ddma()`.
  - `dwc2_cmpl_host_isoc_dma_desc()` syncs one isochronous descriptor from device, computes actual length/status, completes URBs when all packets are done, and decrements QH descriptor count.
  - `dwc2_complete_isoc_xfer_ddma()` scans active isochronous descriptors and handles normal IOC, session continuation, dequeue, AHB error, and babble error.
  - `dwc2_update_non_isoc_urb_state_ddma()` interprets descriptor status and halt reason for control/bulk/interrupt URBs.
  - `dwc2_process_non_isoc_desc()` syncs one non-isoc descriptor, updates QTD/URB state, advances control phases, saves toggles, and completes failed or finished URBs.
  - `dwc2_complete_non_isoc_xfer_ddma()` scans descriptor chains for non-isoc endpoints, updates QH data toggle and ping state, and leaves unfinished QTDs queued.
  - `dwc2_hcd_complete_xfer_ddma()` is the external completion entry point used by interrupt handling. It dispatches isoc vs non-isoc completion, releases channels/frame-list entries, requeues QHs with remaining work, selects new transactions, and queues them.

## Control flow

Descriptor-DMA setup begins when a QH is created and `dwc2_hcd_qh_init_ddma()` is called. Split transfers are rejected because DDMA does not support them here. The QH receives a descriptor list and `n_bytes` side array. Periodic QHs also ensure a frame list exists and periodic scheduling is enabled in `HCFG`.

When `hcd.c` selects a QH and assigns a host channel, `dwc2_hcd_start_xfer_ddma()` initializes descriptors. Non-isoc endpoints get a linear descriptor chain, then `dwc2_hc_start_transfer_ddma()` programs `HCTSIZ`, `HCDMA`, and enables the channel. Interrupt endpoints additionally mark frame-list entries. Isochronous endpoints calculate an initial descriptor index only at the start of a session, fill descriptors at interval-spaced indexes, enable frame-list bits, set `chan->ntd` to the maximum descriptor count, and start the channel only once for the session.

Completion enters `dwc2_hcd_complete_xfer_ddma()` from channel interrupt handling with a halt status. Isochronous traffic is special: normal transfer-complete scans descriptors and may continue the session without releasing the channel if queued QTDs remain; serious errors or session end complete remaining QTDs, halt/release the channel, and unlink the QH. Non-isoc completion scans descriptor chains, completes or advances URBs/QTDs, releases the channel, unlinks the QH, and re-adds it if QTDs remain.

After completion/release, the file immediately calls the normal scheduler (`dwc2_hcd_select_transactions()` and `dwc2_hcd_queue_transactions()`) to fill newly available channels. Isochronous continuation can force periodic queueing even when no new QH was selected.

## State and persistence behavior

The QH owns persistent DDMA state: `desc_list`, `desc_list_dma`, `desc_list_sz`, `n_bytes`, `ntd`, `td_first`, `td_last`, and per-QTD isochronous descriptor indexes. `n_bytes` persists the original programmed byte count for each descriptor because hardware overwrites descriptor status with remaining bytes. The host controller state owns the global periodic frame list (`frame_list`, `frame_list_dma`, `frame_list_sz`) and frame-number cache.

DMA synchronization is explicit. Descriptor and frame-list writes are synced for device before hardware consumption; completion paths sync individual descriptors for CPU before reading status. Descriptor lists are mapped with `dma_map_single()` and unmapped during QH free. Frame-list access is protected by `hsotg->lock` during enable/disable/free and synced when modified.

Channel release updates scheduler channel accounting, clears frame-list bits for periodic QHs, cleans hardware channel state, moves channels back to `free_hc_list`, clears `chan->qh`, clears `qh->channel`, resets `qh->ntd`, and zeros the descriptor list if present.

## Dependencies and integration points

`hcd_ddma.c` depends on:

- `hcd.h` for QH/QTD/channel structures, frame helpers, channel cleanup/halt/start, QH queue helpers, URB completion, data-toggle save, and transaction scheduling.
- DWC2 register and descriptor definitions from `core.h`, especially descriptor status bits such as `HOST_DMA_A`, `HOST_DMA_IOC`, `HOST_DMA_EOL`, `HOST_DMA_STS_PKTERR`, byte-count masks, and `HCFG`/`HFLBADDR`.
- Linux DMA APIs for map/unmap/sync, kmem caches for descriptor-list allocation, and USB endpoint/speed constants.

Its main integration point with `hcd.c` is descriptor-DMA transfer start from `dwc2_queue_transaction()` and hardware channel programming through `dwc2_hc_start_transfer_ddma()`. Its main integration point with interrupt handling is `dwc2_hcd_complete_xfer_ddma()`.

## Risks and edge cases

- The allocation path maps descriptor lists as `DMA_TO_DEVICE` but error/free paths unmap with `DMA_FROM_DEVICE` in this source; that direction mismatch is worth auditing against the DMA API expectations for this platform.
- Isochronous descriptor indexing is complex and race-prone. The code skips frames to prevent hardware fetching newly programmed descriptors out of order, and comments acknowledge alternative channel-retention behavior and frame rollover TODOs.
- `dwc2_cmpl_host_isoc_dma_desc()` computes `frame_desc_idx` by masking with `usb_urb->number_of_packets - 1`, which assumes power-of-two packet counts for correct modulo behavior; this deserves scrutiny if arbitrary isochronous packet counts reach this path.
- DDMA rejects split transfers outright. Any configuration enabling descriptor DMA while needing split traffic must fall back or fail cleanly.
- Completion can call into URB giveback callbacks that dequeue more URBs. Several checks guard against continuing after `DWC2_HC_XFER_URB_DEQUEUE`, but this remains a high-risk lifecycle area.
- Descriptor active-bit ordering matters. The code delays setting `HOST_DMA_A` on previous descriptors until later descriptors are populated to avoid hardware seeing partially built chains.
- Serious isochronous errors complete all queued URBs with failure status, even if some descriptors may have succeeded; this is conservative but can affect class drivers expecting per-packet partial success.

## Test signals

Strong runtime signals include descriptor-DMA control transfers completing setup/data/status phases, bulk IN/OUT transfers larger than one descriptor, interrupt endpoint scheduling through the frame list, high-speed and full-speed isochronous streams with correct per-packet status and `start_frame`, URB dequeue from completion callbacks, AHB/babble/stall/xact error handling, NYET-to-ping-state propagation, and channel reuse after DDMA release.

Instrumentation should watch descriptor `A/IOC/EOL` bits, `qh->ntd`, `td_first/td_last`, frame-list bits, DMA sync warnings, `chan->qh` ownership, `free_hc_list` membership, and absence of leaks in descriptor caches/frame-list allocation after endpoint disable and HCD remove.

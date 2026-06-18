# sources/distributed-fs/ceph-client/drivers/usb/host/xhci-sideband.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/host/xhci-sideband.c` implements the exported xHCI sideband API used by external client drivers to share selected xHCI endpoint transfer rings and secondary interrupter event rings with a non-host execution agent. The source was read as a complete 494-line file. Its practical role is to let a sideband client register ownership against a USB interface, add non-stream endpoints, obtain scatter-gather descriptions for controller-owned rings, create/remove a secondary interrupter, and tear the whole association down without leaving xHCI virtual-device state marked as offloaded.

## Important APIs, Types, and Functions

Important exported entry points are `xhci_sideband_register`, `xhci_sideband_unregister`, `xhci_sideband_add_endpoint`, `xhci_sideband_remove_endpoint`, `xhci_sideband_stop_endpoint`, `xhci_sideband_get_endpoint_buffer`, `xhci_sideband_get_event_buffer`, `xhci_sideband_create_interrupter`, `xhci_sideband_remove_interrupter`, `xhci_sideband_interrupter_id`, `xhci_sideband_check`, and `xhci_sideband_notify_ep_ring_free`. Internal helpers are `xhci_ring_to_sgtable`, `__xhci_sideband_remove_endpoint`, and `__xhci_sideband_remove_interrupter`.

The central data object is `struct xhci_sideband` from the public sideband header. This file populates its `xhci`, `vdev`, `intf`, `type`, `notify_client`, `ir`, `eps[]`, and `mutex` fields and also writes the reciprocal `struct xhci_virt_device::sideband` and `struct xhci_virt_ep::sideband` links. It depends on xHCI-internal objects such as `struct xhci_hcd`, `struct xhci_virt_device`, `struct xhci_virt_ep`, `struct xhci_ring`, `struct xhci_segment`, and secondary interrupter allocation/removal helpers.

## Control Flow

Registration starts from a USB interface. `xhci_sideband_register` derives the USB device, HCD, and `struct xhci_hcd`, rejects unaddressed devices and all types except `XHCI_SIDEBAND_VENDOR`, allocates a sideband object, initializes its mutex, and then takes `xhci->lock` to verify and install exclusive sideband ownership on `xhci->devs[slot_id]`. Endpoint handoff is separate: `xhci_sideband_add_endpoint` locks the sideband mutex, verifies the virtual device still exists, converts the host endpoint descriptor to an xHCI endpoint index, rejects stream-capable endpoints and endpoints already used by any sideband, then stores both the endpoint-side and sideband-side links.

Ring access flows through `xhci_sideband_get_endpoint_buffer` or `xhci_sideband_get_event_buffer`, both of which validate the sideband relationship and call `xhci_ring_to_sgtable`. That helper walks the ring segments, translates each segment DMA allocation into pages with `dma_get_sgtable`, builds a combined scatterlist with `sg_alloc_table_from_pages`, and stores the first segment DMA address in `sg_dma_address(sgt->sgl)` so the client can discover the ring IOVA. Interrupter flow is similarly explicit: `xhci_sideband_create_interrupter` creates one secondary interrupter for the sideband, configures `ip_autoclear`, and exposes its target ID through `xhci_sideband_interrupter_id`; removal calls `xhci_remove_secondary_interrupter`.

Unregistration is the cleanup root. `xhci_sideband_unregister` takes the sideband mutex, removes every tracked endpoint by issuing synchronous stop-endpoint commands, removes the secondary interrupter, clears `sb->vdev`, then takes `xhci->lock` to clear `sb->xhci` and `vdev->sideband` before freeing the sideband object.

## State and Persistence Behavior

The file owns only in-kernel lifetime state. There is no file-backed persistence. Sideband state persists while a registered client holds the `struct xhci_sideband` pointer. Endpoint state is represented by reciprocal pointers in `sb->eps[]` and `ep->sideband`; virtual-device state is represented by `vdev->sideband`; event routing state is represented by `sb->ir`. Ring memory is not allocated here and remains owned by xHCI, while callers receive temporary `struct sg_table` objects that they must free.

Concurrency is split between `sb->mutex` for sideband membership/interrupter changes and `xhci->lock` for virtual-device ownership. Endpoint removal synchronously stops the endpoint so xHCI command completion can perform ring cleanup before client access is considered invalid. `xhci_sideband_notify_ep_ring_free` sends a synchronous callback opportunity to the sideband client before a transfer ring is freed.

## Dependencies and Integration Points

Direct dependencies are `<linux/usb/xhci-sideband.h>`, `<linux/dma-direct.h>`, and `"xhci.h"`. The API integrates with USB interface drivers that need vendor sideband/offload behavior, xHCI virtual device and endpoint internals, the secondary interrupter allocator, DMA scatterlist helpers, and USB offload power-management checks via `usb_offload_check`. The sideband client must know how to write xHCI TRBs and target the returned interrupter ID when routing completion events.

## Risks and Edge Cases

The largest correctness risk is ownership lifetime: a sideband client must stop touching endpoint and event rings after removal or unregister, because the backing xHCI ring storage may be cleaned up immediately after the synchronous callbacks. `xhci_ring_to_sgtable` exposes controller DMA memory to another agent; DMA mask mismatches are called out in a comment and can make a sideband device unable to access the returned IOVA. Stream endpoints are rejected, so clients requiring bulk streams need a different model. Error handling in the sg-table conversion is sensitive to partial allocation and page accounting; callers must treat a `NULL` return as no safe ring access. Power-management users of `xhci_sideband_check` must first ensure downstream devices are marked offload-PM-locked, otherwise the active-sideband answer can be stale.

## Test Signals

Useful signals include module build coverage with `CONFIG_USB_XHCI_SIDEBAND`, sideband registration/unregistration under device disconnect, endpoint add/remove on all endpoint types with streams rejected, secondary interrupter create/remove and target-ID routing, sg-table validation against multi-segment endpoint and event rings, ring-free callback ordering, and runtime/system suspend paths using `xhci_sideband_check` while offload devices are active.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/cdns2/cdns2-debug.h -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/cdns2/cdns2-debug.h

## Purpose
This header provides inline string decoders for CDNS2 USB/DMA interrupt state, endpoint transfer rings, and TRBs. It supports trace/debug output without owning runtime behavior.

## Important APIs, Types, And Functions
`cdns2_decode_usb_irq()` decodes USB and external IRQ bits. `cdns2_decode_dma_irq()`, `cdns2_decode_epx_irq()`, and `cdns2_decode_ep0_irq()` decode DMA endpoint interrupt/status bits. `cdns2_raw_ring()` formats a transfer ring including dequeue/enqueue indexes, free TRB count, cycle states, and raw TRB words. `cdns2_trb_type_string()` and `cdns2_decode_trb()` format normal and link TRBs.

## Control Flow
These functions are pure formatting helpers used by trace/debug code. They append into caller-provided buffers with `scnprintf()` and warn if the buffer fills exactly to `size - 1`.

## State And Persistence
No state is stored here. The helpers inspect `struct cdns2_endpoint`, `struct cdns2_ring`, and `struct cdns2_trb` state supplied by callers.

## Dependencies And Integration Points
The header depends on register bit definitions, TRB macros, and `cdns2_trb_virt_to_dma()` from the CDNS2 gadget code/header. It is indirectly tied to `cdns2-trace.h` formatting.

## Risks
The helpers assume `TRBS_PER_SEGMENT <= 40` before dumping every TRB; with the current larger ring size they report that the ring is too big rather than dumping all entries. Buffer truncation detection is approximate. Because this is inline debug code, macro/type changes in `cdns2-gadget.h` can break trace builds.

## Test Signals
Enable tracing/debug formatting and check decoded USB reset/setup/suspend/LPM, endpoint IOC/ISP/TRBERR/DESCMIS/ISOERR, and TRB text for normal and link descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/cdns2/cdns2-debug.h -->

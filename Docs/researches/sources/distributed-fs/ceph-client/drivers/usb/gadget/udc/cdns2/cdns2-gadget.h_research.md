# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/cdns2/cdns2-gadget.h

## Purpose

`cdns2-gadget.h` is the private hardware and software contract for the Cadence USBHS-DEV CDNS2 gadget controller driver. It defines the MMIO register layouts for EP0, non-control endpoints, interrupt registers, common USB registers, and ADMA registers, plus the transfer-ring/TRB formats and the in-memory `cdns2_device`, `cdns2_endpoint`, and `cdns2_request` objects used by the implementation files. The header does not implement behavior, but it fixes the bit-level interface that all CDNS2 gadget, EP0, PCI, tracing, and debug code rely on.

## Important APIs, Types, And Constants

The register structures are packed/aligned views over the device MMIO aperture: `struct cdns2_ep0_regs`, `struct cdns2_epx_regs`, `struct cdns2_interrupt_regs`, `struct cdns2_usb_regs`, and `struct cdns2_adma_regs`. Their companion bit masks define EP0 control/status bits, endpoint configuration fields, USB/LPM/pullup bits, and ADMA endpoint status/command bits.

The DMA ring contract is encoded by `struct cdns2_trb` and the TRB constants. `TRBS_PER_SEGMENT` is 600, with two additional reserved TRBs for isochronous handling. `TRB_NORMAL` and `TRB_LINK` describe data and link descriptors; `TRB_CYCLE`, `TRB_TOGGLE`, `TRB_ISP`, `TRB_CHAIN`, and `TRB_IOC` drive hardware ownership and completion signaling. `TRB_BUFF_LEN_UP_TO_BOUNDARY()` exists because TRB buffer pointers must not cross 4 KiB boundaries.

The core driver state is split among `struct cdns2_ring`, `struct cdns2_endpoint`, `struct cdns2_request`, and `struct cdns2_device`. The device object holds register bases, IRQ, DMA pool, EP0 setup/request state, endpoint table, selected DMA endpoint, wake/self-powered flags, pending status work, supported endpoint bitmap, burst optimization table, and on-chip buffer sizes.

## Control Flow And State

The header implies a ring-driven data path: gadget requests are wrapped as `cdns2_request`, mapped to TRBs, placed on a `cdns2_endpoint.ring`, and moved between `pending_list` and `deferred_list` according to ring space and hardware progress. Completion uses `start_trb`, `end_trb`, `finished_trb`, and `num_of_trb` to account for partial descriptor progress. EP0 is modeled with setup, data, and status stages, plus `ep0_preq`, `setup`, and `pending_status_request`.

Endpoint persistence is in memory and MMIO only. `ep_state` bit flags track enabled, stalled, wedge, claimed, full ring, pending stall, and deferred doorbell state. Ring cycle bits persist producer/consumer ownership while the driver is loaded. The controller state is not durable across driver removal or reset.

## Dependencies And Integration Points

The header depends on Linux USB gadget APIs, DMA direction definitions, kernel bit helpers, endianness types, and MMIO access conventions. `cdns2-pci.c` fills `struct cdns2_device` platform fields and calls `cdns2_gadget_init()`/`cdns2_gadget_remove()`. `cdns2-trace.h` inspects endpoints, requests, TRBs, and ADMA registers for tracepoints.

## Risks

The main risks are hardware contract drift and bitfield misuse. Register structures rely on exact offsets, packed layout, alignment, and mixed 8/16/32-bit accesses. The endpoint existence macro encodes direction bits in `eps_supported`, so platform glue must populate the bitmap consistently. TRB boundaries, ring wrap, and cycle toggling can cause stuck transfers, duplicate completions, or DMA reading stale descriptors.

## Test Signals

Useful signals include successful gadget registration, EP0 enumeration, tracepoints for request enqueue/giveback and TRB completion, DMA endpoint interrupt status without TRB or descriptor-missing errors, and suspend/resume/LPM handling. Ring pressure tests should watch `EP_RING_FULL`, `EP_DEFERRED_DRDY`, and deferred request behavior.

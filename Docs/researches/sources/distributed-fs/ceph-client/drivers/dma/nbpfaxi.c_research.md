# sources/distributed-fs/ceph-client/drivers/dma/nbpfaxi.c

## Purpose
`nbpfaxi.c` is a dmaengine driver for Renesas NBPFAXI64 DMA controllers. It supports memory copy and slave DMA using hardware link descriptors, per-channel completion interrupts, and a separate error interrupt.

## Important APIs, Types, and Functions
- `struct nbpf_config` identifies model-specific channel count and buffer size.
- `struct nbpf_link_reg` is the packed hardware link descriptor loaded by the DMAC.
- `struct nbpf_link_desc`, `struct nbpf_desc`, and `struct nbpf_desc_page` implement a page-sized descriptor allocator containing high-level dmaengine descriptors, software link wrappers, and DMA-mapped link registers.
- `struct nbpf_channel` contains one dmaengine channel, MMIO base, IRQ, terminal/request-line configuration, slave bus settings, descriptor lists (`free_links`, `free`, `queued`, `active`, `done`), `running`, and paused state.
- `nbpf_prep_one()` programs one hardware link for memcpy or slave direction, including bus-width, burst, request-line, link-mode, interrupt-mask, and sweep-buffer bits.
- `nbpf_prep_sg()`, `nbpf_prep_memcpy()`, and `nbpf_prep_slave_sg()` allocate descriptors and generate link chains.
- `nbpf_issue_pending()`, `nbpf_chan_irq()`, `nbpf_chan_tasklet()`, and `nbpf_err_irq()` drive queueing, normal completion, callback invocation, and error abort.
- `nbpf_of_xlate()` accepts two OF cells: terminal id and request-line flags.

## Control Flow
Probe requires a device tree node, chooses controller geometry from compatible data, maps MMIO, gets a clock, reads optional max memory burst properties, discovers one of three supported IRQ layouts, requests the error IRQ and channel IRQs, initializes channel objects, registers `DMA_MEMCPY`, `DMA_SLAVE`, and `DMA_PRIVATE`, enables the clock, configures global level interrupts, registers dmaengine, and registers the OF controller. Channel allocation initializes descriptor lists, allocates an initial descriptor page, and writes channel link-mode configuration. Prepare allocates enough link descriptors for each SG segment, fills hardware descriptors, syncs them for device access, and returns a dmaengine descriptor. Submit moves descriptors to `queued`; issue splices them to `active` and starts the first descriptor if idle. Completion IRQ acknowledges the channel, moves `running` to `done`, starts the next active descriptor, and schedules the tasklet. The tasklet completes cookies and invokes callbacks, recycling descriptors immediately if acknowledged or marking them `user_wait` until acked. Error IRQs clear hardware errors, idle the affected channel, and abort queued/active/done descriptors without callbacks.

## State and Persistence
No persistent storage is used. Runtime state lives in per-channel descriptor lists, DMA mappings for link descriptors, slave configuration fields, terminal/request flags, `running`, and `paused`. Hardware state includes channel control/configuration registers, link descriptor pointers, current transaction byte count, global interrupt style, and error/end status registers. Runtime PM only toggles the controller clock.

## Dependencies and Integration Points
The driver integrates with platform devices, OF matching for `renesas,nbpfaxi64dmac*` compatibles, `dt-bindings/dma/nbpfaxi.h` request flags, dmaengine memcpy/slave APIs, `of_dma_controller_register()`, clk APIs, IRQ APIs, and streaming DMA mapping for hardware descriptors. It supports platform id-table names as well as OF matches.

## Risks and Edge Cases
- `nbpf_desc_page_alloc()` uses `GFP_DMA` page allocation and maps each link register separately; mapping failures must unwind correctly, and the local unwind uses `sizeof(hwdesc)` instead of `sizeof(*hwdesc)` in the unmap-error path.
- Hardware descriptor `next` fields are cast to 32 bits, so effective descriptor addressing assumes reachable DMA addresses despite the wider system DMA API.
- Error handling intentionally drops callbacks for aborted descriptors; clients must tolerate silent completion loss after hardware errors.
- `nbpf_pause()` sets suspend and then clears enable to terminate sweep-buffer style reception, which is tailored to variable-length receive clients.
- Descriptor allocation can expand dynamically under memory pressure but prepare paths return `NULL` if new descriptor pages cannot be allocated.

## Test Signals
Good validation includes build coverage for each model table entry, OF xlate with valid/invalid two-cell specs, memcpy dmatest, slave SG with narrow and wide bus widths, optional max burst properties, shared and per-channel IRQ layouts, pause-on-receive residue behavior, descriptor recycling after delayed async ack, and forced error IRQ handling.

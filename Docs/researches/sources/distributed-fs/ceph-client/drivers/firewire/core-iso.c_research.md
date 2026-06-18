# sources/distributed-fs/ceph-client/drivers/firewire/core-iso.c

### Purpose
`core-iso.c` provides FireWire isochronous support: page-backed DMA buffers, driver-backed ISO context lifecycle and queueing, completion flushing, stop handling, and client-side IRM channel/bandwidth allocation.

### Important APIs, Types, And Functions
Exports include `fw_iso_buffer_init()`, `fw_iso_buffer_destroy()`, `__fw_iso_context_create()`, `fw_iso_context_destroy()`, `fw_iso_context_start()`, `fw_iso_context_queue()`, `fw_iso_context_queue_flush()`, `fw_iso_context_flush_completions()`, `fw_iso_context_stop()`, and `fw_iso_resource_manage()`. Internal helpers include `fw_iso_buffer_alloc()`, `fw_iso_buffer_map_dma()`, `fw_iso_buffer_lookup()`, `manage_bandwidth()`, `manage_channel()`, and `deallocate_channel()`.

### Control Flow, State, And Persistence
Buffer allocation bulk-allocates zeroed DMA32 pages and stores a page array; mapping creates one DMA mapping per page and records direction. Destroy unmaps all DMA addresses and releases pages. Context creation delegates to the card driver, then fills common metadata and emits tracepoints for outbound/single-receive/multichannel possibilities. Start, set-channels, queue, flush-queue, flush-completions, and stop are thin traced wrappers around card driver methods. Completion flush disables the context work item around the driver's flush callback; stop calls the driver then cancels work. Resource management uses compare-swap transactions to the IRM's bandwidth and channel registers, handling generation changes, 1394-1995 retry behavior, channel bit ordering, and rollback if bandwidth allocation fails after channel allocation.

### Dependencies, Integration Points, Risks, And Test Signals
This file depends on DMA mapping, page allocation, `struct fw_card_driver` ISO methods, transaction helpers, CSR register constants, tracepoints, and cdev mmap/ISO ioctls. Risks include DMA mapping unwind using the intended direction, noncontiguous buffer offset lookup edge cases, deadlock if flush/stop is called from the context work itself, generation-stale resource semantics, and IRM compare-swap contention. Test signals include buffer allocation failure unwind, mmap DMA map/unmap, transmit/receive/multichannel context creation, queue validation from cdev, completion flush from process context, stop canceling work, allocation/deallocation of high and low channel registers, bandwidth rollback, and `-EAGAIN` on stale generation allocation.

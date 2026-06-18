# sources/distributed-fs/ceph-client/drivers/media/pci/pt3/pt3_dma.c

Purpose: Implements PT3 DMA buffer allocation, circular descriptor construction, DMA engine start/stop, and polling-time processing of newly written transport-stream access units.

Important APIs, types, and functions: `pt3_alloc_dmabuf()` allocates coherent data buffers and descriptor pages, then builds a circular xfer descriptor list. `pt3_free_dmabuf()` releases them. `pt3_init_dmabuf()` writes canary bytes at access-unit boundaries and resets indices. `pt3_start_dma()` and `pt3_stop_dma()` program per-FE DMA registers. `pt3_proc_dma()` detects completed access units and feeds packets to DVB demux. `get_dma_base()` maps adapter index to hardware DMA register order.

Control flow: Allocation creates `pt3->num_bufs` coherent data buffers, marks them unwritten, calculates descriptor page count, fills descriptors with 4096-byte transfers, chains descriptor pages, and loops the last descriptor back to the first. Start writes descriptor low/high addresses and sets DMA control. Stop writes stop control and polls status up to five times. Processing checks whether the current canary is still present; if not, it advances access-unit by access-unit until it reaches an unwritten canary, feeding complete 128-packet units to demux and resetting canaries as it consumes.

State and persistence: Per-adapter DMA state includes data buffers, descriptor pages, buffer index, offset, allocated counts, and initial discard count set by the fetch thread. Hardware descriptor and DMA control registers are programmed on each start.

Dependencies and integration points: Called from `pt3.c` adapter allocation, feed start/stop, fetch thread, suspend, and resume. Uses PCI DMA coherent API, MMIO register helpers, and DVB software demux filtering.

Risks: Canary-based completion assumes real TS data will not preserve the canary byte at exact access-unit starts; this is a pragmatic hardware protocol but can miss writes if the canary value remains. `pt3_stop_dma()` returns `-EIO` after fixed 250 ms max wait. Allocation failure cleanup depends on counts being updated immediately after each allocation. `get_dma_base()` swaps indices 1 and 2 to match hardware order, which is easy to regress.

Test signals: Validate descriptor ring for min/max buffer counts, page boundary chaining, last descriptor loopback, index remapping for all four adapters, canary initialization and consumption, wraparound packet feeding, initial discard behavior, DMA stop timeout, and allocation failure cleanup after partial data/descriptor allocation.

# sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/saa7164-buffer.c

Purpose: allocates, formats, activates, and frees firmware/DMA buffers for SAA7164 streaming ports, plus small user-space staging buffers.

Important APIs, types, and functions: `saa7164_buffer_alloc()` allocates a `struct saa7164_buffer`, coherent DMA data memory, and coherent page-table memory. `saa7164_buffer_dealloc()` frees those resources. `saa7164_buffer_zero_offsets()` clears a hardware write offset. `saa7164_buffer_activate()` assigns a buffer to a hardware buffer slot by writing offset and page-table pointers into BAR registers. `saa7164_buffer_cfg_port()` writes pitch/bufsize/counter registers and activates all buffers on a port queue. `saa7164_buffer_alloc_user()` and `saa7164_buffer_dealloc_user()` handle CPU-only buffers.

Control flow: allocation validates length alignment but then sizes DMA data from fixed `SAA7164_PT_ENTRIES` and streaming parameters. It initializes buffers to `0xff`, computes a CRC for debugging, and fills page-table entries with 4K offsets into the coherent data buffer. Port configuration writes shared stream registers, locks `port->dmaqueue_lock`, iterates free buffers, activates each into a hardware slot, and unlocks.

State and persistence: buffer objects track index, flags (`FREE`/`BUSY`), position, actual size, DMA addresses, page-table addresses, and CRC. Hardware BAR state stores the current buffer counter, pitch, buffer size, per-buffer offsets, and page-table pointers. State is volatile and tied to stream lifecycle.

Dependencies and integration points: depends on `struct saa7164_port` descriptor offsets filled by `saa7164-api.c`, DMA coherent allocation, list-based DMA queue state, and low-level `saa7164_writel/readl()` register access. Streaming code in encoder/VBI/DVB paths consumes these buffers.

Risks: `len` is validated but mostly ignored, so callers may assume a requested size that is not actually used. The page-table pointer writes use 32-bit high/low register names in a way marked TODO, so 64-bit DMA addressing is sensitive. `BUG_ON(i > port->hwcfg.buffercount)` should likely be `>=` because activation already rejects `i >= buffercount`; this can attempt one invalid activation before the BUG condition catches later. Freeing non-free buffers logs only a warning. Correct `params->numpagetables`, pitch, and line count are essential to avoid overruns.

Test signals: allocate/deallocate under probe/remove and stream start/stop; verify coherent DMA addresses written into BAR slots; stream TS/PS/VBI long enough to wrap through all buffers; run on systems with DMA addresses above 4GB if supported; enable buffer debug and check offsets advance; exercise failure paths by forcing allocation failures.

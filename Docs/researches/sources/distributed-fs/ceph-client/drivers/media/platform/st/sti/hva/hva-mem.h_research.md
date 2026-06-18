# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/hva/hva-mem.h

Purpose: defines the HVA DMA buffer metadata structure and declares allocation helpers.

Important APIs and types: `struct hva_buffer` stores a debug name, physical DMA address, CPU virtual address, and byte size. Functions are `hva_mem_alloc` and `hva_mem_free`.

Control flow: encoder code requests named buffers through `hva_mem_alloc`, keeps the returned pointer in codec-private state, and frees it at close.

State and persistence: no header-owned state; `struct hva_buffer` instances describe runtime DMA allocations.

Dependencies and integration points: requires `dma_addr_t`, `u32`, and `struct hva_ctx` visibility from including files. Included by `hva-hw.h` and used directly by `hva-h264.c`.

Risks: the buffer abstraction carries no DMA attributes field, so allocation/free policy is fixed in `hva-mem.c`. Callers must not free buffers allocated elsewhere through this API.

Test signals: compile coverage and successful H.264 context allocation/free paths.

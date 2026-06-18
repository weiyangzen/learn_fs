# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-vdi.c

## Purpose
`wave5-vdi.c` implements the Wave5 VDI layer: low-level register access, common firmware memory allocation, coherent DMA buffer allocation/free, safe memory writes/clears, array allocation helpers, and SRAM gen_pool allocation.

## Important APIs and Functions
Public functions include `wave5_vdi_init`, `wave5_vdi_release`, `wave5_vdi_write_register`, `wave5_vdi_read_register`, `wave5_vdi_clear_memory`, `wave5_vdi_write_memory`, `wave5_vdi_allocate_dma_memory`, `wave5_vdi_free_dma_memory`, `wave5_vdi_allocate_array`, `wave5_vdi_allocate_sram`, and `wave5_vdi_free_sram`. `wave5_vdi_allocate_common_memory` is the internal setup helper that chooses common buffer size by product code.

## Control Flow
`wave5_vdi_init` allocates common memory, validates product family, and clears a register range when the BIT processor is not running. MMIO helpers wrap `writel` and `readl`. DMA helpers allocate coherent buffers into `struct vpu_buf`, write bounded data into mapped buffers, clear buffers, and free them while zeroing metadata. SRAM helpers allocate from a gen_pool up to the smaller of configured SRAM size and available pool space.

## State and Persistence
State is stored in `struct vpu_device` buffers: `common_mem`, `sram_buf`, and arrays passed by higher layers. DMA memory persists until explicit free or device release. `wave5_vdi_release` nulls `vdb_register` and frees common memory.

## Dependencies and Integration
The file depends on `wave5-vpu.h`, `wave5-vdi.h`, `wave5-regdefine.h`, Linux DMA coherent APIs, MMIO accessors, and generic allocator APIs. It is the dependency beneath `wave5-hw.c` firmware and framebuffer paths.

## Risks and Test Signals
Risks include freeing zero-sized buffers returning `-EINVAL`, logging but still zeroing on free of an unmapped buffer, possible structure reuse in `wave5_vdi_allocate_array`, product-code size mismatch, and ensuring coherent allocations satisfy firmware address limits. Test signals are VDI init/release, DMA allocation failure injection, boundary checks in `wave5_vdi_write_memory`, SRAM pool exhaustion, repeated array resize/free cycles, and MMIO smoke reads of product registers.

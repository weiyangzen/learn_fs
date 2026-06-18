# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-vdi.h

## Purpose
`wave5-vdi.h` declares the minimal low-level VDI interface and shared DMA buffer structure for Wave5 hardware access.

## Important APIs and Types
The header defines `VPU_PRODUCT_CODE_REGISTER`, register accessor macros `vpu_write_reg` and `vpu_read_reg`, and `struct vpu_buf` with `size`, DMA address `daddr`, and CPU virtual address `vaddr`. It declares `wave5_vdi_init` and `wave5_vdi_release`; additional VDI functions are implemented in `wave5-vdi.c` and used through other headers or visible declarations in included Wave5 headers.

## Control Flow and Integration
Higher layers use `vpu_write_reg` and `vpu_read_reg` to route register access to `wave5_vdi_write_register` and `wave5_vdi_read_register`. The `vpu_buf` structure is the common currency for firmware common memory, work buffers, bitstream ring buffers, framebuffer auxiliary buffers, and SRAM allocations.

## State and Persistence
The header owns no state. `struct vpu_buf` instances persist in `struct vpu_device`, codec info, and frame buffer arrays until freed by VDI helpers or cleanup paths.

## Dependencies and Risks
It depends on `wave5-vpuconfig.h` and Linux string, slab, and device headers. The header uses C++-style comments in a couple of places but remains accepted in kernel C. A risk is that only init/release are declared here while users may rely on declarations from other included headers for the rest of the VDI API; keeping prototypes centralized would reduce drift.

## Test Signals
Compile all Wave5 objects with sparse/W=1 style checks, verify accessor macro type correctness, and run init/release plus DMA buffer lifecycle tests through the higher-level driver.

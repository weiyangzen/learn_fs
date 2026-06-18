# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_vpu2_hw_jpeg_enc.c

## Purpose
Implements Rockchip VEPU2 JPEG baseline encode runs for the Hantro driver. It builds the JPEG header in the destination buffer, configures source crop/format/buffer registers, loads hardware-ordered quantization tables, starts encoding, and records encoded payload size on completion.

## Important APIs, Types, And Functions
- Exports `rockchip_vpu2_jpeg_enc_run()` and `rockchip_vpu2_jpeg_enc_done()`.
- Helpers `rockchip_vpu2_set_src_img_ctrl()`, `rockchip_vpu2_jpeg_enc_set_buffers()`, and `rockchip_vpu2_jpeg_enc_set_qtable()` handle image geometry, DMA addresses, output limit, and luma/chroma quant tables.
- Uses `struct hantro_jpeg_ctx`, `hantro_jpeg_header_assemble()`, `get_unaligned_be32()`, VEPU register macros from `rockchip_vpu2_regs.h`, and vb2 contiguous DMA helpers.

## Control Flow
The run path obtains source/destination buffers, starts the Hantro prepare phase, maps the destination CPU address, assembles the JPEG header using current width/height/quality, switches hardware into JPEG mode, programs overfill crop values from aligned source dimensions to visible destination dimensions, writes output stream address after the header, writes input plane addresses for one to three planes, writes quantization tables in two contiguous blocks, programs endian and AXI settings, ends prepare, and sets encode enable. The done hook reads `VEPU_REG_STR_BUF_LIMIT`, divides by 8, and adds the header size to the output payload.

## State And Persistence
The only persistent software effect is the vb2 destination payload size. Header bytes are written into the destination buffer before hardware output. All other state is per-job register state.

## Dependencies And Integration Points
Selected by Rockchip VEPU2 variants in `rockchip_vpu_hw.c` for JPEG encoding. It depends on Hantro JPEG helpers, V4L2 JPEG quality state, supported Hantro source format descriptors, and the shared VEPU2 IRQ handler.

## Risks And Edge Cases
Destination buffers smaller than `header_size` are warned and get a zero stream limit. `vb2_plane_vaddr()` must be available for header assembly. Horizontal crop requires 4-pixel alignment. Quant-table register ordering is hardware-specific and the two loops must stay separate.

## Test Signals
Exercise JPEG encode across supported input layouts, cropped visible sizes, quality settings, minimal destination buffers, and large 4K/8K boundaries. Check JPEG parseability, payload size accounting, header correctness, and absence of VEPU buffer-full/bus-error IRQs.

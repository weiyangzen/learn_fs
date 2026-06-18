# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_vpu981_hw_av1_dec.c

## Purpose
Implements RK3588 VPU981 AV1 stateless decode support for the Hantro driver, including AV1 syntax-to-register programming, reference-frame bookkeeping, coherent side-buffer management, probability/CDF persistence, film grain generation, and optional postprocessing output.

## Important APIs, Types, And Functions
- Exports `rockchip_vpu981_av1_dec_init()`, `rockchip_vpu981_av1_dec_exit()`, `rockchip_vpu981_av1_dec_run()`, `rockchip_vpu981_av1_dec_done()`, and `rockchip_vpu981_postproc_ops`.
- Maintains `struct hantro_av1_dec_hw_ctx` side buffers for global motion, tile info, film grain, input/output probability tables, sync tile buffer, and loop-filter/CDEF/superres/restoration column data.
- Major setup helpers cover tile layout, reference frames and sign bias, segmentation, loop filter, CDEF, loop restoration, superres, global motion shear parameters, probability tables, film grain synthesis, input/output buffer addresses, and postprocessor registers.

## Control Flow
Initialization allocates all fixed coherent buffers and seeds default AV1 CDFs. Each run starts prepare, loads required AV1 sequence/frame/tile-group controls, reallocates tile-column buffers if the frame needs more columns, cleans stale software references, stores the current destination buffer by source timestamp, writes core syntax parameters, global motion, tile descriptors, references, segmentation, loop filter, dimensions/superres, CDEF, loop restoration, film grain, CDF tables, decode mode, bus/timeouts, output tile addresses, and input stream base/length. It then ends prepare and sets `av1_dec_e`. Completion updates stored CDFs unless frame-end CDF update is disabled. Exit frees every coherent buffer.

## State And Persistence
The AV1 context is stateful across jobs: software reference slots retain timestamps, dimensions, order hints, frame types, and vb2 buffer references; CDF tables persist per refresh flags; coherent side buffers may be reused and grown. No on-disk persistence exists.

## Dependencies And Integration Points
Integrated by `rk3588_vpu981_codec_ops` and `rk3588_vpu981_variant` in `rockchip_vpu_hw.c`. Depends on V4L2 stateless AV1 controls, Rockchip AV1 helper functions for CDFs and film-grain block generation, Hantro buffer helpers, `rockchip_vpu981_regs.h`, DMA-coherent allocation, and the RK3588 AV1 IRQ handler.

## Risks And Edge Cases
Allocation failure paths during init return immediately without freeing earlier allocations until exit, so caller cleanup must run. Reference lookup is timestamp/index sensitive; several paths assume a valid index after distance tests and can be fragile if userspace supplies inconsistent references. Film grain allocates multiple temporary kernel buffers per frame. Tile counts, tile offsets, superres math, 10-bit layouts, and postprocessor format mappings are high-risk areas.

## Test Signals
Cover AV1 key/inter/intra-only frames, refresh flags, missing/invalid references, order-hint wrap, screen-content/intrabc, film grain, CDEF, loop restoration, superres, tiled streams, 8-bit and 10-bit outputs, postprocessed NV12/NV15/P010, and memory-allocation failure injection. Good signals are clean RK3588 decode-ready IRQs, stable CDF behavior over long GOPs, and no DMA leaks on stream close.

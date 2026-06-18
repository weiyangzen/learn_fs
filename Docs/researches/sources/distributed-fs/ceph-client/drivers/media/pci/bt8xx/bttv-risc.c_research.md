# sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttv-risc.c

## Purpose
`bttv-risc.c` builds and manages Bt848 RISC DMA programs for video and VBI capture, calculates scaler/crop register geometry, hooks active per-buffer programs into the persistent main RISC loop, and starts/stops DMA according to active buffers.

## Important APIs, Types, And Functions
Program generators are `bttv_risc_packed()` and internal `bttv_risc_planar()`. Geometry routines are `bttv_calc_geo_old()`, `bttv_calc_geo()`, and `bttv_apply_geo()`. Main-loop and DMA functions are `bttv_risc_init_main()`, `bttv_risc_hook()`, `bttv_set_dma()`, `bttv_start_dma()`, and `bttv_stop_dma()`. Buffer-specific paths are `bttv_buffer_risc()`, `bttv_buffer_risc_vbi()`, `bttv_buffer_activate_video()`, and `bttv_buffer_activate_vbi()`.

## Control Flow
Probe calls `bttv_risc_init_main()` to allocate one page containing a loop with sync and jump slots for odd/even VBI and video fields. Buffer prepare builds per-buffer RISC instructions over the vb2 DMA-SG scatterlist, splitting writes across SG segment boundaries and accounting for packed, planar, raw, interlaced, single-field, and sequential field layouts. IRQ-time activation unlinks selected buffers from queues, applies geometry/color registers, patches main-loop jump slots to point at buffer programs, and sets IRQ flags so the hardware returns control at frame/VBI boundaries. `bttv_set_dma()` updates loop IRQ status, watchdog timer, capture control bits, and FIFO/RISC enable bits.

## State And Persistence
RISC memory is allocated in `struct btcx_riscmem` fields for `btv->main` and each `struct bttv_buffer` top/bottom field. Active state is `btv->curr`, `btv->cvbi`, `btv->loop_irq`, and `btv->dma_on`, protected by `s_lock` in callers. Geometry is stored in each buffer so IRQ activation can program registers without recalculating.

## Dependencies And Integration Points
The file depends on `btcx-risc` allocation helpers, videobuf2 DMA-SG plane descriptors, bttv TV norms/formats/crop state, Bt848 register definitions, and the main IRQ code in `bttv-driver.c`. VBI queueing in `bttv-vbi.c` and video queueing in `bttv-driver.c` both call into these routines.

## Risks
RISC program size estimates and SG walking are memory-safety critical; underestimation or bad offsets can overrun the allocated program or program invalid DMA addresses. Multiple assignments to `r` in `bttv_buffer_risc()` can overwrite an earlier field generation error if later generation succeeds. The VCR hack skips trailing lines, which can surprise format-size assumptions. Activation occurs in IRQ-sensitive contexts and must keep main-loop jump slots consistent with hardware execution.

## Test Signals
Signals include successful buffer prepare for every supported pixel format/field mode, stable streaming without SCERR/OCERR/FDSR messages, correct image geometry after crop/standard changes, VBI data completion, and watchdog timer not firing under normal capture. Debug RISC disassembly should show coherent sync/write/jump sequences.

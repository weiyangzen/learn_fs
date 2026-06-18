# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vpu_buffer.h

## Purpose
`iris_vpu_buffer.h` centralizes Iris VPU buffer sizing constants and inline size calculators used by the Iris decoder/encoder resource code. It does not allocate memory itself; it encodes hardware alignment, codec-specific auxiliary buffer dimensions, maximum picture/tile counts, and line-buffer/QP sizing formulas so platform-specific buffer-size implementations can compute firmware-visible buffer requirements consistently.

## Important APIs, Types, And Constants
- Declares `struct iris_inst` and exports `iris_vpu_buf_size()`, `iris_vpu33_buf_size()`, `iris_vpu4x_buf_size()`, and `iris_vpu_buf_count()`.
- Defines broad alignment and count constants such as `MIN_BUFFERS`, `DMA_ALIGNMENT`, `HFI_ALIGNMENT_4096`, `NUM_HW_PIC_BUF`, `MAX_TILE_COLUMNS`, `MAX_WIDTH`, `MAX_HEIGHT`, `NUM_MBS_4K`, and `NUM_MBS_720P`.
- Provides codec families of constants for H.264, H.265/HEVC, VP9, AV1, and encoder command/slice metadata buffers, including slice-list sizes, CABAC ratios, hardware picture table sizes, Dolby/HDR metadata sizes, ARP sizes, and tile/probability table sizes.
- Inline helpers compute line-buffer and metadata sizes for H.264 and AV1: `size_h264d_lb_fe_top_data()`, `size_h264d_lb_*()`, `size_h264d_qp()`, `size_av1d_lb_fe_*()`, `size_av1d_lb_se_*()`, `size_av1d_lb_pe_top_data()`, `size_av1d_lb_vsp_top()`, `size_av1d_lb_recon_dma_metadata_wr()`, and `size_av1d_qp()`.

## Control Flow And Behavior
The header is purely declarative plus inline arithmetic. Callers pass frame dimensions and buffer type/session context into platform buffer-size routines; these routines compose the constants and helpers to choose sizes for hardware picture buffers, line buffers, slice command buffers, metadata, QP maps, and codec-specific scratch areas. The inline functions mostly align width/height to codec LCU or macroblock boundaries, multiply by per-line or per-control-pack constants, and return byte sizes.

## State And Persistence
There is no state, locking, allocation, or persistence. The only implicit state is compile-time configuration: formulas depend on kernel macros such as `ALIGN`, `DIV_ROUND_UP`, `BIT`, `max`, and fixed hardware limits.

## Dependencies And Integration Points
- Depends on Iris buffer type definitions from headers included by users of this file, especially `enum iris_buffer_type`.
- Used by Iris VPU buffer-size implementations and session setup paths that must program HFI/Iris firmware with correct buffer sizes.
- Hardware-facing constants must match firmware and VPU architecture expectations; the exported function declarations split generic, VPU33, and VPU4x sizing.

## Risks And Edge Cases
- Several formulas use `u32`; extremely large dimensions or future hardware limits could overflow unless callers clamp to supported caps first.
- Duplicate macro definitions exist for some AV1 and PE line-buffer constants, increasing the risk of accidental divergent edits.
- Integer arithmetic such as `VPX_DECODER_FRAME_BIN_RES_BUDGET_RATIO (3 / 2)` truncates to `1`, so callers must not assume fractional precision from that macro.
- The constants are hardware contract values; incorrect alignment or per-codec table sizes can cause firmware rejection, decode corruption, or DMA overruns.

## Test Signals
- Build coverage catches missing type/macro dependencies and duplicate/invalid declarations.
- Runtime test signals are successful stream-on and buffer negotiation for H.264, HEVC, VP9, AV1, and encoder paths across VPU33/VPU4x platforms.
- Stress useful boundaries: 720p threshold, 4K max dimensions, AV1 large tile counts, 10-bit/UBWC formats, and dynamic resolution changes that recompute line buffers.

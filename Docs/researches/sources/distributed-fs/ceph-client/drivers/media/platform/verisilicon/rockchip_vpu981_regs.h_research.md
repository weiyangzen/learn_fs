# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_vpu981_regs.h

## Purpose
Defines RK3588 VPU981 AV1 decoder register descriptors and address offsets used by `rockchip_vpu981_hw_av1_dec.c`. It is the typed bitfield map for AV1 syntax, bus, timeout, reference, side-buffer, and postprocessor programming.

## Important APIs, Types, And Functions
- Defines `AV1_SWREG()` and `AV1_DEC_REG()` to construct `struct hantro_reg` descriptors.
- Exposes descriptors such as `av1_dec_e`, `av1_dec_mode`, segmentation fields, loop-filter fields, reference scaling/sign-bias fields, CDEF/LR/superres fields, probability-table addresses, timeout/bus controls, and postprocessor output format/stride/size fields.
- Defines raw address offsets including `AV1_TILE_OUT_LU`, `AV1_REFERENCE_Y(i)`, `AV1_SEGMENTATION`, `AV1_GLOBAL_MODEL`, `AV1_CDEF_COL`, `AV1_FILM_GRAIN`, `AV1_INPUT_STREAM`, `AV1_PROP_TABLE`, and postprocessor output addresses.

## Control Flow
No runtime control flow exists. AV1 code passes these descriptors to `hantro_reg_write()` and raw offsets to `hantro_write_addr()` while programming a decode job.

## State And Persistence
The header owns no state. It describes the VPU981 MMIO state layout. Software persistence for references and probability tables lives in `struct hantro_av1_dec_hw_ctx`.

## Dependencies And Integration Points
Includes `hantro.h` for `struct hantro_reg`. It is tightly coupled to RK3588 AV1 decoder code and the RK3588 IRQ path in `rockchip_vpu_hw.c`.

## Risks And Edge Cases
Many descriptors encode signed AV1 syntax into unsigned masks, so callers must clamp/transform values before writing. Register numbers are sparse and hardware-specific; wrong offsets can corrupt unrelated decoder or postprocessor state. Because the file is declarative, it cannot enforce valid combinations such as superres, bit depth, or postprocessor formats.

## Test Signals
Build coverage catches descriptor type errors. Runtime signals come from AV1 conformance decode on RK3588, postprocessor format tests, interrupt status readback, and targeted tests for reference scaling, loop restoration, film grain, and timeout behavior.

# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_g2_regs.h

## Purpose
Defines G2 register descriptors, mode constants, interrupt bits, codec-specific fields for HEVC and VP9, address registers, postprocessor/downscale fields, and stream-buffer extension registers.

## Important APIs, Types, And Functions
The key macro is `G2_DEC_REG`, which constructs `struct hantro_reg` descriptors for masked read-modify-write helpers. It declares descriptors such as `g2_mode`, `g2_stream_len`, HEVC reference-list fields, VP9 segmentation/filter/reference-scale fields, output/RS/downscale fields, and address offsets like `G2_OUT_LUMA_ADDR`, `G2_REF_LUMA_ADDR(i)`, and `G2_VP9_PROBS_ADDR`.

## Control Flow And State
No runtime state is stored. The header centralizes the G2 hardware ABI. Some descriptors have legacy and non-legacy variants, and some register numbers are reused by HEVC POC fields and VP9 filter-delta fields depending on decode mode.

## Dependencies And Integration Points
Included by `hantro_g2.c`, G2 HEVC/VP9 runners, and postprocessor code. It depends on `hantro.h` for `struct hantro_reg`.

## Risks And Test Signals
Register descriptor reuse makes accidental cross-codec changes risky. Legacy vs new register fields need SoC-specific test coverage. Useful signals include register dumps from G2 HEVC/VP9 runs, conformance suites on legacy and non-legacy variants, and tests for downscale/postprocessor paths.

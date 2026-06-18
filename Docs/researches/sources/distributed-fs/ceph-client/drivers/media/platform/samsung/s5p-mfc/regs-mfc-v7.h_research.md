# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/regs-mfc-v7.h

## Purpose
This header extends the v6 MFC register contract for v7 hardware. It adds VP8 encoder support, three-plane source address/stride registers, encoded-source plane return registers, VP8 encoder option registers, v7 variant limits, padding bytes, context sizes, and v7 scratch sizing formulas.

## Important APIs, Types, and Constants
Key exports are `S5P_FIMV_CODEC_VP8_ENC_V7`, source first/second/third address and stride registers, encoded source first/second/third address registers, VP8 option/filter/golden-frame/layer registers, `MAX_FW_SIZE_V7`, `MAX_CPB_SIZE_V7`, `MFC_VERSION_V7`, `MFC_NUM_PORTS_V7`, luma/chroma padding constants, context buffer sizes, `S5P_FIMV_SCRATCH_BUF_SIZE_MPEG4_DEC_V7`, and `S5P_FIMV_SCRATCH_BUF_SIZE_VP8_ENC_V7`.

## Control Flow and State
No executable flow exists. The core variant table maps `samsung,mfc-v7` and `samsung,exynos3250-mfc` to v7 buffer sizes and firmware. The command path remains v6-style, while operation code can use these additional registers when v7 capabilities are detected.

## Dependencies and Integration Points
The header includes `regs-mfc-v6.h`, so it depends on the v6 register model. It integrates with `s5p_mfc_cmd_v6.c`, which maps `S5P_MFC_CODEC_VP8_ENC` to the v7 codec id, and with encoder operation code for VP8 controls and multi-plane source programming.

## Risks
VP8 encode is only one part of the stack; V4L2 format exposure, controls, firmware, and register programming must all align. The three-plane registers also increase risk for format-specific plane ordering errors. Exynos3250 uses different clocks in the variant table, so build/runtime tests should include both v7 compatible entries.

## Test Signals
Signals include v7 firmware init, VP8 encode stream output, three-plane source formats, v7 MPEG4 decode scratch allocation, v7 padding behavior, and regression of inherited v6 decode/encode paths.

# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/regs-mfc-v10.h

## Purpose
This header layers MFC v10 register and buffer definitions on top of the v8/v7/v6 register model. It adds HEVC and VP9 codec identifiers, v10-specific clock/state/static-buffer registers, hierarchical encoding controls, and motion-estimation sizing formulas.

## Important APIs, Types, and Constants
The file exports `S5P_FIMV_MFC_CLOCK_OFF_V10`, `S5P_FIMV_MFC_STATE_V10`, decoder static-buffer registers, HEVC encoder option/register fields, hierarchical QP and bitrate layer registers, v10 context buffer sizes, firmware/CPB maxima, `MFC_VERSION_V10`, `MFC_NUM_PORTS_V10`, `S5P_FIMV_CODEC_HEVC_DEC`, `S5P_FIMV_CODEC_VP9_DEC`, `S5P_FIMV_CODEC_HEVC_ENC`, `DEC_VP9_STATIC_BUFFER_SIZE`, and `ENC_V100_*_ME_SIZE` macros.

## Control Flow and State
There is no executable flow. Runtime behavior is enabled by the core variant table in `s5p_mfc.c`, which sets `version_bit = MFC_V10_BIT`, chooses v10 buffer sizes, and points firmware to `s5p-mfc-v10.fw`. Operation code uses these constants to allocate internal memory and program codec-specific registers before host-to-RISC commands.

## Dependencies and Integration Points
It includes `regs-mfc-v8.h`, so v10 inherits the v6+ command and register layout plus v7/v8 extensions. It is consumed through `s5p_mfc_common.h` and the operation layer, and is selected by OF compatible `samsung,mfc-v10`.

## Risks
The size macros assume macro arguments represent macroblock-scale dimensions used consistently by operation code. Passing pixels where macroblocks are expected would over- or under-allocate ME buffers. HEVC and VP9 enablement also depends on firmware support and format tables; mismatches between register constants and advertised V4L2 formats can produce hard-to-debug firmware errors.

## Test Signals
Signals include v10 probe with firmware load, HEVC/VP9 decode, HEVC encode, hierarchical QP/bitrate control programming, VP9 static buffer allocation, and regression tests that v8/v6 codecs still use inherited offsets correctly.

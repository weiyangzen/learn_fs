# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/regs-mfc-v12.h

## Purpose
This header defines the v12 extension of the Samsung MFC register contract. It mostly adjusts context, firmware, CPB, padding, and motion-estimation sizing limits for the v12/FSD generation while inheriting v10 registers.

## Important APIs, Types, and Constants
Exports include `MFC_CTX_BUF_SIZE_V12`, per-codec v12 context sizes, `MAX_FW_SIZE_V12`, `MAX_CPB_SIZE_V12`, `MFC_VERSION_V12`, `MFC_NUM_PORTS_V12`, `S5P_FIMV_CODEC_VP9_ENC`, `MFC_CHROMA_PAD_BYTES_V12`, `S5P_FIMV_D_ALIGN_PLANE_SIZE_V12`, and `ENC_V120_*_ME_SIZE` formulas aligned to 256 bytes.

## Control Flow and State
There is no local control flow. `s5p_mfc.c` maps OF compatible `tesla,fsd-mfc` to a v12 variant using these constants and firmware `s5p-mfc-v12.fw`. `s5p_mfc_ctrl.c` has a v12-specific behavior note: firmware is reloaded for each run because repeated initialization can fail if firmware transfer state is reused.

## Dependencies and Integration Points
The header includes `regs-mfc-v10.h`; all v6+ command semantics and v10 codec extensions remain available. It is included indirectly by `s5p_mfc_common.h`, making the version macros available to variant setup, format gating, and operation code.

## Risks
The v12 path expands CPB size to 7 MiB and changes alignment/padding assumptions. Memory pressure, CMA availability, and IOMMU behavior should be tested. The VP9 encoder codec id is declared here, but user-visible encoder support depends on the encoder format/control path outside this subset.

## Test Signals
Key signals are FSD/v12 probe, repeated open/close cycles proving firmware reload works, high-resolution decode with larger CPB, v12-aligned multi-plane frame allocation, HEVC encode ME buffer allocation, and any VP9 encode exposure tests if the encoder path advertises it.

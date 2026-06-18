# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_offset.h lines 10384-12973

## Scope

This chunk is a generated register-offset slice from the AMDGPU DCN 3.0.2 ASIC register header. It covers line 10384 through line 12973 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_offset.h`. The content is almost entirely `#define` constants of the form `mm<REGISTER_NAME>` plus a matching `mm<REGISTER_NAME>_BASE_IDX`.

The chunk contains 1,203 register-offset macros and 1,203 matching base-index macros. Most of the range uses `_BASE_IDX 2`, while the MPC/MPCC blocks at the end use `_BASE_IDX 3`. There are no functions, data structures, includes, or executable control paths in this chunk.

## Purpose

The purpose of this header slice is to provide compile-time MMIO register identifiers for the DCN 3.0.2 display engine. Driver code elsewhere includes this file, combines these offsets with AMDGPU register access helpers and field-mask/shift headers, and programs display hardware blocks without hard-coding raw offsets at call sites.

This chunk maps several major display hardware areas:

- DIO/DIG/DP/VPG/AFMT/DME instances 3 through 5 for display output links, HDMI/DP packet generation, audio formatting, DisplayPort stream control, and link training.
- DCIO global and chip-level registers for reference clocks, UNIPHY link controls, GPIO/DDC/HPD/AUX pins, panel power sequencing, and backlight PWM.
- DSC compressor instances 0 through 4, including top-level control, DSCCIF, DSCC PPS programming, quality/error counters, debug buses, and perfmon blocks.
- DWB writeback blocks, including flow control, CRC, host read, overflow reporting, color/gamut/remap, and output gamma tables.
- MPC/MPCC compositor blocks, including MPCC pipe selection, gains, background color, memory power, status, and the start of MPCC output gamma/gamut-remap blocks.

## Important Macro Families

### DIO, DIG, DP, VPG, AFMT, and DME

The chunk begins in the tail of a DP2 generic-stream-packet area, with `mmDP2_DP_GSP9_CNTL` through `mmDP2_DP_GSP_EN_DB_STATUS`, so the previous chunk owns most of the DP2 block. It then fully defines display output instances 3, 4, and 5:

- `mmVPG3_*`, `mmVPG4_*`, and `mmVPG5_*` cover video packet generator access/data registers, generic packet update controls, generic status, memory power, ISRC packet access/data, and MPEG info registers.
- `mmAFMT3_*`, `mmAFMT4_*`, and `mmAFMT5_*` cover HDMI/DP audio formatter packet control, audio info, IEC 60958 channel status words, audio CRC, ramp controls, status, interrupt status, audio source selection, and memory power.
- `mmDME3_*` and `mmDME4_*` provide DME control and memory-control registers. There is no visible `DME5` block in this line range.
- `mmDIG3_*`, `mmDIG4_*`, and `mmDIG5_*` define front-end/back-end DIG control, test and CRC registers, HDMI control/status/metadata/audio/ACR/VBI/infoframe/generic-packet registers, TMDS registers, lane enable, DIG version, and force-disable registers.
- `mmDP3_*`, `mmDP4_*`, and `mmDP5_*` define DisplayPort link control, pixel format, MSA fields, DPHY training, CRC, secondary-data packet/audio/timestamp registers, MST MSE rate and slot allocation registers, MSO/DSC/metadata/ALPM/GSP controls, and double-buffer control.

The instance spacing is regular: DIG/DP instance 3 uses the `0x23xx`/`0x24xx` range, instance 4 uses `0x24xx`/`0x25xx`, and instance 5 uses `0x25xx`/`0x26xx`. These macros are likely consumed by instance-specific register-list initializers in DCN link encoder, stream encoder, audio, VPG, and DP code.

### DCIO Global and Chip-Level Blocks

The `dce_dc_dcio_dcio_dispdec` block defines global DCIO registers such as:

- `mmDC_GENERICA`, `mmDC_GENERICB`
- `mmDCIO_CLOCK_CNTL`, `mmDC_REF_CLK_CNTL`
- `mmUNIPHYA_*` through `mmUNIPHYE_*` link and channel crossbar controls
- `mmLVTMA_PWRSEQ_*` panel power sequence controls and state
- `mmBL_PWM_*` backlight PWM controls and lock
- `mmDCIO_GSL_GENLK_PAD_CNTL`, `mmDCIO_GSL_SWAPLOCK_PAD_CNTL`
- `mmDCIO_SOFT_RESET`

The `dce_dc_dcio_dcio_chip_dispdec` block defines GPIO and pad controls for generic GPIO, DDC1 through DDC5, DDCVGA, GENLK, HPD, PWRSEQ, pad strengths, AUX control, RX enable, pull-up enable, and `mmAUXI2C_PAD_ALL_PWR_OK`. These offsets are integration points for GPIO/DDC/AUX/HPD helpers, panel power sequencing, link detection, and display bring-up paths.

### DSC and DC Perfmon

The DSC portion covers compressor instances 0 through 4. Each instance follows the same pattern:

- `mmDSC_TOP<n>_DSC_TOP_CONTROL` and `mmDSC_TOP<n>_DSC_DEBUG_CONTROL`
- `mmDSCCIF<n>_DSCCIF_CONFIG0/1`
- `mmDSCC<n>_DSCC_CONFIG0/1`, `STATUS`, and `INTERRUPT_CONTROL_STATUS`
- `mmDSCC<n>_DSCC_PPS_CONFIG0` through `PPS_CONFIG22`
- memory power, squared-error accumulators, max absolute error, rate-buffer fullness, rate-control-buffer fullness, and test/debug index/data registers

Each DSC instance also has an adjacent DC perfmon block:

- `mmDC_PERFMON19_*` for DSC0
- `mmDC_PERFMON20_*` for DSC1
- `mmDC_PERFMON21_*` for DSC2
- `mmDC_PERFMON22_*` for DSC3
- `mmDC_PERFMON23_*` for DSC4

The PPS register run is particularly important because DSC programming depends on writing the correct picture parameter set into a fixed sequence of hardware registers. Missing or shifted offsets here would corrupt compressed-display setup rather than producing an obvious compile error.

### DWB Writeback

The DWB top block begins at `mmDWB_ENABLE_CLK_CTRL` and includes memory power, flow-control window/source sizing, update control, CRC mask/value registers, output control, backpressure count, host-read control, overflow status/counter, and soft reset.

The writeback perfmon block is `mmDC_PERFMON24_*`.

The DWB color-processing block begins at `mmDWB_HDR_MULT_COEF` and covers:

- gamut remap mode and coefficient format
- A and B gamut remap matrices
- output gamma control, LUT index/data/control
- RAM A and RAM B start/end/offset/region registers for B/G/R channels

This block is register-dense and sequential. Gamma and gamut programming code usually relies on these offsets being contiguous and correctly paired with field definitions.

### MPC and MPCC

The chunk then switches to base index 3 for MPC/MPCC registers. It defines MPCC instances 0 through 4:

- `MPCC_TOP_SEL`, `MPCC_BOT_SEL`
- `MPCC_OPP_ID`
- `MPCC_CONTROL`, `MPCC_SM_CONTROL`
- `MPCC_UPDATE_LOCK_SEL`
- top and bottom gain registers
- background color registers
- `MPCC_MEM_PWR_CTRL`
- `MPCC_STATUS`

The final visible block starts the MPCC output-gamma/gamut-remap area:

- `mmMPCC_OGAM0_*` is complete in this chunk, covering control, LUT access, RAM A/B region programming, and gamut remap A/B matrix registers.
- `mmMPCC_OGAM1_*` begins at line 12916 and continues past the end of this chunk. The next chunk must complete the MPCC_OGAM1 register family.

## APIs, Types, and Functions

This chunk defines no C APIs, types, functions, structs, enums, or inline helpers. Its exported surface is the preprocessor macro namespace:

- `mm...` macros resolve to register offsets.
- `mm..._BASE_IDX` macros identify the register base aperture/index used by AMDGPU register access macros.

The effective API contract is naming and numeric stability. Callers can use these constants directly or through register-list macros that are expanded into DCN hardware structures.

## Control Flow

There is no runtime control flow in this file. The operational control flow occurs in downstream driver code:

1. DCN resource construction selects an ASIC-specific register header.
2. Register-list macros bind these `mm...` constants into encoder, link, audio, DSC, DWB, DCIO, or MPC structures.
3. Runtime display code writes or reads the selected register through MMIO helpers.
4. Hardware state changes according to the written register values.

Because this file has no executable checks, offset correctness is only validated indirectly by compile-time macro resolution and hardware behavior.

## State and Persistence Behavior

The header itself has no persistent state. It names registers that control persistent hardware state while the GPU/display engine is powered:

- Link/output state: DIG, DP, HDMI, TMDS, DPHY, MST, DSC-over-DP, ALPM, and generic packet controls.
- Audio and metadata state: AFMT, VPG, HDMI infoframes, DP secondary data, GSP controls, ISRC, MPEG info, and metadata transmission.
- Board/panel state: DCIO clocks, UNIPHY crossbars, GPIO/DDC/AUX/HPD, panel power sequence, and backlight PWM.
- Compression state: DSC PPS/config/status/debug/error counters and memory power.
- Writeback state: DWB flow control, CRC, host read, overflow, color transforms, and OGAM LUTs.
- Composition state: MPCC routing, gains, background color, update locking, memory power, status, and MPCC OGAM/gamut remap.

Persistence is hardware-scoped: values may survive until reset, power-gating, mode-set reprogramming, or driver teardown depending on the block. The `*_MEM_PWR*`, `*_SOFT_RESET`, `*_UPDATE_*`, `*_DB_*`, and `*_STATUS` register families are especially state-sensitive.

## Dependencies and Integration Points

This chunk depends on the generated ASIC register model matching DCN 3.0.2 hardware documentation. It is normally used together with companion headers that provide field masks/shifts and with DCN source files that define per-block register lists.

Likely integration points include:

- Link encoder and stream encoder code for `DIG<n>`, `DP<n>`, HDMI, TMDS, lane-enable, and force-disable programming.
- DisplayPort link training, MST, DSC-over-DP, and secondary-data packet paths for `DP<n>_*`.
- Audio and infoframe paths for `AFMT<n>_*`, HDMI packet controls, and DP secondary audio registers.
- AUX/DDC/HPD/GPIO/panel/backlight code for `DC_GPIO_*`, `PHY_AUX_CNTL`, `DC_GPIO_AUX_CTRL_*`, `LVTMA_PWRSEQ_*`, and `BL_PWM_*`.
- DSC resource and validation paths for `DSC_TOP<n>_*`, `DSCCIF<n>_*`, and `DSCC<n>_*`.
- Perfmon/debug code for `DC_PERFMON19` through `DC_PERFMON24`.
- Writeback/capture paths for `DWB_*`.
- MPC compositor and color-management paths for `MPCC<n>_*`, `MPCC_OGAM0_*`, and the beginning of `MPCC_OGAM1_*`.

The `_BASE_IDX` split is part of this integration contract: most display I/O, DCIO, DSC, and DWB registers use base index 2, while MPC/MPCC registers use base index 3.

## Risks

- Numeric offset drift is high impact. A wrong register value can program the wrong hardware block while still compiling cleanly.
- Repeated instance blocks make copy/paste or generator errors plausible. DIG/DP/VPG/AFMT instances 3 through 5 and DSC instances 0 through 4 should preserve consistent per-instance spacing and matching register families.
- The chunk begins and ends in the middle of larger logical families: it starts at the tail of DP2 GSP registers and ends inside MPCC_OGAM1. Merge/reconciliation must include neighboring chunks for complete whole-file conclusions.
- `mmAFMT4_*` lacks a visible `base address` comment in this chunk even though surrounding AFMT3 and AFMT5 blocks include one. This may be harmless generated-comment variance, but it is a signal to compare against neighboring generated headers if auditing.
- Base index changes from 2 to 3 at the MPC/MPCC region. Any register-list code that assumes a uniform base index across the source file would misaddress MPCC registers.
- Long sequential LUT/region/PPS register runs are fragile. Missing one macro or shifting one offset can affect a large programmed table.
- Hardware behavior is often only observable on the target ASIC and with real displays, so normal build tests cannot prove register correctness.

## Test Signals

Useful validation signals for this chunk include:

- Build coverage that includes AMDGPU DCN 3.0.2 paths and fails on missing/renamed macros.
- Static comparison against AMD-generated register databases or adjacent known-good DCN headers to confirm offsets, instance spacing, and `_BASE_IDX` values.
- Mode-setting tests across DP and HDMI connectors using DIG/DP instances 3 through 5, including audio, infoframes, metadata packets, DSC, MST, and link-training scenarios.
- AUX/DDC/HPD tests that exercise `DC_GPIO_*`, `PHY_AUX_CNTL`, and `DC_GPIO_AUX_CTRL_*` paths.
- Backlight and panel power-sequence tests for `LVTMA_PWRSEQ_*` and `BL_PWM_*` registers.
- DSC validation with compressed modes, checking PPS programming, interrupt/status behavior, and visual output.
- Writeback tests that verify DWB flow control, CRC values, overflow counters, host read, gamut remap, and output gamma behavior.
- MPC composition tests with multiple planes and color-management changes, checking MPCC routing, gains, background color, OGAM LUT programming, and update locks.
- Perfmon/debug tests that verify `DC_PERFMON19` through `DC_PERFMON24` counters can be selected, started, read, and stopped.

## Chunk Boundary Notes

The preceding chunk should cover the full DP2 block before `mmDP2_DP_GSP9_CNTL`. The following chunk should continue `mmMPCC_OGAM1_*` after `mmMPCC_OGAM1_MPCC_OGAM_RAMA_REGION_10_11_BASE_IDX`. A whole-file merge should treat this document as a partial view of generated register mappings, not as a complete source-file report.

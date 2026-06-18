# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vpe/vpe_6_1_0_sh_mask.h lines 2612-4393

## Scope

This chunk covers the tail of the generated AMD VPE 6.1.0 shift/mask header. The range starts in the VPCM gamut-remap field definitions and runs through the final `#endif` of the header. It contains only C preprocessor constants that describe hardware register bit positions and masks; it has no functions, structs, variables, control statements, allocation, locking, or runtime code.

The covered line range defines field layouts for these VPE display-processing blocks:

- VPCM color management: remaining gamut-remap coefficients, bias values, gamma-correction controls, LUT index/data/control registers, RAMA PWL region descriptors, HDR multiplier, dealpha, coefficient-format selection, memory-power control/status, and debug index/data.
- VPDPP top: clock gate controls, soft reset bits, CRC values/control, and host-read rate control.
- VPMPCC and VPMPC: top/bottom source selection, compositor mode and alpha/global gain fields, background color, memory-power/status, MPC clock/reset/CRC/bypass/background/read-control/pending-status registers.
- VPMPCC OGAM: output-gamma LUT, RAMA region programming, gamut-remap control, coefficient format, and gamut-remap matrix coefficients.
- VPMPCC MCM: shaper LUT, RAMA PWL regions, 3D LUT, 1D LUT, output normalization/offsets, memory-power, and test/debug registers.
- VPMPC output CSC: output muxing, float/denormal controls, denormal clamps, output CSC coefficient format/mode, and CSC matrix coefficients.
- VPFMT and VPOPP: formatter clamps, dynamic expansion, dithering/bit-depth controls, output pipe control, pipe CRC control/results, and top clock control.
- VPCDC and VPEP support: clock/reset, FE/BE surface and viewport configuration, global sync, ready status, memory power, RBBMIF timeout/status/disable bits.
- DC perfmon: performance-counter selection/control/state, perfmon interrupt/control, counter values, and high/low readback fields.

Because the chunk begins after the first VPCM gamut-remap definitions, some adjacent `VPCM_GAMUT_REMAP_*` fields are documented by the prior chunk. This file should be merged with the rest of the source-file chunks before drawing final per-file conclusions.

## Purpose

`vpe_6_1_0_sh_mask.h` is generated hardware metadata for the AMD VPE 6.1 IP block. The constants in this range define how a 32-bit MMIO register value is packed: each field has a `__SHIFT` value and a `_MASK` value. Driver code combines these masks with register offsets from `vpe_6_1_0_offset.h` and AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32`, and `WREG32` to program individual hardware fields without open-coded bit arithmetic.

The direct in-tree consumer is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vpe_v6_1.c`, which includes both:

- `vpe/vpe_6_1_0_offset.h`
- `vpe/vpe_6_1_0_sh_mask.h`

The current `vpe_v6_1.c` code shown in this repository mostly exercises VPEC microcode, ring, interrupt, reset, and queue fields from earlier parts of the same header. The fields in this chunk describe the broader VPE pixel pipeline and diagnostic surface that firmware, command packets, debug tooling, golden settings, or future driver paths can use once the VPE data path is configured beyond ring bring-up.

## Important Macro Families

### VPCM Color Management and Gamma Correction

The first part of the range completes VPCM color-management fields:

- `VPCM_GAMUT_REMAP_C21_C22`, `C23_C24`, `C31_C32`, and `C33_C34` pack two 16-bit matrix coefficients per register. The previous chunk contains the earlier coefficient pairs.
- `VPCM_BIAS_CR_R` and `VPCM_BIAS_Y_G_CB_B` define 16-bit bias fields for RGB/YCbCr-style channel naming.
- `VPCM_COEF_FORMAT` selects bias, post-CSC, and gamut-remap coefficient formats.
- `VPCM_DEALPHA` enables dealpha and alpha-blend behavior.
- `VPCM_HDR_MULT_COEF` provides a 19-bit HDR multiplier coefficient.

The VPCM gamma-correction subsection uses the common AMD color LUT layout:

- `VPCM_GAMCOR_CONTROL` selects gamma-correction mode, PWL disable, current mode, and active bank selection.
- `VPCM_GAMCOR_LUT_INDEX`, `VPCM_GAMCOR_LUT_DATA`, and `VPCM_GAMCOR_LUT_CONTROL` provide indexed LUT access, 18-bit LUT data, write color mask, read color selection, debug read, host selection, and config mode.
- `VPCM_GAMCOR_RAMA_START_*`, `END_*`, `OFFSET_*`, and `REGION_*` fields describe the piecewise-linear RAMA curve programming for B/G/R channels.
- Region registers are packed in pairs. Each region has a 9-bit LUT offset and a 3-bit segment count; two regions are packed into one 32-bit register with the second region starting at bit 16 and segment count at bit 28.

The generated constants also expose `VPCM_MEM_PWR_CTRL`, `VPCM_MEM_PWR_STATUS`, `VPCM_TEST_DEBUG_INDEX`, and `VPCM_TEST_DEBUG_DATA`, which allow the gamma/color-management memory and debug windows to be controlled or inspected.

### VPDPP Top-Level Control and CRC

The `vpe_vpep_vpdpp0_dispdec_vpdpp_top_dispdec` address block defines the top-level display pipe processor controls:

- `VPDPP_CONTROL` contains clock enable and multiple gate-disable bits for VPECLK and DISPCLK domains, plus a test clock selector.
- `VPDPP_SOFT_RESET` individually resets VPCNVC, VPDSCL, VPCM, and VPOBUF sub-blocks.
- `VPDPP_CRC_VAL_R_G` and `VPDPP_CRC_VAL_B_A` expose 16-bit CRC values for color channels and alpha.
- `VPDPP_CRC_CTRL` enables CRC, continuous mode, one-shot pending state, 4:2:0 component selection, CRC source selection, pixel-format selection, and a 16-bit CRC mask.
- `VPHOST_READ_CONTROL` controls host-read rate limiting.

These fields are integration points for validation and debug paths that need deterministic CRC signatures from the VPE pixel pipeline. Incorrect source/format/mask programming can make CRC failures look like image-processing failures.

### VPMPCC Compositor and VPMPC Configuration

The `vpe_vpep_vpmpc_vpmpcc0_dispdec` block defines one multipipe compositor component:

- `VPMPCC_TOP_SEL`, `VPMPCC_BOT_SEL`, and `VPMPCC_VPOPP_ID` select source routing and destination/output-pipe identity.
- `VPMPCC_CONTROL` packs compositor mode, alpha blend mode, premultiplied-alpha mode, active-overlap-only behavior, background bits-per-component, bottom gain mode, global alpha, and global gain.
- `VPMPCC_TOP_GAIN`, `VPMPCC_BOT_GAIN_INSIDE`, and `VPMPCC_BOT_GAIN_OUTSIDE` provide 19-bit gain fields.
- `VPMPCC_BG_R_CR`, `VPMPCC_BG_G_Y`, and `VPMPCC_BG_B_CB` define 12-bit background color components.
- `VPMPCC_MEM_PWR_CTRL` and `VPMPCC_STATUS` expose output-gamma memory power state and compositor idle/busy/disabled state.

The adjacent `vpe_vpep_vpmpc_vpmpc_cfg_dispdec` block is MPC-wide configuration:

- `VPMPC_CLOCK_CONTROL` controls VPECLK gate disable and test clock selection.
- `VPMPC_SOFT_RESET` resets `VPMPCC0`, SFR0, SFT0, and the wider VPMPC block.
- `VPMPC_CRC_CTRL`, `VPMPC_CRC_SEL_CONTROL`, and `VPMPC_CRC_RESULT_*` configure and read MPC CRCs.
- `VPMPC_BYPASS_BG_AR` and `VPMPC_BYPASS_BG_GB` define bypass-background alpha/R/G/B component fields.
- `VPMPC_HOST_READ_CONTROL` mirrors host-read rate control for this block.
- `VPMPC_PENDING_STATUS_MISC` exposes `VPMPCC0_CONFIG_UPDATE_PENDING`.

These fields are central to blending, routing, background fill, CRC validation, and update synchronization in the compositor stage.

### VPMPCC Output Gamma and Gamut Remap

The `vpe_vpep_vpmpc_vpmpcc_ogam0_dispdec` block mirrors the VPCM gamma-correction structure for compositor output gamma:

- `VPMPCC_OGAM_CONTROL` selects OGAM mode, PWL disable, current mode, and bank selection.
- `VPMPCC_OGAM_LUT_INDEX`, `VPMPCC_OGAM_LUT_DATA`, and `VPMPCC_OGAM_LUT_CONTROL` provide indexed LUT programming and read/debug controls.
- `VPMPCC_OGAM_RAMA_START_*`, `END_*`, `OFFSET_*`, and `REGION_*` define per-channel PWL curve configuration and the same paired-region offset/segment layout used by VPCM.
- `VPMPCC_GAMUT_REMAP_COEF_FORMAT` and `VPMPCC_GAMUT_REMAP_MODE` select gamut-remap coefficient format and mode/current mode.
- `VPMPC_GAMUT_REMAP_C11_C12_A` through `C33_C34_A` pack 16-bit matrix coefficients for the alpha/output path.

The repeated region families are a risk area because a single field name typo or mask mismatch can affect only one curve segment or channel while the surrounding blocks still appear functional.

### VPMPCC MCM Shaper, 3D LUT, and 1D LUT

The `vpe_vpep_vpmpc_vpmpcc_mcm0_dispdec` block is the largest color-management section in this chunk. It defines:

- `VPMPCC_MCM_SHAPER_CONTROL`, shaper offsets/scales, shaper LUT index/data/write-enable, and shaper RAMA region descriptors.
- `VPMPCC_MCM_3DLUT_MODE`, `INDEX`, `DATA`, `DATA_30BIT`, `READ_WRITE_CONTROL`, output normalization factor, and per-channel output offsets.
- `VPMPCC_MCM_1DLUT_CONTROL`, indexed 1D LUT access, LUT control, 1D RAMA start/slope/base/end/offset registers, and paired region descriptors from region 0 through 33.
- `VPMPCC_MCM_MEM_PWR_CTRL` and MCM test/debug index/data registers.

The 3D LUT fields are especially format-sensitive: some registers carry 12-bit per-channel values, while `VPMPCC_MCM_3DLUT_DATA_30BIT` packs 10-bit B/G/R fields into one register. Read/write control exposes color-plane write mask, read color select, selected LUT bank, and 30-bit mode. Driver code must select the correct data format before writing or reading LUT entries.

The 1D LUT and shaper RAMA families use the same high-level pattern as VPCM/OGAM: start controls, start slopes/bases, end controls, offsets, and paired region offset/segment registers. That regularity helps generation and review, but it also makes copy/paste or generator-offset errors hard to spot by visual inspection.

### Output CSC, Formatter, Output Pipe, and CRC

The output color-space conversion block, `vpe_vpep_vpmpc_vpmpc_ocsc_dispdec`, defines:

- `VPMPC_OUT0_MUX` for output source selection.
- `VPMPC_OUT0_FLOAT_CONTROL`, `VPMPC_OUT0_DENORM_CONTROL`, and denormal clamp registers for G/Y and B/Cb components.
- `VPMPC_OUT_CSC_COEF_FORMAT` and `VPMPC_OUT0_CSC_MODE`.
- `VPMPC_OUT0_CSC_C11_C12_A` through `C33_C34_A`, packing 16-bit CSC coefficients in pairs.

The VPFMT block defines output formatting behavior:

- `VPFMT_CLAMP_COMPONENT_R/G/B` and `VPFMT_CLAMP_CNTL` provide clamp values and clamp selection.
- `VPFMT_DYNAMIC_EXP_CNTL` controls dynamic expansion mode and enable state.
- `VPFMT_CONTROL` contains pixel encoding, sub-sampling order, memory power mode, interlace, truncation, dithering, and pixel-repetition related fields.
- `VPFMT_BIT_DEPTH_CONTROL` selects truncation/dither depth, mode, spatial/temporal dithering, high-pass, frame counter, and RGB random enable.
- `VPFMT_DITHER_RAND_R/G/B_SEED` define random seeds for dithering.

The VPOPP blocks define output pipe control, pipe CRC control/mask/results, and top-level clock control:

- `VPOPP_PIPE_CONTROL` exposes output clock enable.
- `VPOPP_PIPE_CRC_CONTROL`, `VPOPP_PIPE_CRC_MASK`, and `VPOPP_PIPE_CRC_RESULT*` control and read pipe CRCs.
- `VPOPP_TOP_CLK_CONTROL` controls VPECLK/DISPCLK gate disable and test clock selection.

Together these constants describe the end of the VPE image-processing path: CSC, denormal/clamp, format conversion, dithering, pipe output, and CRC validation.

### VPCDC, Memory Power, Timeouts, and Perfmon

The `vpe_vpep_vpcdc_cdc_dispdec` block provides command/data-capture and front/back-end support fields:

- `VPEP_MGCG_CNTL` controls medium-grain clock gating and memory low-power delay.
- `VPCDC_SOFT_RESET` resets FE0, BE0, and global sync.
- `VPCDC_FE0_SURFACE_CONFIG`, `CROSSBAR_CONFIG`, viewport start/dimension, and chroma viewport start/dimension fields describe FE surface layout and routing.
- `VPCDC_BE0_P2B_CONFIG` and `VPCDC_BE0_GLOBAL_SYNC_CONFIG` define backend pipe-to-buffer and sync behavior.
- `VPCDC_GLOBAL_SYNC_TRIGGER` and `VPCDC_VREADY_STATUS` expose global-sync trigger and VREADY status.
- `VPEP_MEM_GLOBAL_PWR_REQ_CNTL`, `VPFE_MEM_PWR_CNTL`, and `VPBE_MEM_PWR_CNTL` control memory power request/force/mode/state/disable behavior.
- `VPEP_RBBMIF_TIMEOUT`, `VPEP_RBBMIF_STATUS`, and `VPEP_RBBMIF_TIMEOUT_DIS` configure and report register-bus timeout behavior per client.

The final address block, `vpe_vpep_vpcdc_vpcdc_dcperfmon_dc_perfmon_dispdec`, defines generic display perfmon registers:

- `PERFCOUNTER_CNTL` selects events, counted value source, increment mode, hardware control, run-enable mode, counter-off behavior, restart, interrupt enable, active state, and counter selector.
- `PERFCOUNTER_CNTL2` selects counted value type, hardware stop selectors, counter-off selector, and secondary counter selector.
- `PERFCOUNTER_STATE` packs state for eight counters with per-counter state select bits.
- `PERFMON_CNTL` and `PERFMON_CNTL2` control perfmon state, report count, counter-off interrupt behavior, clock enable, and run-enable start/stop selectors.
- `PERFMON_CVALUE_INT_MISC`, `PERFMON_CVALUE_LOW`, `PERFMON_HI`, and `PERFMON_LOW` expose interrupt status/ack bits and counter value readback.

These fields are not VPE command submission logic, but they are important for diagnostics, performance analysis, and hang triage.

## Control Flow and State

There is no C control flow in this chunk. The effective runtime flow is indirect:

1. Code or firmware chooses a register offset from `vpe_6_1_0_offset.h`.
2. It uses this header's `__SHIFT` and `_MASK` constants through field helpers, or manually with bit operations, to pack or extract a register field.
3. It reads or writes the resulting value through AMDGPU MMIO accessors.
4. The VPE hardware changes image-processing behavior, memory-power state, reset state, routing, CRC output, timeout reporting, or performance-counter state.

The persistent state is hardware state, not C-owned state. Key state surfaces represented by this range include LUT contents and selected banks, PWL region configuration, CSC/gamut matrices, alpha/gain/background settings, CRC enable/results, soft-reset bits, pending-update status, memory power state, surface/viewport/global-sync configuration, timeout status/ack bits, and perfmon counters. Those values persist in registers until hardware reset, power transitions, firmware/driver reinitialization, or a later MMIO write changes them.

The register families also include status and current-mode fields, such as `*_MODE_CURRENT`, `*_SELECT_CURRENT`, `VPMPCC_STATUS`, `VPMPC_CRC_UPDATE_ENABLED`, `VPMPC_CRC_UPDATE_LOCK`, `VPCDC_VREADY_STATUS`, `VPEP_RBBMIF_STATUS`, and perfmon active/state bits. Driver paths should treat those as hardware-observed state rather than ordinary writable configuration unless the corresponding hardware specification says otherwise.

## Dependencies and Integration Points

The direct dependencies are compile-time hardware-contract dependencies:

- `vpe_6_1_0_offset.h` must provide matching `reg*` offsets and base-index macros for every register family whose fields are defined here.
- `vpe_v6_1.c` includes this header together with the offset header and uses the same generated naming convention with AMDGPU MMIO helpers.
- SOC/IP version selection must choose this VPE 6.1.0 layout only for compatible hardware. The file also sits near VPE 6.1.1/6.1.3 firmware paths in `vpe_v6_1.c`; local overrides in that C file show that minor IP versions can move some registers, so these masks must not be blindly reused with incompatible offsets.
- AMDGPU field helpers depend on the exact naming convention `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`.
- Display/color-management code, VPE firmware command processing, debugfs or diagnostic readers, CRC validation paths, reset/power-management paths, and performance-monitoring tools can all depend on these definitions matching the ASIC register specification.

The integration boundary is narrow but strict: this header says where bits live inside a register, while the sibling offset header says where the register lives in MMIO space. A correct mask paired with a wrong offset, or a correct offset paired with a wrong mask, is still a hardware programming bug.

## Risks

- A wrong shift or mask compiles cleanly but can program the wrong hardware field at runtime. The failure may appear as bad color output, incorrect blending, broken CRCs, stuck update-pending state, timeouts, or performance-counter misreads.
- Many fields pack two or three channel values into one register. Channel ordering errors, especially between RGB and YCbCr-style names (`R_CR`, `G_Y`, `B_CB`), can produce subtle color defects.
- LUT and RAMA programming is highly repetitive. Generator or copy errors in one region, channel, or LUT family can affect only a narrow range of a transfer curve and be hard to diagnose visually.
- The MCM 3D LUT has both normal and 30-bit data paths. Using 12-bit-style fields when the hardware expects 10-bit packed `DATA_30BIT`, or the reverse, can corrupt LUT programming without obvious MMIO errors.
- Reset and clock-gating fields are mixed into the same generated header as color fields. Incorrect use during active processing can hang a pipeline or leave sub-blocks disabled.
- Memory-power controls expose force, disable, low-power mode, and state bits. Treating status bits as configuration, or powering down memory while LUTs are in use, risks underflow, stale data, or hangs.
- CRC and perfmon fields are validation tools as well as hardware controls. Misprogramming masks, source selectors, or run-enable controls can invalidate test results.
- The chunk starts mid-VPCM gamut-remap family, so this chunk alone is incomplete for full VPCM matrix analysis.
- The final line is the file's include-guard terminator. Any later merged report must account for all earlier chunks because this chunk does not include the license/header guard start or the VPEC ring/firmware fields.

## Test Signals

Useful validation signals for this generated header are a mix of build, static, and hardware tests:

- Kernel build coverage for `drivers/gpu/drm/amd/amdgpu/vpe_v6_1.c` with `vpe_6_1_0_offset.h` and `vpe_6_1_0_sh_mask.h` included.
- Static generated-header checks that every field in this range has a coherent `__SHIFT`/`_MASK` pair and that masks are contained within 32 bits.
- Cross-header checks that every `regVPCM_*`, `regVPDPP_*`, `regVPMPCC_*`, `regVPMPC_*`, `regVPFMT_*`, `regVPOPP_*`, `regVPCDC_*`, `regVPEP_*`, and perfmon register in the offset header has matching field definitions where expected.
- Hardware smoke tests on compatible VPE 6.1 hardware: VPE probe, firmware load, ring start, command submission, suspend/resume, and GPU reset should not regress after header changes.
- Color-management validation that programs VPCM/OGAM/MCM LUTs and matrices and compares known output or CRC values.
- CRC tests that enable VPDPP, VPMPC, and VPOPP CRC paths with known frames and verify stable channel results and mask behavior.
- Formatter tests for clamp, bit depth, truncation, dithering, random seeds, dynamic expansion, and CSC output on RGB and YCbCr-like formats.
- Power-management tests that toggle clock gating, soft resets, memory power states, and low-power modes while checking for idle/busy/status convergence.
- Timeout and recovery tests that verify `VPEP_RBBMIF_STATUS` timeout status/ack/mask behavior and per-client disable bits.
- Perfmon tests that select events, start/stop counters, read high/low values, acknowledge interrupts, and confirm active/state bits behave as expected.

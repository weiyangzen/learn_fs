# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 27384-29960

## Scope And Purpose

This chunk is generated AMD DCN 2.0 register field metadata. It contains no executable C logic; its purpose is to publish preprocessor constants for register bit shifts and masks in the DCN 2.0 display engine. The constants are consumed with the matching register-offset header so AMDGPU Display Core code can pack, update, and decode MMIO register fields through `REG_SET`, `REG_UPDATE`, `REG_GET`, `SF`, `SRI`, `SRII`, and related table-building macros.

The path is under a local `ceph-client` source mirror, but the content is Linux AMDGPU display-driver hardware metadata. It does not implement Ceph filesystem behavior.

The requested range covers:

- The tail of `MPCC_OGAM6` RAM B region descriptors, specifically output-gamma RAMB regions 18 through 33.
- Full `MPCC_OGAM7` output-gamma field definitions: mode, LUT index/data/RAM control, RAM A and RAM B per-channel start/slope/end controls, and paired region descriptors 0 through 33.
- `dce_dc_mpc_mpc_ocsc_dispdec`: MPC output color-space-conversion coefficient format, output CSC mode, two coefficient banks for MPC outputs 0 through 5, and OCSC debug index/data fields.
- `dce_dc_mpc_mpc_dcperfmon_dc_perfmon_dispdec`: `DC_PERFMON17` performance counter control, state, value, interrupt, watermark, and status fields.
- `dce_dc_opp_abm0_dispdec`: backlight/PWM and ABM1 adaptive backlight management fields, including histogram/gain/low-scale controls and readback results.
- OPP output pipeline instances 0 through 4: formatter (`FMT`), display pattern generator (`DPG`), output buffer (`OPPBUF`), OPP pipe control, and OPP pipe CRC fields.
- The beginning of OPP formatter instance 5, covering only `FMT5_FMT_CLAMP_COMPONENT_R` and `FMT5_FMT_CLAMP_COMPONENT_G` within this chunk.

The chunk boundary is not semantic. It starts after earlier `MPCC_OGAM6` definitions and ends before the rest of `FMT5`, so complete per-block interpretation requires adjacent chunks.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, or persistence objects in this range. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` defines the bit position for a field.
- `<REGISTER>__<FIELD>_MASK` defines the 32-bit mask for that field.
- Register names are prefixed by hardware instance where applicable, for example `MPCC_OGAM7_`, `MPC_OUT3_`, `FMT4_`, `DPG2_`, `OPPBUF1_`, and `OPP_PIPE_CRC0_`.

Important macro families:

- `MPCC_OGAM6_MPCC_OGAM_RAMB_REGION_18_19` through `MPCC_OGAM6_MPCC_OGAM_RAMB_REGION_32_33` describe paired RAM B piecewise-linear output-gamma region descriptors. Each register packs an even and odd region with `LUT_OFFSET` at bits 0 and 16 and `NUM_SEGMENTS` at bits 12 and 28.
- `MPCC_OGAM7_MPCC_OGAM_MODE`, `MPCC_OGAM7_MPCC_OGAM_LUT_INDEX`, `MPCC_OGAM7_MPCC_OGAM_LUT_DATA`, and `MPCC_OGAM7_MPCC_OGAM_LUT_RAM_CONTROL` define the MPCC 7 output-gamma operating mode, 9-bit LUT index, 19-bit LUT data, write-enable color mask, RAM select, and configuration status fields.
- `MPCC_OGAM7_MPCC_OGAM_RAMA_*` and `MPCC_OGAM7_MPCC_OGAM_RAMB_*` define the two output-gamma RAM banks. They include per-channel blue/green/red start control, linear slope, end control, end slope/base, and 34 region descriptors per RAM. Start fields use 18-bit starts plus 7-bit start-segment values; end controls pack 16-bit end, slope, and base values; region descriptors use the repeated 9-bit offset plus 3-bit segment-count shape.
- `MPC_OUT_CSC_COEF_FORMAT` exposes `MPC_OCSC_COEF_FORMAT`; `MPC_OUT[0-5]_CSC_MODE` exposes `MPC_OCSC_MODE`; and `MPC_OUT[0-5]_CSC_Cxx_Cyy_[AB]` registers pack signed or fixed-point output CSC coefficients into low/high 16-bit fields for A and B coefficient banks.
- `MPC_OCSC_TEST_DEBUG_INDEX` and `MPC_OCSC_TEST_DEBUG_DATA` provide indexed debug access fields for the MPC output CSC block.
- `DC_PERFMON17_*` defines display performance monitor controls: enable, clear, select, trigger mode, interrupt generation/clear/status, counter mode, state, current value, high/low latched values, and watermark fields.
- `BL1_PWM_*` defines ambient/user/target/current/final/minimum backlight/PWM levels, ABM/PWM enable and clock controls, update sample rate, and grouped register lock/master-update controls.
- `DC_ABM1_*` defines ABM image processing and histogram collection fields: IPCSC coefficient select, ACE offset/slope tables, ACE thresholds, control flags, histogram/low-scale read-progress gating, min/max luma/pixel counters, sample rates, histogram-bin shift flags/indexes, 32 histogram result registers, and the backlight master lock.
- `FMT[0-4]_*` and the partial `FMT5_*` fields define formatter clamp lower/upper values, dynamic expansion, pixel encoding, subsampling, bit-depth truncation, spatial and temporal dithering controls, random seeds and offsets, clamp color format, side-by-side stereo width, 4:2:0 memory low-power controls, and 4:2:2 edge handling.
- `DPG[0-4]_*` defines display pattern generator enable, mode, dynamic range, bit depth, active resolution, field polarity, ramp increments, color values, offset/segment dimensions, and double-buffer-pending status.
- `OPPBUF[0-4]_*` defines output-buffer active width, display segmentation, overlap pixels, pixel repetition, double-buffer pending, 3D dummy data and VACT spacing, and padded segment pixel count.
- `OPP_PIPE[0-4]_OPP_PIPE_CONTROL` defines output pipe clock enable/on and digital bypass fields.
- `OPP_PIPE_CRC[0-4]_*` defines output-pipe CRC enable, continuous mode, stereo/interlace modes, pixel and source selection, one-shot pending status, CRC mask, and A/R/G/B/C result fields.

## Control Flow

This header chunk has no runtime control flow. Data flow is compile-time macro substitution:

1. DCN 2.0 resource and block headers include the generated offset and mask headers.
2. Register-list macros map hardware register offsets to per-block register structs.
3. Shift/mask macros are collected into per-block field structs through `SF`, `OPP_SF`, `ABM_SF`, and similar macros.
4. Runtime code calls register helpers, which use these constants to read-modify-write MMIO fields or decode status values.

Representative consumer flows in this tree:

- MPC color and gamma code uses MPCC OGAM and MPC OCSC masks through MPC register tables. Output gamma programming selects the MPCC OGAM mode/RAM bank, writes LUT index/data, and programs PWL region descriptors; output CSC programming selects an MPC output CSC mode and writes coefficient pairs into A or B coefficient banks.
- ABM/backlight code in `display/dc/dce/dce_abm.c` and `display/dc/dce/dmub_abm_lcd.c` writes `DC_ABM1_HG_SAMPLE_RATE`, `DC_ABM1_LS_SAMPLE_RATE`, `BL1_PWM_BL_UPDATE_SAMPLE_RATE`, `DC_ABM1_HG_MISC_CTRL`, `DC_ABM1_IPCSC_COEFF_SEL`, `BL1_PWM_CURRENT_ABM_LEVEL`, `BL1_PWM_TARGET_ABM_LEVEL`, and `BL1_PWM_USER_LEVEL`, using the matching masks for field packing.
- OPP formatter code in `display/dc/dce/dce_opp.c` programs `FMT_BIT_DEPTH_CONTROL` fields for truncation, spatial dithering, temporal dithering, randomization, and FRC selection.
- DCN20 OPP code in `display/dc/opp/dcn20/dcn20_opp.c` uses `DPG_CONTROL` and related fields to configure and disable display test patterns, reads DPG status, and captures OPP register state.
- OPP buffer and pipe code in `display/dc/opp/dcn10/dcn10_opp.c` writes `OPPBUF_CONTROL` active width and `OPP_PIPE_CONTROL` clock enable, then reads OPP pipe, CRC, and buffer registers for debug snapshots.
- Debug and validation paths read `OPP_PIPE_CRC_CONTROL`, `OPP_PIPE_CRC_RESULT*`, `DC_PERFMON17_*`, ABM histogram/results, and OPP register snapshots to validate displayed output or hardware state.

The header does not encode sequencing constraints. Consumers must still honor hardware-specific requirements such as LUT RAM selection before LUT writes, double-buffer update timing, ABM lock/update behavior, backlight/PWM enable ordering, OPP clock availability, CRC one-shot/continuous capture state, and perfmon clear/enable ordering.

## State And Persistence Behavior

The header itself stores no state and has no persistence behavior. It describes hardware MMIO fields that live in DCN 2.0 display registers.

State represented by this chunk includes:

- MPCC output-gamma state: selected mode, LUT index/data, active RAM bank, RAM configuration status, per-channel PWL start/end/slope settings, and 34 region descriptors for MPCC 7 plus the end of MPCC 6 RAM B.
- MPC output CSC state: coefficient format, per-output CSC mode, and A/B coefficient banks for six MPC outputs.
- MPC perfmon state: counter enable/clear/select, trigger and interrupt state, current value, high/low latched values, and watermark thresholds.
- Backlight and ABM state: PWM/user/target/current/final duty levels, ABM enable and clock settings, register locks, histogram/gain controls, sample rates, luma statistics, histogram bins, and master lock state.
- OPP formatter state: clamp limits, dynamic expansion, pixel/subsampling controls, bit-depth truncation, dithering seeds and modes, stereo width, 4:2:0 memory power state, and 4:2:2 edge handling.
- DPG state: generated-pattern enable/mode, resolution, dynamic range, colors, ramp settings, offset/segment configuration, and pending double-buffer updates.
- OPPBUF/OPP pipe state: active output width, segmentation, overlap, repetition, 3D dummy/spacer values, clock enable/on state, digital bypass, and pending update bits.
- OPP pipe CRC state: CRC capture enable, modes, selected source/pixels, pending one-shot capture, result mask, and channel result registers.

Persistence is hardware-defined. Many fields are programmed state that remains until modeset, suspend/resume, power-gating transition, reset, or explicit rewrite. Other fields are read-only status, sticky interrupt status, clear-on-write controls, pending bits, or latched readback values. The macro names expose likely semantics (`*_STATUS`, `*_PENDING`, `*_CLEAR`, `*_INT_STATUS`, `*_LOCK`, `*_STATE`, `*_RESULT`), but access type, reset value, and side effects are not described in this header.

## Dependencies And Integration Points

This chunk depends on the generated AMD DCN 2.0 register contract:

- `dcn_2_0_0_offset.h` supplies the corresponding MMIO register offsets and base indices.
- This `dcn_2_0_0_sh_mask.h` chunk supplies shifts and masks for fields in those registers.
- AMD Display Core block headers collect these constants into register/field tables for MPC, OPP, ABM, and resource construction.

Notable local integration points found in the tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn30/dcn30_mpc.h`, which demonstrates the MPCC OGAM and MPC output CSC field-table pattern also used by generated DCN-family resource tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_abm.h`, `dce_abm.c`, and `dmub_abm_lcd.c`, which map and use the ABM/PWM fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_opp.h` and `dce_opp.c`, which map and use formatter bit-depth, dither, and clamp fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn10/dcn10_opp.h` and `dcn10_opp.c`, which map OPPBUF, OPP pipe, and OPP pipe CRC fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn20/dcn20_opp.h` and `dcn20_opp.c`, which map and program DPG fields for test-pattern output.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc.h`, which includes debug/state capture members corresponding to MPCC OGAM, MPC output CSC, DPG, OPP pipe, OPP CRC, and OPPBUF state.

Practical integration surfaces are DRM/KMS modesets, color-management programming, HDR/SDR output transforms, output gamma LUT programming, display test patterns, panel backlight and adaptive backlight management, output bit-depth/dithering, multi-stream or segmented output buffering, pipe clock control, CRC-based validation, perfmon sampling, and display debug state collection.

## Risks And Edge Cases

- These constants are a hardware ABI. A wrong shift or mask can compile cleanly while silently writing the wrong bits, producing color corruption, broken backlight behavior, invalid test patterns, CRC mismatches, or display hangs.
- The chunk starts and ends inside larger generated families. `MPCC_OGAM6` RAM B is partial at the start, and `FMT5` is partial at the end; a final file-level report must merge adjacent chunks before claiming full block coverage.
- MPCC OGAM region definitions are repetitive and instance-indexed. Off-by-one region, RAMA/RAMB, or channel naming drift can affect only a narrow segment of a gamma curve and appear as banding or inaccurate color rather than an obvious failure.
- MPC output CSC coefficients are packed in 16-bit halves and duplicated across outputs 0 through 5 and banks A/B. Mask drift can swap coefficients, truncate sign/fraction bits, or update the wrong bank.
- ABM/PWM fields affect panel brightness. Incorrect masks for duty cycle, update sample rate, register locks, or current/target levels can cause visible flicker, stuck brightness, unsafe brightness jumps, or failed adaptive backlight updates.
- Histogram and luma statistic fields may be status/readback or gated by read-progress controls. Treating readback fields as ordinary writable state can clear or corrupt diagnostic data.
- Formatter bit-depth and dithering fields are highly visible. Incorrect truncation depth, temporal/spatial dither enable, random seed, or FRC selection can cause banding, noise, flicker, or unstable CRC output.
- `FMT_MAP420_MEMORY_CONTROL` contains memory power control/state fields. Wrong force/disable/state masks can interact with low-power transitions or 4:2:0 output programming.
- DPG, OPPBUF, and OPP pipe controls are double-buffered or clock-sensitive in places. Updating widths, segmentation, pattern dimensions, or clocks at the wrong time can create transient corruption or pending bits that never clear.
- CRC control has mode, interlace/stereo, source, pixel-select, and one-shot-pending fields. Misprogramming can make CRC validation meaningless even when output looks correct.
- Perfmon control includes interrupt and clear bits. Incorrect clear/status masks can drop performance events or leave interrupts asserted.

## Test Signals

Useful validation signals combine build-time coverage with DCN20 hardware behavior:

- Build AMDGPU/DC with DCN 2.0 support enabled. Missing or renamed macros should fail in MPC, OPP, ABM, resource, and debug-state register table paths.
- Diff this generated mask chunk against the matching `dcn_2_0_0_offset.h` families and adjacent DCN mask headers to catch unintended instance, field-width, or bank drift.
- Exercise output color programming on DCN20 hardware: gamma LUT updates through MPCC OGAM, output CSC matrix changes, SDR/HDR-like transforms, and visible color correctness across multiple pipes.
- Validate panel backlight and ABM behavior: brightness changes, ABM enable/disable, suspend/resume brightness restore, histogram readbacks, sample-rate changes, and absence of flicker or stuck duty-cycle state.
- Exercise formatter modes: truncation, spatial and temporal dithering, 6/8/10-bit style output depths, 4:2:0 and 4:2:2 output paths, stereo width where applicable, and clamp behavior.
- Exercise DPG test patterns for OPP instances 0 through 4, including enable/disable, ramp, color, dimensions, and double-buffer-pending status.
- Validate OPPBUF and OPP pipe state under normal and segmented output: active width, overlap, pixel repetition, MSO-style segmentation, pipe clock enable/on status, and digital bypass state.
- Validate OPP pipe CRC capture in one-shot and continuous modes, including interlace/stereo settings, selected source, pixel selection, result masks, and expected CRC stability.
- Sample `DC_PERFMON17` counters around known display workloads and confirm clear/enable/status/interrupt behavior.
- Watch kernel logs and display output for black screens, color shifts, banding, flicker, missed vblank/page-flip completion, underflow messages, EDID-independent modeset failures, CRC mismatches, perfmon interrupt noise, ABM failures, or resume regressions.

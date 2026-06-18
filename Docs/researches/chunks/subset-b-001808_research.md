# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 14928-17438

## Purpose

This chunk is generated AMD DCN 3.1.2 register field metadata. It contains no executable C logic; it publishes C preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for display-pipe registers. Runtime code combines these constants with matching register offsets from `dcn_3_1_2_offset.h` through helper macros such as `FD_SHIFT`, `FD_MASK`, `REG_SET`, `REG_UPDATE`, `REG_GET`, and `REG_WAIT`.

The requested range is a large mid-file slice of `dcn_3_1_2_sh_mask.h`. It starts inside the `CM0_CM_BLNDGAM_RAMA_REGION_18_19` definition set, covers the rest of CM0 blend-gamma RAM A/B and CM0 shaper/3D LUT/test-debug fields, then moves through DPP0 top-level CRC/control fields, DC perfmon instance 11, DPP1 conversion/cursor/scaler fields, and most of DPP1 color-management fields through `CM1_CM_MEM_PWR_STATUS`. The final requested line is only the `//CM1_CM_DEALPHA` comment; the actual `CM1_CM_DEALPHA` field definitions begin in the following chunk.

Although this tree path is under a local `ceph-client` source mirror, this file is AMDGPU display-driver hardware metadata, not Ceph or distributed-filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, or locks in this range. Its interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the bit offset of a field inside a 32-bit MMIO register value.
- `<REGISTER>__<FIELD>_MASK`: the field mask, already shifted into register position.

This chunk contains 2,113 `#define` lines: 1,056 shift macros and 1,057 mask macros. The one-count difference is from the artificial line boundary: line 14928 includes only the `NUM_SEGMENTS__SHIFT` for `CM0_CM_BLNDGAM_RAMA_REGION_18_19`, while the corresponding first field shift at line 14927 is outside this chunk.

Major register families covered:

- `CM0_CM_BLNDGAM_*`: tail of CM0 blend-gamma RAM A region descriptors, complete RAM B start/end/base/slope/offset/region descriptors, LUT index/data/control, HDR multiplier, memory power control/status, dealpha, coefficient format, and test debug fields.
- `CM0_CM_SHAPER_*`: shaper control, per-channel offsets/scales, LUT index/data/write-enable, RAM A/B start/end and 34-region segment descriptors, and second memory-power control/status.
- `CM0_CM_3DLUT_*`: 3D LUT mode, index, data, 30-bit data path, read/write control, output normalization, and per-channel output offsets.
- `DPP_TOP0_*`: DPP0 control, soft reset, CRC readback/control, CRC component selection, shadow/readback controls, and host read control.
- `DC_PERFMON11_*`: perfcounter control/state, perfmon control, current-value capture, high/low counter values, windowing, event select, clear, enable, and mode fields.
- `CNVC_CFG1_*`: DPP1 surface pixel format, format control, fixed-point conversion bias/scale, color keyer, alpha 2-bit LUT, pre-dealpha, pre-CSC mode/matrix coefficients, coefficient format, pre-degamma, and pre-realpha.
- `CNVC_CUR1_*`: DPP1 cursor0 enable/mode/2x magnification/pitch/format/position fields, cursor colors, and FP scale/bias.
- `DSCL1_*`: DPP1 scaler coefficient RAM tap select/data, scaler mode, tap control, DSCL control and 2-tap parameters, manual replicate, horizontal/vertical/chroma scale ratios and filter initial phases, overscan, output timing blanking, recout/MPC size, line-buffer format and memory controls, DSCL memory power, output-buffer control and memory power.
- `CM1_CM_*`: DPP1 color-management control, post-CSC and gamut-remap matrices, bias formats/values, gamma-correction RAM A/B descriptors, blend-gamma RAM A/B descriptors, LUT access fields, HDR multiplier, and memory power control/status.

## Control Flow

The header itself has no runtime control flow. The effective runtime path is generated macro expansion:

1. DCN 3.1 resource, IRQ, and DMUB code include `dcn_3_1_2_offset.h` and this mask header.
2. Register-list macros build per-block register tables from offset macros, while mask/shift-list macros build companion field tables from this file.
3. DPP, HW sequencer, DMUB, and IRQ code call register helpers such as `REG_SET_*`, `REG_UPDATE_*`, `REG_GET_*`, and `REG_WAIT`; those helpers use this chunk's masks and shifts to isolate or update individual fields without hand-coded bit arithmetic.
4. Hardware sequencing is implemented by consumers, not by this header. Consumers decide when to power up DSCL/CM memories, load LUTs, program scalers and color matrices, read CRC/perf counters, or clear/reset blocks.

The fields in this chunk participate in modeset and plane programming flows: DPP format conversion and cursor setup occur before scanout, scaler ratios/taps and line-buffer state are programmed during plane scaling setup, color-management LUTs and matrices are programmed during color pipeline updates, and CRC/perfmon fields are used by diagnostics or debug paths.

## State And Persistence Behavior

This file stores no software state and persists nothing. It describes MMIO-backed hardware state in DCN display blocks:

- Color-management state: gamma/blend-gamma/shaper/3D LUT banks, region descriptors, per-channel start/end/base/slope values, matrix coefficients, bias values, dealpha/re-alpha controls, HDR multiplier, and coefficient formats.
- Scaler and line-buffer state: DSCL mode, tap counts, 2-tap parameters, filter coefficients, initial phases, scale ratios, recout/MPC dimensions, line-buffer format, memory partitioning, and output-buffer controls.
- Conversion/cursor state: source format, pre-CSC and fixed-point conversion controls, color key values, alpha LUT entries, cursor dimensions/format/position/colors, and FP scale/bias.
- Diagnostic state: DPP CRC selection/readback, soft-reset/control fields, DC perfmon event selection, counter control, high/low counter snapshots, current-value captures, and debug index/data registers.
- Power state: CM, shaper, DSCL LUT, line-buffer, and output-buffer memory power force/disable/status fields.

Persistence is hardware-defined. Programming registers generally retain values until a modeset, pipe reprogramming, power gating, suspend/resume, or ASIC reset. LUT index/data registers are stateful access ports rather than ordinary memory arrays: write ordering, bank selection, write-enable masks, and index resets matter. Status, CRC, perfmon, reset, and memory-power fields may be read-only, sticky, self-clearing, or sequencing-sensitive; this generated header only encodes bit positions, not access semantics.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.1.2 register database and must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_offset.h` for the corresponding register offsets and base-index values.
- AMD DC register helper macros in `reg_helper.h`, `dmub_reg.h`, and DPP/HWSS resource headers that paste register and field tokens into `FD_MASK`, `FD_SHIFT`, `SR`, `SRI`, and related expansions.

Direct include sites for this exact generated header in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn31/irq_service_dcn31.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn31.c`

Important consumer areas include:

- DPP transform/scaler/color-management code, especially shared DCN DPP paths that use register tables for `CNVC_CFG`, `CNVC_CUR`, `DSCL`, `DPP_TOP`, and `CM` blocks.
- DCN31 resource construction, where `BASE(reg..._BASE_IDX) + reg...` builds register addresses and mask/shift lists populate typed field tables.
- HW sequencer diagnostic paths that use `DPP_TOP0_DPP_CRC_*` fields for DPP CRC configuration and readback.
- DMUB DCN31 support, which includes this header so firmware-service register structures can use generated masks and shifts consistently with host driver code.

## Risks And Edge Cases

- Generated-field drift is the central risk. A wrong shift or mask compiles cleanly but updates the wrong bits in a live MMIO register.
- Shift/mask pairs must stay consistent. For example, a correct `REG_UPDATE` depends on the mask covering exactly the field width at the shift position; a mismatch can corrupt adjacent fields in color, scaler, cursor, power, or perfmon registers.
- Repeated RAM-region definitions are copy-sensitive. Gamma, blend-gamma, and shaper RAM A/B region macros repeat the same offset/segment pattern across regions 0 through 33 and across CM0/CM1; a single generated typo may only appear with particular color-transfer curves or LUT bank choices.
- LUT programming uses index/data side effects. Incorrect masks for LUT index, write enable, RAM select, or read/write control can silently load the wrong bank, channel, or entry.
- Memory-power fields are sequencing-sensitive. Bad masks for DSCL/CM/shaper memory force, disable, or state fields can cause writes to be ignored, power transitions to hang, or low-power optimizations to corrupt display state.
- DPP1 and DPP0 are both represented in this chunk. The DPP0 material is mostly top-level control/CRC/perfmon, while DPP1 includes CNVC/DSCL/CM pipeline programming; instance-token mistakes may only fail on multi-pipe or secondary-plane configurations.
- Chunk boundaries are artificial. The first field set starts mid-register, and the last `CM1_CM_DEALPHA` comment has no field definitions in this work item. Adjacent chunks are required before making complete file-level claims.

## Test Signals

Useful validation is mostly generated-header consistency plus display hardware behavior:

- Build AMDGPU/DC with DCN31 support enabled; missing or renamed shift/mask macros should fail in resource, IRQ, DMUB, DPP, or HWSS register-table construction.
- Mechanically verify that every full register field in the chunk has both a `__SHIFT` and `_MASK` macro, allowing for the known boundary exceptions at lines 14928 and 17438.
- Diff this range against AMD's authoritative DCN 3.1.2 register database and the companion `dcn_3_1_2_offset.h`.
- Exercise DPP color paths: degamma/gamma/blend-gamma/shaper/3D LUT loading, HDR multiplier, gamut remap, post-CSC, bias, pre-CSC, dealpha/re-alpha, and color-key behavior.
- Exercise scaler paths on DPP1: RGB and YCbCr formats, 4:2:0 luma/chroma scaling, identity scaling, non-integer scaling, tap-count changes, coefficient RAM programming, overscan, recout sizing, and line-buffer partitioning.
- Validate cursor paths on DPP1: cursor enable/disable, color modes, position, 2x magnification, pitch, size, and FP scale/bias.
- Validate diagnostics: DPP CRC capture/readback, perfmon counter enable/clear/window/event select, and debug index/data paths.
- Test suspend/resume, display hotplug, modeset, plane enable/disable, and memory low-power transitions while watching for blank screens, underflow, color corruption, cursor artifacts, CRC mismatches, perfmon counter anomalies, stuck power-state waits, and kernel register-helper warnings.

## Cross-Chunk Notes

Earlier chunks own the beginning of `CM0_CM_BLNDGAM_RAMA_REGION_18_19`, including the first LUT-offset shift at line 14927. Later chunks own the actual `CM1_CM_DEALPHA` definitions and continue the remaining CM1 color-management/shaper/3D-LUT namespace. The final per-file research document should merge adjacent chunks before making complete claims about all DCN 3.1.2 DPP instances, all CM blocks, or the complete generated mask namespace.

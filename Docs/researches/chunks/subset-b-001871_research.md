# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 15090-17598

## Scope

This chunk covers lines 15090-17598 of the generated AMD DCN 3.1.5 shift/mask header. It is preprocessor register metadata only: 2,113 `#define` entries across 2,509 source lines, with 1,056 `__SHIFT` constants, 1,065 `_MASK` constants, and generated register/address-block comments. There are no functions, structs, enums, variables, includes, allocations, locks, or executable statements in this range.

The range starts in the middle of the DPP1 color-management blend-gamma RAMA region table, continues through DPP1 blend-gamma RAMB, DPP1 shaper, DPP1 3DLUT, DPP1 DPP top, DPP1 performance monitor, DPP2 CNVC converter/cursor, DPP2 DSCL scaler, and DPP2 color-management blocks, then ends in the DPP2 blend-gamma RAMB region table. The first and last logical register groups are split across neighboring chunks.

## Purpose

The purpose of this header slice is to publish exact bit positions and masks for DCN 3.1.5 display-pipe hardware registers. AMDGPU display code combines these macros with the matching DCN 3.1.5 offset header and register helper macros to pack MMIO writes, read status fields, and instantiate per-ASIC DPP register tables without hard-coding raw bit positions in driver logic.

This file is a generated hardware contract. Runtime behavior lives in consumers such as the DCN 3.x DPP, color-management, scaler, converter, cursor, performance-monitor, resource-pool, IRQ, and DMUB code. This chunk only describes field layout.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The exported interface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of a field.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit field mask.
- `//<REGISTER>` comments group fields under a logical register.
- `// addressBlock: ...` comments identify the decoded display hardware block.

Major constant families in this chunk include:

- `CM1_CM_BLNDGAM_RAMA_REGION_8_9` through `CM1_CM_BLNDGAM_RAMA_REGION_32_33`, plus the split tail of `CM1_CM_BLNDGAM_RAMA_REGION_6_7`, covering DPP1 blend-gamma RAM A region LUT offsets and segment counts.
- `CM1_CM_BLNDGAM_RAMB_*`, covering DPP1 blend-gamma RAM B per-channel start, start segment, start slope, start base, end base, end value, end slope, offset, and region descriptors from regions 0-33.
- `CM1_CM_HDR_MULT_COEF`, `CM1_CM_MEM_PWR_CTRL`, `CM1_CM_MEM_PWR_STATUS`, `CM1_CM_DEALPHA`, `CM1_CM_COEF_FORMAT`, `CM1_CM_SHAPER_*`, `CM1_CM_MEM_PWR_CTRL2`, `CM1_CM_MEM_PWR_STATUS2`, `CM1_CM_3DLUT_*`, and `CM1_CM_TEST_DEBUG_*`, covering DPP1 color-management scalar controls, memory power, dealpha, shaper LUT setup, HDR 3D LUT mode/index/data, output normalization/offset, and test debug access.
- `DPP_TOP1_DPP_*` and `DPP_TOP1_HOST_READ_CONTROL`, covering DPP1 clock enable, global alpha, input/output color keyer controls, CRC control/results, soft reset, and host-read controls.
- `DC_PERFMON12_*`, covering DPP1/display performance counter event selection, counter control/state, perfmon control, interrupt/status, and high/low counter values.
- `CNVC_CFG2_*` and `CNVC_CUR2_*`, covering DPP2 converter surface format, format control, floating-point bias/scale, color keyer thresholds, alpha 2-bit LUT, pre-dealpha, pre-CSC matrix fields, pre-degamma, pre-realpha, and cursor control/colors/FP scale-bias.
- `DSCL2_*`, covering DPP2 scaler coefficient RAM, scaler mode/taps/ratios/initial phases, DSCL update/autocal, overscan, OTG blanking, recout/MPC sizing, line-buffer format/memory partitioning, line-buffer counters, DSCL/OBUF memory power, and OBUF controls.
- `CM2_CM_*`, covering DPP2 color-management bypass, post-CSC, gamut remap, bias, gamma correction RAMA/RAMB, blend-gamma control/LUT/RAMA/RAMB, and the beginning of blend-gamma RAMB region descriptors.

Many register families are structurally repeated across pipe instances. In this range, the suffixes `CM1`, `CNVC_CFG2`, `DSCL2`, `DPP_TOP1`, and `CM2` distinguish DPP/display-pipe instances while preserving field names consumed by common DPP helper macros.

## Control Flow

This chunk has no runtime control flow. Its effective flow is compile-time token expansion:

1. DCN 3.1.5 resource code includes the DCN 3.1.5 offset and shift/mask headers.
2. Resource tables such as `dcn315_resource.c` expand DPP register-list macros into `dpp_regs`, `tf_shift`, and `tf_mask` tables using `DPP_REG_LIST_DCN30(...)` and `DPP_REG_LIST_SH_MASK_DCN30(...)`.
3. DPP constructors such as `dpp3_construct()` store pointers to those tables in `struct dcn3_dpp`.
4. Runtime DPP code uses helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG`, and transfer-function helpers to concatenate register/field names and resolve the `__SHIFT`/`_MASK` constants from this header.
5. The resolved values drive MMIO register reads, writes, read-modify-write updates, indexed LUT writes, and status decoding.

The declaration order mirrors hardware organization rather than software call order: DPP1 color management, DPP1 top/perf blocks, then DPP2 converter/scaler/color-management blocks. Repeated per-channel and per-region definitions are intentionally expanded as independent symbols so common code can address a specific instance/register/field combination at compile time.

## State And Persistence Behavior

The header stores no software state and persists no data. It describes bit locations for state held in DCN 3.1.5 display hardware registers.

Writable fields in this chunk can program transfer-function RAM descriptors, shaper curves, blend-gamma curves, 3D LUT mode/index/data, color matrices, color keying, alpha handling, format conversion, cursor format/color controls, scaler coefficients and geometry, DPP top-level clock/reset/CRC controls, performance counter configuration, and memory power controls for color-management, scaler, line-buffer, and OBUF memories.

Hardware-updated fields expose current mode/select state, memory power state, CRC results, soft-reset state, scaler update state, line-buffer counters, performance counter state, performance interrupt/status, and readback/debug data. This header does not encode access type, reset values, read-clear/write-one-to-clear behavior, required polling, or programming sequences.

Programmed values persist according to the relevant display block power and reset domains. They may remain in hardware until a modeset rewrite, plane update, display block reset, DPP power gating, suspend/resume restore, GPU reset, or full ASIC reset. Status fields can change asynchronously relative to the driver code that includes these macros.

## Dependencies And Integration Points

This chunk depends on the matching DCN 3.1.5 offset header for register addresses. The shift/mask header identifies bit placement only; it does not provide MMIO addresses or base indices.

Primary consumers are AMDGPU display register helpers and generated register tables:

- `drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` includes this ASIC register metadata and expands DPP register lists into `dpp_regs`, `tf_shift`, and `tf_mask`.
- `drivers/gpu/drm/amd/display/dc/dpp/dcn30/dcn30_dpp.c` and `dcn30_dpp_cm.c` use the stored shift/mask tables to program post-CSC, gamut remap, gamma correction, blend gamma, shaper, 3D LUT, memory power, converter, cursor, and scaler-related fields.
- `dpp3_construct()` wires the per-instance register table and shared shift/mask table into each `struct dcn3_dpp`.
- `dmub/src/dmub_dcn315.c` also includes `dcn_3_1_5_sh_mask.h` for DCN315 DMUB register definitions, though the DPP/color-management fields in this specific range are mainly consumed by display-pipe code.

Key functional integration areas are:

- Plane color pipeline setup: pre-CSC/pre-degamma/pre-dealpha in `CNVC_CFG2`, post-CSC/gamut remap/bias/gamma/blend/shaper/3DLUT in `CM1` and `CM2`.
- Transfer-function programming: `CM*_CM_GAMCOR_*`, `CM*_CM_BLNDGAM_*`, and `CM1_CM_SHAPER_*` define RAM A/B start, end, slope, base, offset, and region descriptor fields used by common transfer-function helpers.
- LUT access paths: `CM1_CM_SHAPER_LUT_INDEX/DATA/WRITE_EN_MASK`, `CM1_CM_3DLUT_INDEX/DATA/DATA_30BIT/READ_WRITE_CONTROL`, and `CM2_CM_GAMCOR/BLNDGAM_LUT_*` fields are used to sequence indexed RAM writes and reads.
- Scaler and viewport programming: `DSCL2_*` fields back coefficient RAM loading, tap selection, scaling ratios, initial phases, autocal, recout/MPC sizing, blanking, and line-buffer partitioning.
- Cursor and conversion paths: `CNVC_CUR2_*` and `CNVC_CFG2_*` fields configure cursor enable/mode/color, surface format, alpha, keying, FP bias/scale, and channel crossbar/clamping behavior.
- Diagnostics and debug: `DPP_TOP1_DPP_CRC_*`, `DC_PERFMON12_*`, and `CM*_CM_TEST_DEBUG_*` expose CRC, performance-counter, and test/debug control/status.
- Power management: `CM1_CM_MEM_PWR_*`, `CM1_CM_MEM_PWR_CTRL2/STATUS2`, `DSCL2_DSCL_MEM_PWR_*`, and `DSCL2_OBUF_MEM_PWR_CTRL` fields control or observe subblock memory power states.

The generated DCN 3.1.5 offset and shift/mask headers must come from the same ASIC register database. Mixing a DCN315 shift/mask header with DCN314/DCN316/DCN32 offsets or resource tables is especially risky because many field names and layouts are visually similar while instance counts, offsets, or high-bit fields can differ.

## Risks And Edge Cases

- The chunk starts mid-register. Only the final mask for `CM1_CM_BLNDGAM_RAMA_REGION_6_7__CM_BLNDGAM_RAMA_EXP_REGION7_NUM_SEGMENTS_MASK` is present here; the rest of `CM1_CM_BLNDGAM_RAMA_REGION_6_7` is in the previous chunk.
- The chunk ends inside the DPP2 blend-gamma RAMB region table. It includes `CM2_CM_BLNDGAM_RAMB_REGION_24_25` completely and starts `CM2_CM_BLNDGAM_RAMB_REGION_26_27`, `28_29`, and `30_31` in the visible range; the later field definitions continue in the next chunk.
- Repeated region macros are copy-sensitive. The region tables use the same pattern for pairs of regions, with LUT offset fields at shifts `0x0` and `0x10`, segment-count fields at `0xc` and `0x1c`, and masks such as `0x000001FFL`, `0x00007000L`, `0x01FF0000L`, and `0x70000000L`. A generator or hand-edit mistake can compile but misplace gamma curve regions.
- Many control and status fields share nearby registers. Examples include DPP soft reset vs. reset status, memory power force/disable vs. state, current mode/select fields vs. requested mode/select fields, perf-counter interrupt controls vs. status, and DSCL update/autocal fields. The access semantics are not represented by the masks.
- Full-width or high-bit masks such as LUT data, 3D LUT data, performance counter values, CSC coefficients, scale ratios, and packed geometry fields require 32-bit unsigned handling. Signed assumptions around constants ending in `L` can be hazardous in nonstandard helper code.
- Indexed LUT programming is sequence-sensitive. `CM*_LUT_INDEX`, `CM*_LUT_DATA`, LUT write color masks, host-select fields, config-mode fields, and 3D LUT read/write control must be coordinated by higher-level code; these macros do not protect against writing the wrong RAM bank or color component.
- Color-pipeline fields are user-visible. Incorrect masks for CSC, gamut remap, gamma, blend-gamma, shaper, 3D LUT, format conversion, or alpha fields can present as color shifts, banding, clipping, incorrect HDR behavior, cursor artifacts, or alpha blending regressions rather than obvious kernel faults.
- Scaler and line-buffer fields are modeset-critical. Bad DSCL masks for taps, ratios, initial phases, recout size, MPC size, line-buffer partitions, or memory power can cause scaling artifacts, underflow, blank output, or intermittent display failures.
- Performance monitor fields are diagnostic-sensitive. Wrong event-selection, counter-state, or interrupt masks can make perf telemetry misleading while normal display output still appears functional.

## Test Signals

Useful validation is mostly build-time consistency plus hardware integration:

- Build AMDGPU display code with DCN315 support to catch missing or renamed macros used by `DPP_REG_LIST_SH_MASK_DCN30(__SHIFT)` and `DPP_REG_LIST_SH_MASK_DCN30(_MASK)` expansion in `dcn315_resource.c`.
- Mechanically verify that each complete register group in this range has paired `__SHIFT` and `_MASK` entries for every field, accounting for the intentionally partial first and last register groups.
- Compare this slice against the authoritative DCN 3.1.5 register database and the matching offset header to ensure every field has the intended bit position and every logical register maps to the intended address.
- Exercise color-management paths on DCN315 hardware: SDR/HDR transfer functions, degamma, gamma correction, blend gamma, shaper LUT, 3D LUT, post-CSC, gamut remap, bias, dealpha/realpha, and format conversion. Look for banding, channel swaps, clipping, alpha errors, and incorrect current-mode reporting.
- Exercise indexed LUT programming with nontrivial curves and alternating RAM A/RAM B use so region descriptors, start/end/base/slope/offset fields, LUT indices, data registers, write color masks, host-select fields, and config-mode fields all move through real values.
- Exercise DPP2 scaler modes with luma/chroma scaling, different tap counts, coefficient RAM programming, overscan, recout/MPC sizing, line-buffer partition changes, and memory power transitions. Watch for underflow, scaler-update stalls, and corrupted output.
- Exercise cursor formats and color-key/alpha paths through `CNVC_CUR2` and `CNVC_CFG2`, including cursor enable/disable, color0/color1, FP scale/bias, color keyer ranges, alpha plane enable, pre-dealpha, and pre-realpha.
- Exercise diagnostics by reading DPP CRC results, DC_PERFMON12 counter values/states, and CM test-debug registers where available. Verify that control bits and status bits decode as expected.
- Exercise suspend/resume, display hotplug, modeset, plane updates, and power-gating paths to ensure memory-power force/disable/status fields and restored color/scaler state behave consistently after block reset or power transitions.

## Open Cross-Chunk Notes

The merge lane should combine this chunk with the previous chunk to describe `CM1_CM_BLNDGAM_RAMA_REGION_6_7` completely. It should combine this chunk with the next chunk to complete the DPP2 blend-gamma RAMB region table after `CM2_CM_BLNDGAM_RAMB_REGION_24_25`, especially the later `26_27`, `28_29`, `30_31`, and `32_33` definitions. Whole-file analysis should reconcile this chunk with neighboring DCN 3.1.5 generated-header chunks before making final claims about the complete DPP1/DPP2 color, converter, scaler, perfmon, and memory-power register coverage.

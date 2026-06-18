# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h lines 12473-15001

## Scope

This chunk covers lines 12473-15001 of the generated AMD DCN 1.0 register shift/mask header. It contains only preprocessor constants: no C functions, structs, enums, or executable logic. The slice starts inside the `CURSOR3_CURSOR_CONTROL` macro family, after its `*_SHIFT` definitions, and ends inside the `CM1_CM_DGAM_RAMB_START_CNTL_G` family; adjacent chunks are required for both complete boundary register groups.

The chunk has 2529 source lines, including 2123 `#define` lines and 382 comment/address-block lines. Its public surface is the generated register-field macro namespace consumed by DCN 1.0 display code together with `dcn_1_0_offset.h` and register helper macros.

## Purpose

The macros define bit positions and masks for DCN 1.0 display pipe hardware:

- Tail of `CURSOR3`: cursor enable/mode fields from the previous chunk plus surface address, high address, size, position, hotspot, stereo offsets, destination X offset, and cursor memory power control/status.
- `DC_PERFMON11`: HUBP/cursor-side display performance-monitor event selection, counter control, counter state, monitor state, interrupt status/ack fields, and low/high counter readback.
- DPP0 top-level control: DPP clock enables, clock gating disable bits, clock rate control, soft reset controls for CNVC/DSCL/CM blocks, CRC readback/control, and host-read setup.
- DPP0 CNVC configuration and cursor: surface pixel format, format expansion/alpha/bypass, floating-point conversion scale/bias, denormal handling, color-key controls, cursor mode/enable/expansion, cursor colors, and cursor FP scale/bias.
- DPP0 DSCL scaler: coefficient RAM selection/data, scaler mode, tap control, two-tap filtering, manual replication, horizontal/vertical luma/chroma ratios and initial phases, black offset, recout/MPC/OTG geometry, line-buffer format and memory control, autocalibration, memory power controls/status, and output-buffer control.
- DPP0 CM color management: bypass, color adjustment matrices, input CSC, gamut remap, output CSC, bias/scale, degamma and regamma LUT controls, piecewise-linear region definitions, HDR multiplier, range clamp, output rounding/truncation, denorm, memory power, and debug index/data.
- `DC_PERFMON12`: DPP0-local performance-monitor fields matching the perfmon control/readback pattern.
- DPP1 top-level, CNVC, cursor, and DSCL blocks: a second DPP instance with the same kinds of clock/reset/CRC, format, cursor, and scaler fields as DPP0.
- First part of DPP1 CM: color matrices, input CSC, gamut remap, output CSC, bias/scale, degamma LUT mode/index/data/write enable, RAMA region setup, and the beginning of RAMB start controls.

## Important Macro Families

Each generated field normally appears as:

- `REGISTER__FIELD__SHIFT` for the field bit offset.
- `REGISTER__FIELD_MASK` for the already-positioned mask.

When the hardware field itself is named `*_MASK`, the generated output uses names such as `CM0_CM_DGAM_LUT_WRITE_EN_MASK__CM_DGAM_LUT_WRITE_EN_MASK__SHIFT` and `..._MASK_MASK`. These double `MASK` names are intentional generated identifiers, not typographical errors.

The `CURSOR3_*` fields describe a hardware cursor attached to a fourth pipe/plane instance. They cover 48-bit-ish address programming through low and high address registers, dimensions, screen position, hotspot, stereo primary/secondary offsets, destination X offset, and cursor object memory power state.

The `DC_PERFMON11_*` and `DC_PERFMON12_*` blocks expose a common DC performance-monitor interface: event select, counted-value select/type, increment mode, hardware start/stop controls, count-off behavior, restart and interrupt enable, active state, packed per-counter state selectors for counters 0-7, monitor state/report count, clock enable, interrupt status/ack bits, and split low/high counter values. `DC_PERFMON11` belongs to the `dce_dc_dcbubp3_dispdec_hubp_dcperfmon_dc_perfmon_dispdec` address block, while `DC_PERFMON12` belongs to DPP0's perfmon block.

DPP top-level macros (`DPP_TOP0_*`, `DPP_TOP1_*`) are clocking, reset, CRC, and debug/control surfaces. The clock fields include enable and multiple gate-disable/rate-control bits. Soft reset bits independently reset CNVC, DSCL, and CM subblocks. CRC fields provide R/G and B/A values plus mode, window enable, continuous/region selection, and source selection controls.

`CNVC_CFG*` and `CNVC_CUR*` define the conversion path that adapts surface format and cursor pixels into the DPP pipeline. Pixel format, alpha, expansion, bypass, denormal, color key, and FP scale/bias fields are used during format setup. Cursor fields choose cursor mode, expansion, enable, two colors, and FP scale/bias.

`DSCL*` is the densest scaler family. It covers programming coefficient RAM taps and phases, selecting scaler/chroma coefficient modes, enabling two-tap hardcoded/sharp behavior, setting luma and chroma scale ratios and init phases, setting recout/MPC geometry, configuring line-buffer depth/format/dither/interleaving/memory partitioning, requesting autocalculation, and controlling scaler and output-buffer memory power.

`CM0_*` and `CM1_*` are the color-management blocks. They include matrix coefficients for COMA/COMB, input CSC, gamut remap, output CSC, bias/scale values, degamma (`DGAM`) and regamma (`RGAM`) LUT index/data/write-enable controls, RAMA/RAMB start/slope/end/region definitions for PWL LUT segments, HDR multiplier, range clamp, denorm, output format, and memory/debug controls. DPP0's CM block is complete in this chunk; DPP1's CM block is only partially covered and continues in the next chunk.

## APIs, Types, and Functions

There are no callable APIs, data types, or functions in this source range. The API-like contract is the macro namespace itself. AMDGPU display code builds register field tables from these names using macros such as `TF_SF(...)`, `TF2_SF(...)`, and `TF_REG_LIST_SH_MASK_DCN10(...)` in `display/dc/dpp/dcn10/dcn10_dpp.h`.

Observed inclusion points for `dcn_1_0_sh_mask.h` include DCN 1.0 resource construction, IRQ service setup, GPIO factory/translation code, and DPP field-table definitions. The header is paired with `dcn_1_0_offset.h`; offset macros choose the register address, while this file provides the field masks and shifts used by register read/modify/write helpers.

## Control Flow

This header has no runtime control flow. Hardware programming flow is implied by how callers consume the field macros:

1. Select a pipe instance and register family, such as `DPP_TOP0` versus `DPP_TOP1`, `DSCL0` versus `DSCL1`, `CM0` versus `CM1`, or `CURSOR3`.
2. Use the matching offset macro from `dcn_1_0_offset.h` to address the MMIO register.
3. Clear the field with `REGISTER__FIELD_MASK`, shift the value by `REGISTER__FIELD__SHIFT`, and combine it with any other fields that share the register.
4. For status and ack fields, read status bits and write documented acknowledge bits without treating all fields as ordinary read/write data.
5. For LUT and coefficient RAM programming, choose an index or tap/phase register first, then write data registers in the sequence expected by the display pipeline.

The most sequencing-sensitive implied flows are cursor address/size/position enable ordering, perfmon event selection before start/readback, DPP clock/reset transitions around subblock programming, scaler coefficient and geometry setup before enabling a plane, line-buffer memory-power handling, and CM LUT region/index/data writes.

## State and Persistence

The header stores no software state. Its constants describe persistent hardware register fields whose values remain in display-controller state until reset, power transition, firmware/hardware action, or driver writes change them.

Important state domains include cursor surface address and geometry, cursor memory power state, performance-monitor configuration and latched counter values, DPP clock/reset/CRC state, CNVC pixel-format and color-key state, DSCL scaler geometry/filter/line-buffer/memory state, and CM matrix/LUT/range-clamp/output-conversion state.

Full-width fields such as cursor surface addresses, perfmon low counters, coefficient RAM data, and debug data need normal 32-bit MMIO treatment. Narrow fields packed into shared registers require preserving unrelated and reserved bits, especially in clock control, soft reset, memory power, LUT write-enable, and interrupt/status registers.

## Dependencies and Integration Points

This chunk has no runtime dependencies beyond the C preprocessor, but it is meaningful only as generated ASIC data integrated with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_offset.h` for register addresses and base indices.
- `display/dc/dpp/dcn10/dcn10_dpp.h`, where many `DSCL0`, `CM0`, `CNVC_CFG0`, `CNVC_CUR0`, and `DPP_TOP0` fields from this chunk are assembled into DCN 1.0 DPP register masks.
- DCN 1.0 resource, IRQ, and GPIO translation code that includes the same generated offset and mask headers.
- The common AMD display register helper layer, which consumes mask/shift structures generated from these macro names.

The repeated `0` and `1` instance prefixes are important. DPP0 fields are directly represented in the DCN 1.0 DPP field lists; DPP1 fields describe the same hardware layout for the next pipe instance and must remain bit-compatible where the ASIC design is replicated.

## Risks

The main risk is silent hardware misprogramming. A wrong mask or shift still compiles, but can set the wrong bit, corrupt a neighboring field, fail to reset or enable a display subblock, select the wrong scaler mode, damage color conversion, or leave performance counters and memory-power controls in an unexpected state.

Chunk-boundary risk is real here. The slice starts after the first `CURSOR3_CURSOR_CONTROL` shift definitions and ends before the full `CM1_CM_DGAM_RAMB_*` region. The final per-file reconciliation should not describe either boundary group as complete based only on this chunk.

Generated repeated instances are copy/generation sensitive. Differences between `DPP_TOP0` and `DPP_TOP1`, `CNVC_CFG0` and `CNVC_CFG1`, `DSCL0` and `DSCL1`, or `CM0` and `CM1` may be either legitimate instance offsets in companion files or accidental field drift. Static comparison is useful because the error mode is usually hardware-visible display corruption rather than an obvious compiler failure.

Status and control bits share registers with reserved fields. Blind writes to soft reset, memory power, perfmon interrupt ack, LUT write-enable, or clock-gating registers can disrupt active pipes. Color-management LUT and PWL region fields also have ordering and bank-selection concerns: writing indices, data, region starts, slopes, and end points out of order can produce incorrect gamma/color output.

## Test Signals

Useful validation signals for this chunk are mostly build, generated-data, and hardware-display oriented:

- Build all DCN 1.0 display objects that include `dcn_1_0_sh_mask.h`, especially DPP, resource, IRQ, and GPIO translation units.
- Static generated-header checks that each `__SHIFT` has a matching mask, masks align with their shifts, masks fit in 32 bits, and duplicate macro names are absent.
- Instance-layout comparison for DPP0/DPP1, CNVC0/CNVC1, DSCL0/DSCL1, and CM0/CM1 fields that should be identical aside from register addresses.
- Regeneration or diff checks against the authoritative DCN 1.0 ASIC register database.
- Modeset smoke tests using multiple pipes to exercise DPP0 and DPP1 clocking, soft reset, format conversion, scaler programming, line-buffer setup, and cursor behavior.
- Plane scaling tests covering luma/chroma ratios, init phases, two-tap settings, coefficient RAM writes, recout/MPC geometry, and line-buffer memory configuration.
- Color pipeline tests for input CSC, gamut remap, output CSC, degamma/regamma LUT programming, PWL region setup, bias/scale, range clamp, HDR multiplier, and output rounding/truncation.
- Perfmon tests that program `DC_PERFMON11` and `DC_PERFMON12`, start/stop counting, read low/high values, and exercise interrupt status/ack paths.
- Runtime register readback around memory power/status fields for cursor, DSCL, output buffer, and CM memories after power-management transitions.

## Cross-Chunk Notes

This is an interior slice of a 54345-line generated header. Adjacent chunks should provide the beginning of `CURSOR3_CURSOR_CONTROL` before line 12473 and the continuation of `CM1_CM_DGAM_RAMB_*` plus the rest of DPP1 color-management state after line 15001.

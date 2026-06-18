# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 29605-32147

## Scope

This chunk is `subset-b-001845`, covering lines 29605-32147 of the generated DCN 3.1.4 register shift/mask header. It is a source-aligned chunk document only; the full per-file research document is expected to be assembled later from all chunks for `dcn_3_1_4_sh_mask.h`.

The chunk starts mid-definition for `CM3_CM_SHAPER_RAMB_REGION_28_29`, continues through several color-management and output-pixel-processor register blocks, covers the complete `OTG0` timing-generator field surface, and ends in the first half of `OTG1_OTG_TRIGA_CNTL`.

## Purpose

`dcn_3_1_4_sh_mask.h` provides generated C preprocessor constants for AMD DCN 3.1.4 display hardware register fields. For each hardware register field, it defines a `__SHIFT` value and a `_MASK` value. Driver code combines these constants with register offsets from `dcn_3_1_4_offset.h` to read, write, and update individual bitfields in memory-mapped display registers.

Within this chunk, the constants describe:

- Color-management shaper RAM and 3D LUT programming fields for `CM3`.
- Display performance-monitor counter control/status/value fields for DPP perfmon instance 13 and OPP perfmon instance 14.
- Formatter (`FMT0`-`FMT3`) clamp, pixel encoding, subsampling, dithering, truncation, 4:2:0 memory, and 4:2:2 control fields.
- Display pattern generator (`DPG0`-`DPG3`) fields for test-pattern enable, ramp generation, colors, dimensions, and status.
- Output pixel processor buffer and pipe fields (`OPPBUF0`-`OPPBUF3`, `OPP_PIPE0`-`OPP_PIPE3`), including 3D parameters and CRC controls/results.
- Output data path support fields in `OPP_TOP`, ABM, DSC remapper (`DSCRM0`-`DSCRM3`), and ODM/OPTC input (`ODM0`-`ODM3`).
- Full `OTG0` timing-generator fields for horizontal/vertical timing, vtotal/DRR control, triggers, stereo/interlace, status readback, interrupts, update locks, CRC capture, global sync lock, DSC start position, pipe update status, and spare storage.
- The beginning of equivalent `OTG1` timing-generator fields, through `OTG1_OTG_TRIGA_CNTL`.

## Important API Surface

This header chunk does not declare C functions or types. Its API is the macro namespace exported to the AMD display driver.

Every definition follows the generated field convention:

- `REGISTER__FIELD__SHIFT` gives the low bit position for `FIELD` inside `REGISTER`.
- `REGISTER__FIELD_MASK` gives the bit mask for the same field.

The common AMD display helpers depend on this exact spelling. In `display/dc/inc/reg_helper.h`, `FN(reg, field)` expands to `FD(reg##__##field)`, and `FD` is supplied by each hardware block to fetch the shift/mask pair from its register-field table. In lower-level/common code, `CGS_REG_FIELD_SHIFT(reg, field)` and `CGS_REG_FIELD_MASK(reg, field)` use the same token-pasting naming contract.

The DCN314 resource setup includes this file alongside `dcn_3_1_4_offset.h`, then uses block-specific field-list macros to populate register descriptors. A mismatch between these generated names and the field lists in files such as `display/dc/opp/*`, `display/dc/optc/*`, or `display/dmub/src/*` usually fails at compile time because the token-pasted macro or struct member no longer exists.

Important macro families in this chunk:

- `CM3_CM_SHAPER_RAMB_REGION_*`, `CM3_CM_MEM_PWR_*`, and `CM3_CM_3DLUT_*`: fields for shaper LUT region layout, memory power control/status, 3D LUT mode/index/data/read-write selection/output normalization, RGB output offsets/scales, and CM test-debug access.
- `DC_PERFMON13_*` and `DC_PERFMON14_*`: performance-counter event selection, counted value selection, increment/run/interrupt modes, counted-value type, hardware stop controls, counter state, perfmon state, run-enable start/stop selection, interrupt status/ack bits, and low/high counter value access.
- `FMT{0,1,2,3}_*`: repeated formatter instance fields for clamp bounds, dynamic expansion, output pixel encoding/subsampling, spatial and temporal dithering, truncation depth/mode, pseudo-random dither seeds, clamp control, side-by-side stereo, 4:2:0 map-memory power, and 4:2:2 control.
- `DPG{0,1,2,3}_*`: repeated display-pattern-generator fields for enable, ramp mode, ramp increment, dimensions, color components, offset segment, and status.
- `OPPBUF{0,1,2,3}_*`: active width, pixel repetition, display segmentation, 3D vactive space sizes, left/right eye offsets, and additional buffer control.
- `OPP_PIPE_CRC{0,1,2,3}_*`: CRC enable/source/stereo/reset/window/control fields and result registers for red/green and blue channels.
- `ODM{0,1,2,3}_OPTC_*`: OPTC input global control, segment source selection, data format/DSC mode, bytes per pixel, slice/segment width, input clock gating/status, memory selection, and spare register fields.
- `OTG0_OTG_*`: the broadest family in this chunk, defining the complete timing-generator control surface for one OTG instance.
- `OTG1_OTG_*`: the same generated naming pattern for a second OTG instance begins near the end of the chunk, but this chunk stops before completing `OTG1`.

## Control Flow

There is no runtime control flow in this header. Its control-flow impact is indirect:

1. DCN314 initialization includes the generated offset and shift/mask headers.
2. Resource construction macros create per-block register and field tables for OPP, OPTC/OTG, DMUB, and other display components.
3. Runtime display code invokes helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `OPP_SF`, or `SF`-based tables with semantic field names.
4. The helpers use the generated shifts and masks to preserve unrelated register bits while packing or extracting the requested field.

For example, OTG timing code can update `OTG0_OTG_H_TOTAL__OTG_H_TOTAL` or `OTG0_OTG_V_TOTAL_CONTROL__OTG_V_TOTAL_MIN_SEL` through token-pasted field names without hard-coding bit positions in the functional timing-generator implementation. Similarly, OPP code can program formatter dither/truncation fields using the `FMT0_*` field definitions, and CRC/debug code can read back `OPP_PIPE_CRC*_OPP_PIPE_CRC_RESULT*` or `OTG0_OTG_CRC*_DATA_*` fields.

The chunk also contains many write-one-to-clear or ack-style interrupt fields, such as `*_ACK`, `*_CLEAR`, and `*_INT_STATUS`. The header does not encode side effects, but its masks are the exact bits later used by interrupt handlers or polling paths.

## State And Persistence Behavior

The macros themselves are compile-time constants and maintain no software state. The state they address lives in DCN hardware registers and associated memories:

- `CM3_CM_SHAPER_RAMB_REGION_*` and `CM3_CM_3DLUT_*` fields select and populate color LUT RAM state. These values persist in display hardware until reprogrammed, reset, power-gated, or overwritten during a mode/color pipeline update.
- `CM3_CM_MEM_PWR_CTRL2` and `CM3_CM_MEM_PWR_STATUS2` represent hardware memory power requests and observed memory power state for shaper and HDR 3D LUT RAMs.
- `FMT*` fields persist formatter output behavior: clamp limits, pixel encoding, dithering/truncation mode, dither seeds, 4:2:0 memory power, and 4:2:2 conversion state.
- `DPG*` fields persist pattern-generator mode and color/ramp parameters, typically used for test patterns or diagnostics.
- `OPPBUF*` and `OPP_PIPE*` fields persist OPP buffer layout, segmentation/MSO-related configuration, and pipe routing.
- `OPP_PIPE_CRC*`, `OTG0_OTG_CRC*`, and perfmon fields expose accumulating or latched diagnostic state. Some status bits are cleared through paired `ACK` or `CLEAR` fields.
- `ODM*` fields persist input segmentation and DSC/format selection for the OPTC path. These are central to multi-stream/output-split modes and need to match pipe/resource allocation.
- `OTG0` timing fields persist the active timing-generator configuration: totals, blanking, sync timing/polarity, dynamic refresh rate ranges, master enable, global update lock state, vertical interrupt positions, global sync lock behavior, CRC windows, and pipe update status.

Most of these registers are not persisted across GPU reset, suspend/resume reinitialization, or display engine power-down. Driver state reconstruction depends on the DC resource and hardware-sequencing layers reprogramming the correct fields from current display state.

## Dependencies And Integration Points

Primary dependencies:

- `dcn_3_1_4_offset.h`: provides the matching register addresses and base-index macros. The shift/mask definitions in this chunk are only meaningful when paired with the corresponding offsets.
- `display/dc/inc/reg_helper.h`: supplies generic field packing/unpacking helpers used by display hardware blocks.
- `display/dc/resource/dcn314/dcn314_resource.c`: includes this header and wires DCN314 register definitions into resource construction.
- OPP implementation and headers, including `display/dc/opp/dcn10/dcn10_opp.h` and later OPP layers: consume the `FMT*`, `OPPBUF*`, and `OPP_PIPE_CRC*` field names through OPP field-list macros.
- OPTC/OTG implementation and headers, including `display/dc/optc/dcn32/dcn32_optc.h` and related timing-generator code: consume the `OTG0_*` and `ODM0_*` fields and instantiate repeated blocks for other hardware instances.
- DMUB display code: includes the DCN314 shift/mask header for firmware-facing register access tables.

Integration is heavily macro-driven. The visible register prefix often encodes a hardware instance (`FMT0`, `FMT1`, `ODM0`, `OTG0`, `OTG1`), while functional code often uses a block-local register table and an instance id. The resource layer maps instance-specific offsets and shift/mask values into those tables so shared OPP/OPTC code can operate on instance-agnostic field members.

## Register Block Notes

### CM3 Color Management

The chunk starts at line 29605 inside `CM3_CM_SHAPER_RAMB_REGION_28_29`, so the first two shift definitions for region 28 are in the previous chunk. The visible lines complete region 29 shifts and the region 28/29 masks, then define region pairs 30/31 and 32/33. Each pair uses 9-bit LUT offset masks (`0x000001FF`/`0x01FF0000`) and 3-bit segment-count masks (`0x00007000`/`0x70000000`) packed into low and high halfwords.

`CM3_CM_MEM_PWR_CTRL2` and `CM3_CM_MEM_PWR_STATUS2` describe force/disable controls and status fields for shaper and HDR 3D LUT memories. `CM3_CM_3DLUT_MODE`, index, data, 30-bit data, read/write control, normalization, RGB offset/scale, and test-debug registers form the programming surface for the 3D LUT path.

### Performance Monitors

`DC_PERFMON13_*` is attached to `dce_dc_dpp3_dispdec_dpp_dcperfmon_dc_perfmon_dispdec`, and `DC_PERFMON14_*` is attached to `dce_dc_opp_opp_dcperfmon_dc_perfmon_dispdec`. Both blocks expose the same structure:

- `PERFCOUNTER_CNTL` for event selection, counted value source, increment mode, hardware/run enable, restart, interrupt enable, active status, and counter select.
- `PERFCOUNTER_CNTL2` for counted-value type, stop selectors, count-off selector, and second-level selector.
- `PERFCOUNTER_STATE` for eight packed counter states and selection bits.
- `PERFMON_CNTL`/`PERFMON_CNTL2` for perfmon state, repeat count, count-off interrupt behavior, clock enable, and run-enable start/stop selectors.
- `PERFMON_CVALUE_INT_MISC`, `PERFMON_CVALUE_LOW`, `PERFMON_HI`, and `PERFMON_LOW` for interrupt status/ack and counter value readback.

These fields are diagnostic and performance-observation infrastructure. Bugs here may not break basic scanout but can break perf counters, debug tooling, or tests that rely on perfmon interrupts and value reads.

### OPP Formatter And Test/CRC Blocks

The `FMT0` through `FMT3` register groups are repeated with identical field layouts. They control output formatting per OPP instance: color clamp lower/upper limits per component, dynamic expansion enable/mode, pixel encoding and subsampling, stereo override, dithering/truncation enable/depth/mode, temporal dither parameters, random seed registers, clamp behavior, 4:2:0 memory power, and 4:2:2 control.

`DPG0` through `DPG3` provide per-OPP pattern-generator controls. Fields cover enable/mode, ramp increment, dimensions, RGB/YCbCr color registers, offset segment, and status. These are likely used by diagnostics, bring-up, or validation paths rather than normal composition.

`OPPBUF0` through `OPPBUF3` cover active width, pixel repetition, display segmentation, overlap pixels, 3D vactive space sizing, 3D offset parameters, and buffer control. These fields integrate with multi-stream output, stereo/3D, and segmentation decisions made above the OPP layer.

`OPP_PIPE_CRC0` through `OPP_PIPE_CRC3` provide CRC enable/source/mode/reset/window selection and result fields. They are important for display validation, pipe CRC debugfs-style tests, and visual correctness checks.

`OPP_TOP_CLK_CONTROL` and `OPP_ABM_CONTROL` provide top-level OPP clock gating/status and ABM pipe source selection. `DSCRM0` through `DSCRM3` define DSC forward-remapper configuration, including source selection, enable/disable state, and memory power fields.

### ODM And OPTC Input

`ODM0` through `ODM3` describe the OPTC input and output data merger path. Their fields include underflow status/clear, double-buffer pending state, segment source selectors, number of input segments, memory selection, DSC/data format mode, DSC bytes per pixel, DSC slice width, segment width, input clock enable/on/gate-disable, and spare registers.

These definitions are used when a stream is split across multiple pipes or when DSC/ODM combine/split modes are active. The segment source fields must stay consistent with pipe topology and timing-generator programming.

### OTG0 Timing Generator

The `OTG0` block is the largest part of this chunk. It defines the bitfield surface for one output timing generator:

- Basic timing: horizontal total, hblank start/end, hsync start/end/control, timing divide mode, vertical total/min/max/mid, vblank, vsync, and vsync mode.
- Dynamic refresh and vtotal control: min/max selection, mid replacing min/max, forced lock, event active period, mid frame count, set-vtotal-min mask, DRR timing interrupts, DRR reach range, change limit, trigger window, average frame, and last-used vtotal.
- Triggers and flow: trigger A/B source, pipe select, polarity, edge detect, delay, clear/manual trigger; force-count-now controls; flow-control position/delay; manual trigger/flow-control bits.
- Enable/status/readback: master enable, current master enable state, start/disable point control, field number, output mux, pixel data readback, blanking/status/position/frame/vf/hv count, count reset/control, interlace status/control, and stereo status/control.
- Interrupts: generic OTG interrupt control, vertical interrupt 0/1/2 positions and controls, force-vsync-next-line status/clear, vtotal interrupt status, and vsync nominal clear.
- Update synchronization: update lock, double-buffer controls, master update lock/status, global update controls, vstartup/vupdate/vready, global sync status, global sync lock control/window, vupdate keepout, and global control registers.
- CRC/static screen/debug: CRC control, CRC windows, CRC data registers, CRC signature masks, static screen event/status masks, 3D structure, clock control/status, DSC start position, pipe update status, and spare register.

The chunk then begins `OTG1`, repeating the initial timing fields and reaching `OTG1_OTG_TRIGA_CNTL`. The rest of OTG1 is outside this chunk.

## Risks

- Generated header drift is high impact. If a shift or mask does not match the hardware register specification, the functional code may compile and run while silently writing the wrong bits.
- Repeated instance blocks are easy to misalign. `FMT0`-`FMT3`, `DPG0`-`DPG3`, `OPPBUF0`-`OPPBUF3`, `ODM0`-`ODM3`, and `OTG0`/`OTG1` must retain identical field layouts where the hardware expects repeated instances.
- Boundary chunks can obscure complete register definitions. This chunk starts inside `CM3_CM_SHAPER_RAMB_REGION_28_29` and ends inside `OTG1_OTG_TRIGA_CNTL`; merge/reconciliation must join adjacent chunks before treating those registers as fully documented.
- Interrupt fields with `ACK`, `CLEAR`, `MSK`, `STATUS`, and `INT_TYPE` have hardware side effects that are not visible in this header. Callers must know whether a field is read-only, write-one-to-clear, level-triggered, or edge-triggered from the register spec or existing driver behavior.
- Timing-generator fields are mode-critical. Incorrect masks for totals, blanking, sync, update locks, or DRR can cause blank screens, unstable refresh rates, hangs waiting for pending updates to clear, or missed vertical interrupts.
- CRC/perfmon fields are test-critical. They may not affect ordinary desktop output, but regressions break validation tools, pipe CRC tests, performance instrumentation, and display debug workflows.
- Power-control fields can create resume or low-power bugs. Incorrect memory power force/disable masks for LUT, formatter map memory, DSC remapper, or OPP top clock control can manifest only after power-gating, suspend/resume, or mode-set sequences.

## Test Signals

Useful validation signals for changes affecting this chunk include:

- Build coverage for DCN314 display code, especially `dcn314_resource.c`, OPP, OPTC, and DMUB users. Token-pasted field references catch many naming mismatches at compile time.
- KMS mode-set tests across multiple timing generators, including single-display and multi-display configurations, to exercise `OTG0` and `OTG1` timing fields.
- Variable refresh / DRR tests that verify vtotal min/max/mid programming, DRR trigger windows, update pending status, and vtotal reach interrupts.
- Pipe CRC tests that compare stable CRC output from `OPP_PIPE_CRC*` and `OTG0_OTG_CRC*` result fields under known frame content.
- Dithering, truncation, pixel-format, 4:2:0, and 4:2:2 output-format tests to cover the `FMT*` field families.
- DSC and ODM split-mode tests to exercise `DSCRM*` and `ODM*` source, format, width, bytes-per-pixel, and memory-selection fields.
- Display pattern generator diagnostics for `DPG*` ramp/color/dimension fields.
- Suspend/resume and display power-gating tests to reveal incorrect memory power and clock-gating masks.
- Perfmon/debug tests that program `DC_PERFMON13` and `DC_PERFMON14` event counters, verify interrupt status/ack handling, and read low/high counter values.

## Research Notes

The line range was read directly from the source header and cross-checked against `Docs/researches/chunk_manifest.tsv`, which maps `subset-b-001845` to lines 29605-32147 and output path `Docs/researches/chunks/subset-b-001845_research.md`. No final source-tree report was written, and `Docs/researches/blueprint_checklist.md` was not modified.

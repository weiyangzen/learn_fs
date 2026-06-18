# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_offset.h lines 5278-7852

## Purpose

This chunk is generated AMD DCN 3.1.4 display-controller register-offset metadata. It contains no executable C logic; it publishes preprocessor constants that map symbolic display hardware register names to numeric MMIO offsets plus companion base-index selectors. Runtime code combines `reg...` offsets with matching `reg..._BASE_IDX` values through register-table helper macros before issuing actual `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, or polling operations.

The range covers the end of DPP pipe 1, complete DPP pipe 2 and DPP pipe 3 display processing blocks, the first four OPP output-pixel-processing blocks, OPP top/DSCRM/perfmon metadata, the first four ODM input blocks, and the beginning of OTG0 timing-generator metadata. Although the repository path is under a local `ceph-client` source mirror, this header is AMDGPU display-driver hardware metadata and does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, local includes, allocation paths, or locking primitives in this slice. The public interface is the generated macro namespace:

- `reg<block>_<register>`: a DCN 3.1.4 MMIO register offset.
- `reg<block>_<register>_BASE_IDX`: the DCN base-address segment selector for that register.

The requested range contains 2,383 `#define reg...` lines: 1,192 register-offset macros and 1,191 `_BASE_IDX` macros. All `_BASE_IDX` values present in the range are `2`. The apparent one-macro mismatch is a chunk-boundary artifact: line 7852 contains `regOTG0_OTG_FLOW_CONTROL`, while `regOTG0_OTG_FLOW_CONTROL_BASE_IDX` is on the next source line outside this work item.

Major macro families in this chunk:

- DPP1 tail: `regDPP_TOP1_DPP_CRC_*`, `regDPP_TOP1_DPP_CRC_CTRL`, and `regDPP_TOP1_HOST_READ_CONTROL`.
- `CNVC_CFG1`/`2`/`3`: surface pixel format, format control, floating-point bias/scale, color keyer, alpha LUT, pre-dealpha/realpha, pre-CSC matrices, coefficient format, and pre-degamma offsets.
- `CNVC_CUR1`/`2`/`3`: cursor control, cursor colors, and cursor floating-point scale/bias offsets.
- `DSCL1`/`2`/`3`: scaler coefficient RAM, mode/tap controls, horizontal/vertical ratios and inits, black color, update/autocal, overscan, OTG blanking, recout/MPC sizes, line-buffer format and memory controls, OBUF controls, and DSCL memory power/status.
- `CM1`/`2`/`3`: color-management control, post-CSC, gamut remap, output CSC, output color-space conversion, degamma/regamma/LUT setup, 3D LUT controls, bias/scale, HDR multiplier, dynamic-expansion, debug, and test/debug-data registers.
- `DC_PERFMON11`/`12`/`13`: DPP-local perf counter control, state, current value, high/low counters, and perfmon control registers.
- `DPP_TOP2`/`3`: DPP control, CRC control/value, and host-read control for DPP pipes 2 and 3.
- `FMT0` through `FMT3`: clamp components, dynamic expansion, bit-depth and 420/422 formatting, dithering/randomization, memory control, and format control offsets.
- `DPG0` through `DPG3`: display pattern generator control, ramp, dimensions, RGB/YUV color components, offset segment, and status.
- `OPPBUF0` through `OPPBUF3`, `OPP_PIPE0` through `OPP_PIPE3`, and `OPP_PIPE_CRC0` through `OPP_PIPE_CRC3`: output buffer controls, 3D parameters, pipe control, CRC mask/control/results.
- `OPP_TOP`, `DSCRM0` through `DSCRM3`, and `DC_PERFMON14`: OPP clock/ABM control, DSC forward config per stream, and OPP-local perf counter metadata.
- `ODM0` through `ODM3`: OPTC input global control, data-source select, data format, bytes per pixel, width, input clock, memory config, and spare registers.
- OTG0 beginning: horizontal/vertical timing totals, blanking, sync, trigger, forced-count, interrupt-status, and flow-control offsets.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by DCN314 display code:

1. DCN314 resource, IRQ, and DMUB code include `dcn_3_1_4_offset.h` together with the matching `dcn_3_1_4_sh_mask.h`.
2. Register-list macros paste block names and instance IDs into symbols such as `regCNVC_CFG2_FORMAT_CONTROL`, `regDSCL3_DSCL_UPDATE`, `regFMT1_FMT_BIT_DEPTH_CONTROL`, `regOPP_PIPE_CRC0_OPP_PIPE_CRC_RESULT2`, or `regODM3_OPTC_DATA_SOURCE_SELECT`.
3. Helpers in `dcn314_resource.c`, such as `SR(...)`, `SRI(...)`, and `SRII(...)`, compute `BASE(reg..._BASE_IDX) + reg...` and populate per-block register tables.
4. Display manager code then uses those tables to program plane formatting, scaling, color transforms, output formatting, pattern generation, CRC capture, DSC forwarding, ODM routing, and timing-generator state.

The macros do not encode ordering constraints. Consumers must still sequence clocks, memory power, pipe lock/unlock, double-buffered updates, color/LUT programming, scaling coefficient loads, output formatting, CRC capture, ODM routing, timing changes, interrupt handling, and suspend/resume restoration correctly.

## State And Persistence Behavior

This chunk stores no software state and persists nothing. It names MMIO-backed GPU state whose lifetime is hardware-defined. Represented state includes:

- DPP input and plane-processing state for pixel format conversion, color keying, cursor composition, scaler ratios/taps, line-buffer and OBUF memory, DPP CRCs, and host reads.
- DPP color state for post-CSC, gamut remap, output CSC, degamma/regamma, LUT setup, 3D LUT control, HDR multiplier, dynamic expansion, and debug/test capture.
- Perfmon counter state for DPP pipes 1 through 3 and the OPP block.
- OPP output state for format clamping/dithering, 4:2:0/4:2:2 conversion, pattern generation, output buffering, pipe control, pipe CRC, ABM, and DSC forwarding.
- ODM input state for OPTC source selection, width/data-format configuration, input clocks, bytes-per-pixel accounting, and memory configuration.
- The beginning of OTG0 timing state for totals, blanking, sync, triggers, status, forced count, and flow control.

Configuration registers generally retain values until modeset, pipe reallocation, power gating, suspend/resume, or ASIC reset. Status, interrupt, debug, CRC, perf-counter, memory-power, update, and trigger registers can be read-only, sticky, self-clearing, write-one-to-clear, or sequencing-sensitive. This offset header does not describe those semantics; field masks in `dcn_3_1_4_sh_mask.h` and the consuming display code provide the operational meaning.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.1.4 register database and must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h` for field shifts and masks.
- DCN314 base definitions such as `DCN_BASE__INST0_SEG2`, used by `BASE(reg..._BASE_IDX)`.

Observed include sites in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn314/irq_service_dcn314.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn314.c`

The strongest integration point is `dcn314_resource.c`, which includes this header, defines `DCN_BASE__INST0_SEG2` as the segment base, and uses token-pasting helpers to expand inherited DCN register-list macros such as `DPP_REG_LIST_DCN30(id)`, `OPP_REG_LIST_DCN30(id)`, and `OPTC_COMMON_REG_LIST_DCN3_14(id)`. `dmub_dcn314.c` includes the same offset and mask headers and computes offsets for the DMUB service register table via `REG_OFFSET_EXP(reg_name)`.

## Risks And Edge Cases

- Offset or base-index drift is the central risk. These are untyped preprocessor constants, so a wrong offset or `_BASE_IDX` can compile cleanly while directing register accesses to the wrong MMIO location.
- Repeated pipe families are copy-sensitive. DPP1/DPP2/DPP3, FMT0-FMT3, DPG0-DPG3, OPPBUF0-OPPBUF3, OPP pipe CRC0-CRC3, DSCRM0-DSCRM3, and ODM0-ODM3 are similar but not interchangeable; a single instance typo may only appear with particular display counts or pipe allocations.
- The line range starts after the beginning of DPP1 and ends in the middle of OTG0. File-level conclusions about DPP1 and OTG0 require adjacent chunks.
- Color and scaler registers are format-sensitive. Wrong CNVC, DSCL, CM, LUT, or HDR multiplier offsets can produce incorrect colors, cursor composition bugs, scaling artifacts, invalid CSC/gamut remap, or failures limited to specific pixel formats.
- Memory-power, OBUF, line-buffer, and update registers are sequencing-sensitive. Access while a block is gated, reset, or not clocked may be ignored, hang polling paths, or leave stale double-buffered state.
- OPP/FMT/DPG/CRC registers affect visible output and diagnostics. Offset mistakes can cause blank output, invalid dithering/clamping, broken test patterns, CRC mismatches, or misleading debug/perfmon data.
- ODM and OTG registers interact with timing and multi-pipe composition. Wrong source, width, clock, memory, blanking, sync, trigger, or flow-control offsets can break high-resolution, split-pipe, or multi-display modes.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware behavior:

- Build AMDGPU/DC with DCN314 enabled; missing or renamed macros should fail while constructing DPP, OPP, OPTC, IRQ, and DMUB register tables.
- Mechanically verify that each non-`_BASE_IDX` `reg...` macro in this range has one matching `_BASE_IDX` macro, allowing for the documented boundary case where `regOTG0_OTG_FLOW_CONTROL_BASE_IDX` is immediately after line 7852.
- Verify all in-range `_BASE_IDX` values remain `2`, matching the DCN314 `DCN_BASE__INST0_SEG2` address segment used by resource and DMUB code.
- Diff this generated range against AMD's authoritative DCN 3.1.4 register database and adjacent DCN 3.x headers where compatibility is expected.
- Exercise display modes that allocate DPP/OPP/ODM instances 1 through 3: multi-monitor modesets, pipe split/ODM paths, scaling, cursor composition, rotation/format changes, HDR and color-management paths, and suspend/resume.
- Validate visual and diagnostic output: DPP/OPP CRC capture, DPG patterns, color/gamma/LUT programming, scaler coefficient loading, dithering/clamping, 420/422 formatting, ABM paths, and perfmon counters.
- Watch kernel logs and display diagnostics for underflow, stuck update/power-status polling, CRC mismatches, color corruption, scaler artifacts, blank display after modeset, broken resume, or failures limited to high-bandwidth ODM/OTG configurations.

## Cross-Chunk Notes

The previous chunk owns the start of DPP1, including the beginning of `DPP_TOP1`. This chunk begins at the DPP1 CRC/host-read tail and then covers complete CNVC/DSCL/CM/perfmon blocks for DPP1. The next chunk continues OTG0 immediately after `regOTG0_OTG_FLOW_CONTROL`, including its matching `_BASE_IDX` and the rest of the OTG0 timing-generator register set. The final per-file research document should reconcile these boundaries before making complete claims about all DPP or OTG register coverage in `dcn_3_1_4_offset.h`.

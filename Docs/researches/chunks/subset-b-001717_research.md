# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_offset.h lines 2695-5217

## Purpose

This chunk is generated AMD DCN 3.0.1 register-offset metadata. It contains no executable C functions, structs, enums, variables, locking, allocation, or persistence logic. Its exported interface is a dense set of preprocessor constants that map symbolic DCN display-controller register names to numeric MMIO offsets and matching base-address segment selectors.

The requested range is a middle slice of `dcn_3_0_1_offset.h`. It starts at the tail of the HUBP2 block with `mmHUBP2_DCSURF_SEC_VIEWPORT_DIMENSION_C_BASE_IDX`, then covers:

- The remainder of HUBP2 top-level plane-fetch controls.
- Complete HUBPREQ2, HUBPRET2, CURSOR0_2, and HUBP2 performance-monitor blocks.
- Complete HUBP3, HUBPREQ3, HUBPRET3, CURSOR0_3, and HUBP3 performance-monitor blocks.
- DPP instance 0 top/CNVC/CNVC cursor/DSCL/CM/perfmon blocks.
- DPP instance 1 top/CNVC/CNVC cursor/DSCL/CM/perfmon blocks.
- DPP instance 2 top/CNVC/CNVC cursor/DSCL and the beginning of CM2, ending at `mmCM2_CM_SHAPER_RAMA_REGION_10_11_BASE_IDX`.

The chunk has 2,419 `#define` lines: 1,209 complete register-offset macros and 1,210 `_BASE_IDX` macros. The one extra base-index macro is the opening line for a register whose matching offset appears in the previous chunk. All visible `_BASE_IDX` values are `2`, so consumers address these registers through DCN base segment 2 plus the generated offset.

Although this repository path is under `sources/distributed-fs/ceph-client`, the file is AMDGPU display-driver hardware metadata. It does not implement Ceph, filesystem, network, or storage behavior.

## Important APIs, Types, And Macros

The API surface is the generated macro namespace:

- `mm<block><instance>_<register>`: a DCN 3.0.1 MMIO register offset.
- `mm<block><instance>_<register>_BASE_IDX`: the base segment selector paired with that offset.
- Register-list expansion macros in consumers paste register names into those symbols and compute absolute addresses as `BASE(mm..._BASE_IDX) + mm...`.

There are no locally declared C types or functions. The important contract is exact spelling, instance numbering, numeric offset value, and `_BASE_IDX` pairing.

Major macro families in this range:

- `HUBP2_*` and `HUBP3_*`: surface configuration, address and tiling configuration, primary and secondary viewport start/dimension registers for luma and chroma planes, request-size configuration, HUBP control, clock control, virtual-memory page-gating configuration, debug registers, and DCFCLK/DPPCLK measurement windows.
- `HUBPREQ2_*` and `HUBPREQ3_*`: surface pitch, VMID settings, primary and secondary surface addresses and high halves, chroma-plane address variants, primary and secondary metadata surface addresses, surface control, flip control, flip interrupt, in-use and earliest-in-use tracking, expansion mode, TTU/QoS controls for surface and cursor fetches, VM DMDATA control, system aperture low/high addresses, L1 TLB control, blank/destination/prefetch/vblank/flip/nominal timing parameters, per-line delivery, cursor settings, reference-to-pixel-frequency ratio, DRQ limit, and memory-power control/status.
- `HUBPRET2_*` and `HUBPRET3_*`: return-path control, memory-power control/status, read-line controls, read-line values/status, and return-path interrupt registers.
- `CURSOR0_2_*` and `CURSOR0_3_*`: cursor control, surface address/high address, size, position, hot spot, stereo control, destination offset, memory-power control/status, and DMDATA address/control/QoS/status/software data registers.
- `DC_PERFMON8_*`, `DC_PERFMON9_*`, `DC_PERFMON10_*`, and `DC_PERFMON11_*`: per-block performance counter control, secondary control, state, global perfmon control, current-value misc/low, high, and low counter registers for HUBP2, HUBP3, DPP0, and DPP1.
- `DPP_TOP0_*`, `DPP_TOP1_*`, and `DPP_TOP2_*`: DPP control, soft reset, CRC readback/control, and host-read control registers.
- `CNVC_CFG0_*`, `CNVC_CFG1_*`, and `CNVC_CFG2_*`: surface pixel format, format conversion, FP bias/scale, color-keyer controls and color bounds, alpha LUT, pre-dealpha, pre-CSC mode/matrix coefficients including B variants, coefficient format, pre-degamma, and pre-realpha.
- `CNVC_CUR0_*`, `CNVC_CUR1_*`, and `CNVC_CUR2_*`: formatter-side cursor control, cursor colors, and FP scale/bias.
- `DSCL0_*`, `DSCL1_*`, and `DSCL2_*`: scaler coefficient RAM access, scaler mode, tap control, DSCL control, 2-tap control, manual replicate control, horizontal and vertical scale ratios/initial phases for luma and chroma, black color, update/autocal, overscan, OTG blanking, recout start/size, MPC size, line-buffer format and memory control, vertical counter, DSCL memory-power control/status, output-buffer control, and OBUF memory-power control.
- `CM0_*` and `CM1_*`: complete DPP color-management blocks, including CM control, post-CSC, gamut remap, bias, gamcor controls and LUTs, gamcor RAMA/RAMB PWL region programming, blend-gamma controls and LUTs, HDR multiplier, memory-power controls, dealpha, coefficient format, shaper controls/LUTs/RAMA/RAMB regions, 3D LUT mode/index/data/read-write controls, output normalization and offsets, and debug index/data registers.
- `CM2_*`: the same color-management pattern as CM0/CM1 through the start of the shaper RAMA region list. This chunk stops before the rest of CM2's shaper RAMA/RAMB, memory-power2, 3D LUT, and debug offsets.

## Control Flow

This header has no local runtime control flow. It participates in driver control flow through inclusion and macro expansion:

1. DCN301 display resource code includes `dcn_3_0_1_offset.h`, `dcn_3_0_1_sh_mask.h`, and the ASIC IP base-offset header.
2. `dcn301_resource.c` defines expansion helpers such as `SR`, `SRI`, `SRII`, and related variants. These paste block and instance tokens into symbols such as `mmHUBPREQ2_DCSURF_SURFACE_PITCH_BASE_IDX` and `mmHUBPREQ2_DCSURF_SURFACE_PITCH`.
3. Resource tables are built for four DPP instances and four HUBP instances. The visible chunk supplies all of the register offsets needed for HUBP/HUBPREQ/HUBPRET/CURSOR instances 2 and 3, and most of the DPP/CNVC/DSCL/CM register coverage for DPP instances 0 through 2.
4. Functional modules later use populated register tables with `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, `REG_GET`, `REG_WAIT`, and related helpers. The sequencing for plane flips, cursor updates, scaler programming, color LUT programming, memory-power transitions, and performance-counter reads lives in those modules, not in this generated header.
5. DMUB DCN301 service code includes the same offset and mask headers, although this particular range is mostly display-pipe register metadata rather than the DMCUB register family used by `dmub_dcn301.c`.

The macros do not encode ordering. Consumers must still enable clocks, ungate memories, program double-buffered state in the correct phase, handle read-only/status/ack fields correctly, and synchronize register writes with modeset or flip timing.

## State And Persistence Behavior

The chunk stores no software state. It describes MMIO-backed hardware state whose persistence is defined by the display engine. Register contents generally persist until a modeset reprograms the pipe, a block is reset or power-gated, a suspend/resume path restores state, or a full GPU reset clears the engine.

Hardware state addressed by this range includes:

- Plane-fetch state for HUBP2 and HUBP3: surface format, address configuration, tiling, luma/chroma viewports, surface pitch, primary/secondary addresses, metadata addresses, VMID, VM aperture/TLB control, DMDATA addressing, flip control, flip interrupt status, current/in-use surface tracking, and prefetch/nominal/vblank/flip timing parameters.
- Request and return-path state: HUBPREQ TTU/QoS delivery controls, per-line delivery, DRQ limits, cursor timing parameters, memory-power controls/status, HUBPRET read-line tracking, and return-path interrupt/status state.
- Cursor state for pipe instances 2 and 3: cursor enable/mode, surface address, dimensions, position, hot spot, stereo mode, memory-power state, dynamic metadata address/control/QoS/status, and software DMDATA register access.
- DPP formatter state: pixel format, alpha-plane enable, format expansion, fixed-point bias/scale conversion, color-key ranges, alpha 2-bit LUT, pre-dealpha/re-alpha, pre-CSC matrices, and formatter cursor colors/scale/bias.
- DSCL scaler state: filter taps and coefficient RAM, scaler mode, horizontal/vertical ratios and initial phases for luma/chroma, line-buffer format and memory power, recout/MPC sizing, overscan, autocalculated parameters, blanking, and output-buffer power.
- CM color-management state: post-CSC, gamut-remap matrices, gamma-correction and blend-gamma LUTs, PWL region tables, shaper LUTs, HDR multiplier, dealpha, coefficient formats, 3D LUT state for CM0/CM1, memory-power controls/status, and test/debug index/data.
- Perfmon state: control bits, counter state, current-value registers, and high/low counter storage for the visible HUBP and DPP perfmon blocks.

Because the constants are address metadata, a wrong offset or base index can redirect writes into another register block. That can leave persistent hardware state corrupted until the affected pipe, DPP, HUBP, or full display engine is reinitialized.

## Dependencies And Integration Points

This chunk is tightly coupled to generated and hand-written display code:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h` supplies field shifts and masks for the register offsets in this file.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/vangogh_ip_offset.h` supplies DCN base segment macros used by DCN301 code.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn301/dcn301_resource.c` includes this header and builds resource register tables. Its `BASE`, `SR`, `SRI`, and array-initializer macros are the direct consumers of the `mm...` and `_BASE_IDX` naming contract.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn30/dcn30_dpp.h` defines `DPP_REG_LIST_DCN30_COMMON()` and `DPP_REG_LIST_DCN30()`, which consume the `DPP_TOP`, `CNVC_CFG`, `CNVC_CUR`, `DSCL`, and `CM` families visible here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn30/dcn30_dpp.c`, `dcn10_dpp_dscl.c`, and `dcn10_dpp_cm.c` use the populated register tables to program formatter, scaler, gamma, gamut, shaper, and LUT behavior.
- HUBP register-list macros used by DCN301 resource construction consume the `HUBP2`, `HUBP3`, `HUBPREQ2`, `HUBPREQ3`, `HUBPRET2`, `HUBPRET3`, `CURSOR0_2`, and `CURSOR0_3` symbols from this range.
- IRQ services across DCN generations map HUBP flip source IDs, including HUBP2 and HUBP3, onto DAL IRQ sources; this chunk supplies the corresponding per-pipe flip-interrupt offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn301.c` includes the DCN301 offset and mask headers for DMUB register tables; adjacent chunks provide more of the DMUB-specific offsets.

The repeated instance layout is an important integration point. `dcn301_resource.c` constructs arrays for four DPPs and four HUBPs; instance 2 and 3 symbols must follow the same spelling and layout as earlier instances or table construction either fails at compile time or silently targets the wrong hardware block.

## Risks And Edge Cases

- Offset drift is the central risk. The constants are untyped compile-time numbers; a wrong value can compile cleanly while driving the wrong MMIO register.
- `_BASE_IDX` drift is equally dangerous. Every visible register belongs to base segment 2 in this chunk. A correct offset paired with an incorrect base selector computes the wrong absolute address.
- Chunk boundaries are artificial. The first line is only a `_BASE_IDX` from the previous HUBP2 register, and the final line stops inside CM2 shaper RAMA programming. A final per-file report must merge adjacent chunks before making whole-file claims.
- Instance-copy mistakes are easy to miss. HUBP2/HUBPREQ2/HUBPRET2/CURSOR0_2 and HUBP3/HUBPREQ3/HUBPRET3/CURSOR0_3 are nearly identical families. A single typo may only fail on the third or fourth pipe, multi-display modes, or specific plane assignments.
- Plane-address and VM registers are high impact. Bad HUBPREQ surface, metadata, aperture, or TLB offsets can cause blank scanout, stale flips, DCC/metadata corruption, VM faults, or unintended memory accesses.
- Flip and interrupt offsets are timing-sensitive. Incorrect flip control or surface-flip-interrupt addresses can produce missed page-flip completion, stuck interrupts, incorrect vblank synchronization, or hangs in atomic commit paths.
- Scaler and formatter errors may be format-specific. DSCL and CNVC offset mistakes can appear only for scaling, YUV/chroma formats, cursor blending, alpha planes, color-keying, or high-bit-depth paths.
- Color-management registers are stateful and table-heavy. Gamcor, blend gamma, shaper, and 3D LUT programming uses index/data and region registers; an address mismatch can corrupt color output without obvious kernel errors.
- Memory-power controls can fail by sequencing. HUBPREQ/HUBPRET/CURSOR/DSCL/CM memory-power control and status registers must be read or written only when the block is clocked and expected to respond.
- Performance counter registers may be read-only, sticky, or clear-on-write depending on fields. This header cannot express those side effects; functional perfmon code must use the companion mask semantics and hardware programming guide assumptions.

## Test Signals

Useful validation for this chunk combines generated-header consistency checks with real display behavior:

- Build AMDGPU display code with DCN301 support enabled. Missing, misspelled, or renamed macros should surface in `dcn301_resource.c`, DPP/HUBP register-list expansion, DMUB register-table construction, and related display modules.
- Mechanically verify that every complete non-`_BASE_IDX` macro in lines 2695-5217 has a matching `_BASE_IDX` macro, accounting for the first line being a carry-over base-index macro from the previous chunk.
- Verify that every visible `_BASE_IDX` value remains `2`.
- Diff the range against AMD's generated DCN 3.0.1 register database and nearby compatible headers such as `dcn_3_0_0_offset.h`, `dcn_3_0_2_offset.h`, and `dcn_3_0_3_offset.h` to catch unintended offset or instance-layout drift.
- Exercise modesets that allocate HUBP/DPP instances 2 and 3: multi-monitor, multi-plane, cursor, scaling, YUV/chroma, DCC/metadata, page-flip, and suspend/resume scenarios.
- Validate flip completion and interrupt handling for HUBP2 and HUBP3, including atomic commits, cursor-only updates, vblank synchronization, and recovery from disabled/re-enabled pipes.
- Run scaler validation for DPP0, DPP1, and DPP2: luma/chroma scaling, 2-tap and multi-tap filters, coefficient RAM programming, overscan, recout/MPC sizing, and bypass paths.
- Run color-management validation for CM0 and CM1, and partial CM2 coverage visible here: post-CSC, gamut remap, gamma correction, blend gamma, shaper LUTs, HDR multiplier, 3D LUT, dealpha, and power-gated memory restore.
- Watch kernel logs and display diagnostics for VM faults, underflow, stale flips, blank outputs, incorrect cursor rendering, scaling artifacts, color banding, broken HDR/color transforms, stuck interrupts, and resume failures.
- Perfmon validation should confirm HUBP2/HUBP3/DPP0/DPP1 counter control and readback operate on the intended block and do not alias adjacent perfmon instances.

## Cross-Chunk Notes

Adjacent chunks are required for a complete `dcn_3_0_1_offset.h` file report. The previous chunk owns the start of HUBP2 and the register paired with this chunk's opening `_BASE_IDX`; the next chunk must finish CM2 after `CM_SHAPER_RAMA_REGION_10_11` and cover the remaining DCN301 register-offset namespace. This chunk should be merged later as one source-aligned contribution, not treated as a standalone final per-file report.

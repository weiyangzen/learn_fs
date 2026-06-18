# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 10072-12607

## Purpose

This chunk is a middle slice of AMD's generated DCN 4.1.0 shift/mask register-field header. It has no executable C logic; it exports preprocessor constants that describe bit positions and bit masks for display-core MMIO fields. Driver code combines these constants with the matching DCN 4.1.0 offset header and register-list macros, then uses AMD display register helpers to pack, update, and read individual fields.

The requested range contains 2,109 `#define` entries: 1,050 `__SHIFT` macros and 1,059 `_MASK` macros. The chunk starts in the middle of the `HUBP3_DCHUBP_CNTL` field list, so only tail masks for timeout, TTU, outstanding-request, and underflow fields are visible there. It ends on the `//CNVC_CFG1_PRE_DEGAM` section marker before that register's field definitions, so the next chunk must cover the actual `CNVC_CFG1_PRE_DEGAM` shift/mask pairs.

Although this repository path is under a local `ceph-client` mirror, the source content is AMDGPU display hardware metadata, not Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocation paths, or direct MMIO operations in this slice. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the field bit offset.
- `<REGISTER>__<FIELD>_MASK`: the field isolation mask, normally used with the shift by `REG_GET`, `REG_SET`, `REG_UPDATE`, `TF_SF`, `TF2_SF`, and related AMD display register-table helpers.

The main register families in this range are:

- `HUBP3_*`: HUBP clock gating/status, virtual memory page configuration, MALL selection and sub-viewport metadata, MALL status, MCache ID assignment, and DCFCLK/DPPCLK measurement-window control.
- `HUBPREQ3_*`: hub request-side surface programming for pipe 3, including luma/chroma pitch, VMID, primary/secondary surface addresses, stereo/surface flip controls, flip interrupts, in-use address snapshots, expansion mode, TTU/QoS watermarks, VM aperture/TLB control, vblank/flip/nominal request timing, per-line delivery, cursor delivery, memory power control, UCLK p-state forcing, and live status registers.
- `HUBPRET3_*`: hub return-side controls for DET buffer/crossbar selection, DMROB/PIXCDC memory power, read-line windows, vblank/read-line interrupts, current read-line value, and read-line status.
- `CURSOR0_3_*`: cursor plane 0 for pipe 3, covering enable/mode/pitch/TMZ, cursor surface address, size, position, hot spot, stereo offsets, destination offset, cursor memory power, Display Metadata (`DMDATA`) address/control/QoS/status/software data, and HUBP 3D LUT address/delivery parameters.
- `CNVC_CFG0_*`: DPP0 input/color format conversion setup, including pixel format, alpha-plane enable, format expansion/conversion, CNVC bypass and alignment, clamping, RGB crossbar routing, FP bias/scale, color/luma keying, alpha LUT, pre-dealpha, pre-realfa, pre-CSC matrices A/B, coefficient format, and the start of pre-degamma control.
- `CM_CUR0_*`: cursor color-management controls for cursor 0, including cursor mode/enable/expansion, two cursor colors, FP bias/scale fields, and A/B cursor matrix mode and coefficients.
- `DSCL0_*`: DPP0 scaler and line-buffer controls, including coefficient RAM indexing/data, scaler mode and tap counts, scale ratios and initial phases for luma/chroma, overscan, OTG blank windows, recout/MPC sizes, line-buffer format/memory partitioning, scaler and OBUF memory power, EASF horizontal/vertical sharpening/ring-estimator controls, bias-function piecewise-linear segments, and iSharp controls/LUT/memory power.
- `CM0_*`: DPP0 color-management controls, including bypass/update state, post-CSC mode and A/B matrices, bias, gamma-correction control, LUT index/data/control, RAMA/RAMB gamma region tables, HDR multiplier, gamma memory power, dealpha, coefficient format, and test/debug index/data.
- `DPP_TOP0_*`: top-level DPP0 clock-gating and clock-enable controls, soft reset bits for CNVC/DSCL/CM/OBUF, DPP CRC values/control, and host read-rate control.
- `CNVC_CFG1_*`: beginning of the DPP1 CNVC configuration block. This chunk repeats the DPP0 CNVC-style fields through coefficient format and then stops at the `PRE_DEGAM` marker.

Several families are replicated instances. `CNVC_CFG0` and `CNVC_CFG1` share the same field layout for the part visible here. `CM0` has RAMA and RAMB copies of the gamma region registers. `DSCL0` has repeated horizontal/vertical and luma/chroma forms, plus repeated PWL segment registers.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by AMDGPU display code that includes generated offset and shift/mask headers, creates per-ASIC register tables, and passes those tables to hardware block constructors. In the visible integration points, DPP code such as `display/dc/dpp/dcn401/dcn401_dpp.h` references many of these fields through `TF_SF(...)` and `TF2_SF(...)` entries for CNVC, CM, cursor color management, DSCL, and DPP top registers.

The effective runtime flow is:

1. DCN 4.1.0 display code includes the generated offset header and this shift/mask header.
2. Register-list macros token-paste symbolic register and field names into offset, shift, and mask table initializers.
3. DCN resource creation and block constructors attach those tables to HUBP, cursor, DPP/scaler, color-management, IRQ, and related display objects.
4. Modeset, plane update, cursor update, color pipeline, flip, watermark, p-state, interrupt, and diagnostics paths call register helpers to read or update fields.
5. The helpers use these constants to preserve unrelated bits while changing a single field or to decode a hardware status field.

The macros do not encode ordering. Consumers must still program addresses before enable bits, stage pending color/scaler updates at the correct time, coordinate flip/vblank interrupts, respect power/clock gating, and poll or acknowledge status fields according to hardware semantics.

## State And Persistence Behavior

The chunk stores no software state and persists nothing on disk. It describes hardware state held in DCN 4.1.0 registers:

- HUBP/HUBPREQ state includes current surface addresses, pending and active flip state, VM/TLB controls, timing-derived prefetch/vblank/flip/nominal request parameters, underflow/timeout status, MALL usage, memory power states, and p-state allow/force indicators.
- HUBPRET state includes return-path buffer configuration, crossbar routing, memory-power state, read-line windows, live read-line snapshots, vblank/read-line interrupt flags, and status bits.
- Cursor state includes cursor image address, size, position, hot spot, stereo offset, memory power, TMZ protection bits, Display Metadata fetch or software payload state, QoS, underflow flags, and 3D LUT delivery parameters.
- CNVC and CM state includes pixel format, alpha/keying/pre-CSC/post-CSC/dealpha/gamma/HDR transform configuration, update-pending/current-mode flags, LUT address/data ports, RAMA/RAMB gamma region tables, and debug readback selectors.
- DSCL state includes scaler ratios, taps, coefficients, init phases, overscan windows, output sizes, line-buffer partitioning, EASF/iSharp enhancement parameters, LUT contents, and scaler/OBUF memory power states.
- DPP top state includes clock-enable/gating controls, soft-reset state, CRC capture/control, and host-read throttling.

Persistence is hardware-defined. Configuration fields generally last until the display pipe is reprogrammed, reset, power-gated, suspended/resumed, or ASIC-reset. Status, interrupt, update-pending, underflow, timeout, memory-state, and readback fields can be read-only, sticky, write-one-to-clear, self-clearing, or valid only while clocks and power domains are active. This generated header does not distinguish those access semantics.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 4.1.0 register database and must stay synchronized with the companion register-offset header for actual MMIO addresses. It also relies on the AMD display register-helper convention that field names can be token-pasted into `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`.

Important integration points include:

- DPP/DCN 4.x headers such as `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn401/dcn401_dpp.h`, where `TF_SF` and `TF2_SF` entries consume `CNVC_CFG0`, `CM0`, `CM_CUR0`, `DSCL0`, and `DPP_TOP0` fields visible in this slice.
- HUBP, plane, flip, cursor, and IRQ service code that uses the `HUBP3`, `HUBPREQ3`, `HUBPRET3`, and `CURSOR0_3` field constants indirectly through generated register tables and source IDs such as the pipe 3 flip interrupt.
- Color-management and scaling paths that program pre-CSC, post-CSC, gamma-correction, HDR multiplier, scaler taps, scale ratios, EASF, and iSharp fields.
- Power-management paths that use memory-power force/disable/state fields for HUBPREQ, HUBPRET, cursor, DSCL, OBUF, CM gamma memory, and iSharp delta LUT memory.
- Diagnostics and validation paths that read HUBP MALL status, HUBPREQ status registers, read-line status, DPP CRC registers, debug index/data, and clock/status bits.

The source slice is generated metadata, so the strongest dependency is not another C function but the contract between generated register names, offset definitions, shift/mask definitions, and the table-building macros that instantiate ASIC-specific register accessors.

## Risks And Edge Cases

- The values are untyped preprocessor constants. A wrong mask or shift can compile cleanly while causing writes to adjacent hardware fields, bad readback decoding, missed interrupts, or silent display corruption.
- The file is generated. Manual edits can diverge from AMD's authoritative register database, the matching offset header, firmware expectations, or silicon documentation.
- Chunk boundaries are artificial. The opening `HUBP3_DCHUBP_CNTL` register is incomplete in this slice, and `CNVC_CFG1_PRE_DEGAM` is only a marker with no visible field definitions here.
- Repeated register families can hide instance-specific errors. `CNVC_CFG0` working does not prove `CNVC_CFG1` is correct; RAMA and RAMB gamma tables must both match hardware; repeated DSCL PWL segments can have subtly different terminal fields.
- Status, interrupt, clear, and update-pending fields are side-effect-sensitive. Confusing mask/type/clear/status bits can cause stuck flip interrupts, missed vblank/read-line events, stale pending states, or interrupt storms.
- Address and timing fields are high impact. Bad surface address, high-address, VMID, VM aperture, pitch, prefetch, vblank, flip, per-line delivery, or p-state timing masks can produce page faults, underflows, hangs, or unstable display during memory-clock transitions.
- Color/scaler fields are user-visible. Wrong CNVC, CSC, gamma, scaler coefficient, EASF, or iSharp masks can produce channel swaps, incorrect alpha, bad HDR/SDR transforms, ringing, blur, clipping, banding, or CRC mismatches.
- Power fields require sequencing. Forcing or disabling memory power while a pipe, scaler, cursor, OBUF, or gamma LUT is active can corrupt state or make status polling unreliable.

## Test Signals

Useful validation for this chunk combines generated-header checks with display behavior on DCN 4.1.0 hardware:

- Build AMDGPU display support for DCN 4.1.0. Missing or renamed macros should fail in register-table declarations for DPP, HUBP, cursor, color-management, scaler, IRQ, or diagnostic paths.
- Mechanically compare every field in lines 10072-12607 against AMD's generated DCN 4.1.0 register database and the matching offset header; allow for the known incomplete `HUBP3_DCHUBP_CNTL` and `CNVC_CFG1_PRE_DEGAM` boundaries.
- Verify shift/mask consistency: each full field in the slice should have a mask covering the shifted width, and expected one-bit fields should have single-bit masks.
- Exercise pipe 3 plane flips, page flips, vblank/read-line interrupts, surface address updates, stereo address selection, cursor movement, cursor hot spots, cursor metadata, and suspend/resume.
- Run modesets and plane updates across linear/tiled, luma/chroma, scaling, rotation/mirroring, alpha, color-keying, HDR, degamma/gamma, and CSC cases; watch for underflows, hangs, and visible color/scaling defects.
- Validate MALL/sub-viewport and p-state behavior under static screen, SubVP, memory-clock changes, and low-power transitions by checking status bits and absence of underflow/timeout logs.
- Use CRC/debug paths where available: DPP CRC values should be stable for known test patterns, and debug/readback fields should match programmed CNVC/CM/DSCL state.
- Check kernel logs and display diagnostics for HUBP underflow, timeout, page faults, flip interrupt loss, stuck update-pending bits, bad memory-power states, and resume-only failures.

## Cross-Chunk Notes

This is one chunk of `dcn_4_1_0_sh_mask.h`. Earlier chunks contain the beginning of the HUBP3 register family and the opening `HUBP3_DCHUBP_CNTL` shifts/masks. Later chunks continue from `CNVC_CFG1_PRE_DEGAM` into the rest of DPP1 and subsequent DCN 4.1.0 register blocks. The final per-file research document should merge this report with neighboring chunks before making whole-file claims about all DCN 4.1.0 register fields or all replicated pipe/DPP instances.

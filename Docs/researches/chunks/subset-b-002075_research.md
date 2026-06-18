# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h lines 42092-44308

## Purpose

This chunk is generated AMD DCN 3.5.0 register-field metadata. It contains only C preprocessor constants for field bit positions and masks; it does not contain executable code, structs, enums, includes, or storage. Consumers combine these `__SHIFT` and `_MASK` constants with the matching DCN 3.5.0 register-offset header to build typed-looking register access tables for AMDGPU Display Core.

The 2,217 lines in this range contain 2,217 `#define` entries: 1,107 shift macros and 1,114 mask macros. The chunk begins in the middle of `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL6` mask definitions, continues through generic secondary data packet control groups for DisplayPort stream encoder 3, covers four `MPCC` blender instances, and then covers most of the `MPCC_OGAM` output gamma and gamut-remap register fields for instances 0 through 3. The final line stops inside `MPCC_OGAM3_MPCC_OGAM_RAMB_REGION_24_25`, so the matching masks for region 24 segment count and region 25 fields are outside this chunk.

Although the repository path is under a local `ceph-client` source tree, this file is AMDGPU display hardware metadata, not Ceph or distributed filesystem logic.

## Important APIs, Types, And Macros

There are no functions or types in this chunk. The exported interface is the macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for packing or extracting a field.
- `<REGISTER>__<FIELD>_MASK` gives the bit mask used by register helpers during read-modify-write or decode operations.

The main macro families are:

- `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL6` through `CONTROL14`: generic secondary-data-packet controls for DP stream encoder 3. Each control group describes enable bits for video-continuous and idle-continuous transmission, one-shot trigger and trigger position, double buffering, payload size, start-of-frame reference, missed-deadline and pending status, double-buffer pending status, and a 16-bit transmission line number field.
- `MPCC0_MPCC_*` through `MPCC3_MPCC_*`: per-MPCC blender/combiner fields. Each instance has top and bottom DPP source selection, OPP binding, blend control, stereo/multi-frame control, update-lock selection and status, top and bottom gain controls, background color channels, OGAM memory power controls, and idle/busy/disabled status.
- `MPCC_OGAM0_*` through `MPCC_OGAM3_*`: output gamma and gamut-remap fields attached to MPCC instances. These include `MPCC_OGAM_CONTROL`, LUT index/data/control, RAM A and RAM B piecewise-linear region descriptors, per-channel start/end/base/slope/offset fields, and gamut-remap coefficient format/mode plus matrix coefficient fields.
- `MPCC_OGAM*_MPC_GAMUT_REMAP_*_{A,B}`: A/B coefficient banks for MPCC gamut remap. Coefficients are paired in 32-bit registers, typically with one 16-bit coefficient in low bits and the other in high bits.

Several register layouts repeat mechanically across instances. The MPCC blender group is repeated for MPCC0 through MPCC3. The OGAM group is repeated for `MPCC_OGAM0` through `MPCC_OGAM3`, with the same LUT, RAMA/RAMB, and gamut-remap field shapes until the artificial chunk boundary cuts off part of `MPCC_OGAM3` RAMB region definitions.

## Control Flow

This header has no runtime control flow. Runtime behavior emerges in AMD display code that includes the generated offset and shift/mask headers:

1. DCN 3.5 display code includes `dcn_3_5_0_offset.h` and `dcn_3_5_0_sh_mask.h`.
2. Register-list macros such as `SRII`, `SRI`, `SF`, and related token-pasting helpers construct per-block register, shift, and mask tables.
3. MPC, MPCC, stream encoder, resource, IRQ, and DMUB objects store those tables.
4. Runtime paths call helpers such as `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, `REG_GET`, and `REG_WAIT`; those helpers use these shift/mask constants to isolate the intended hardware fields.

The sequencing is not encoded here. Consumers must still order stream encoder SDP updates, MPCC connection/disconnection, blender programming, update locking, OGAM memory power state changes, LUT writes, gamut-remap coefficient updates, and modeset commits according to the hardware programming model.

## State And Persistence Behavior

This chunk persists no software state. It describes hardware state in DCN 3.5.0 display registers:

- DP GSP control state for stream encoder 3 secondary data packet scheduling, including continuous or one-shot send modes, double-buffer status, trigger-pending status, and target transmission line.
- MPCC routing state for selecting top/bottom DPP inputs and associating an MPCC with an output pixel processor.
- MPCC blend state for blend mode, alpha blend mode, premultiplied alpha, active-overlap-only blending, background bits-per-component, bottom gain mode, global alpha, global gain, top gain, bottom gain inside/outside, and background RGB/YCbCr values.
- MPCC stereo or surface-mode state through `MPCC_SM_CONTROL`, including enable, mode, frame/field alternation, forced next-frame or top polarity, and current frame polarity.
- MPCC update-lock state and readback status, used to coordinate atomic or double-buffered programming.
- MPCC OGAM memory power state through force, disable, low-power mode, and state fields.
- OGAM LUT state: active mode, selected RAM bank, PWL disable, current mode/select readback, LUT index, LUT data, color write mask, read color selection, host selection, and LUT configuration mode.
- OGAM RAMA/RAMB piecewise-linear region state: per-channel start/end/base/slope/offset values and region-pair fields for LUT offsets plus number-of-segments encodings.
- MPCC gamut-remap state: coefficient format, selected/current mode, and A/B bank matrix coefficients.

Hardware persistence is power-domain and modeset dependent. Register values generally survive until the display block is reprogrammed, gated, reset, suspended/resumed, or replaced by an atomic commit. Status fields such as busy/idle/disabled, current OGAM selection, update-lock status, pending flags, and double-buffer status reflect live hardware state. The generated mask header does not describe read-only, sticky, self-clearing, write-one-to-clear, or double-buffer semantics; those rules come from silicon documentation and the consuming driver code.

## Dependencies And Integration Points

This chunk must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_offset.h`, which supplies the matching MMIO register offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn35.c`, which includes this header for DCN 3.5 DMUB register definitions.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn35/irq_service_dcn35.c`, another direct DCN 3.5 include site.
- MPC register table definitions in `display/dc/mpc/dcn10`, `dcn20`, `dcn30`, and `dcn32`, where `MPCC*_MPCC_*` and `MPCC_OGAM*_...` fields are mapped into common MPC structures.
- DCN 3.5 resource construction, which reuses those MPC structures to expose MPCC composition and output color programming to the rest of Display Core.
- Higher-level display color code that selects MPCC output gamma, PWL LUT banks, gamut-remap mode, and coefficient format through `dc_hw_types.h` concepts such as `MPCC_OGAM_GAMUT_REMAP`, `CM_GAMUT_REMAP_MODE_*`, and `CM_GAMUT_REMAP_COEF_FORMAT_*`.
- DisplayPort stream encoder code paths that program generic secondary data packets, where the `DP_SYM32_ENC3_*_GSP_CONTROL*` constants define fields for stream encoder instance 3.

The chunk therefore sits at the boundary between generated hardware descriptions and runtime display features: multi-plane composition, blending, update locking, output gamma LUT programming, gamut conversion, power management of OGAM memories, and DP SDP packet scheduling.

## Risks And Edge Cases

- These values are untyped preprocessor constants. A wrong shift or mask can compile cleanly while writing the wrong MMIO bits.
- The file is generated. Manual edits can diverge from AMD's register database, the companion offset header, firmware expectations, and silicon documentation.
- Repetition across MPCC and OGAM instances makes instance-local generator errors easy to miss. MPCC0 working does not prove MPCC1 through MPCC3 have correct masks.
- The range starts and ends inside register families. `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL6` has only trailing masks in this chunk, and `MPCC_OGAM3_MPCC_OGAM_RAMB_REGION_24_25` continues after line 44308.
- Field names ending in `_MASK_MASK`, such as `MPCC_OGAM_LUT_WRITE_COLOR_MASK_MASK`, are valid generated names for a field whose hardware name includes `MASK`. Consumers must not simplify or rename them by hand.
- MPCC blend and routing fields affect visible composition. Incorrect source selection, OPP ID, blend mode, alpha, gain, or background masks can cause black planes, wrong plane ordering, incorrect transparency, or color shifts.
- Update-lock and busy/idle/status fields are sequencing-sensitive. Misinterpreting status masks can lead to timeouts, programming while a block is busy, or stale register snapshots.
- OGAM LUT and PWL region fields are precision-sensitive. Wrong 18-bit data masks, 9-bit LUT offsets, 3-bit segment counts, 18/19-bit base/offset masks, or channel-specific fields can introduce banding, clipping, non-monotonic curves, or channel swaps.
- RAM A/B and current-select fields implement banked updates. Incorrect masks can update the displayed bank instead of the inactive bank, causing visual tearing or partially programmed gamma/gamut state.
- OGAM memory power fields interact with color programming. Programming LUT or remap state while memory is forced off or in the wrong low-power state can drop writes or leave stale color state after resume.
- DP GSP trigger and pending fields are timing-sensitive. A wrong transmission-line mask or double-buffer flag can cause generic SDP packets to be sent on the wrong line, missed, duplicated, or left pending.

## Test Signals

Useful validation is mostly build-time macro coverage plus hardware display behavior:

- Build AMDGPU Display Core with DCN 3.5 support enabled. Missing or renamed macros should fail where DCN35 DMUB, IRQ, resource, stream encoder, or MPC tables reference this header.
- Mechanically check this exact line range for expected shift/mask pairs, allowing boundary exceptions for the partial `DP_SYM32_ENC3...CONTROL6` and partial `MPCC_OGAM3...RAMB_REGION_24_25` groups.
- Diff the chunk against AMD's authoritative DCN 3.5.0 register database and adjacent generated DCN headers where the same MPCC/OGAM register families are expected to match.
- Exercise multi-plane composition with alpha, global alpha/gain, bottom gain, background colors, stereo/surface-mode variants, and plane connect/disconnect. Watch for wrong plane order, unexpected transparency, stale backgrounds, and MPCC idle/busy wait failures.
- Exercise output gamma LUT and gamut-remap programming through KMS color-management paths, including degamma/gamma changes, color transforms, HDR/SDR transitions, and bank switching. Watch for banding, wrong colors, flicker during atomic commits, and incorrect readback/current-mode state.
- Run suspend/resume, runtime power management, display hotplug, and modeset loops while changing gamma/gamut state. Look for lost OGAM programming, memory power state mistakes, or resume-only color corruption.
- Validate DP secondary-data-packet behavior on the stream encoder instance corresponding to `DP_SYM32_ENC3`, including one-shot and continuous packet sends, double buffering, trigger line selection, and pending/deadline status.

## Cross-Chunk Notes

This is a middle chunk of `dcn_3_5_0_sh_mask.h`. Earlier chunks contain the first parts of the stream encoder and display register namespace, including the start of `DP_SYM32_ENC3` GSP control groups. Later chunks continue the remaining `MPCC_OGAM3` RAMB region fields and then proceed into later DCN 3.5.0 register families. The final per-file research should merge adjacent chunks before making whole-file claims about all MPCC, OGAM, stream encoder, or color-management registers.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 56611-59133

## Scope

This chunk is a generated DCN 3.0.0 register field-layout slice. It contains only preprocessor constants for hardware register fields: `<REGISTER>__<FIELD>__SHIFT` bit positions and `<REGISTER>__<FIELD>_MASK` bit masks. There are no functions, structs, enums, variables, includes, locks, allocation paths, or runtime branches in this range.

The requested range contains 2,097 `#define` entries: 1,047 `__SHIFT` constants and 1,050 `_MASK` constants. The imbalance is caused by the artificial chunk boundary: the range starts in the middle of the `MPCC_OGAM3_MPCC_OGAM_RAMA_REGION_28_29` field group and ends at `MPC_RMU0_SHAPER_RAMB_END_CNTL_B`, before the matching masks and remaining RMU RAMB region definitions continue in the next chunk.

Although the source path is under a local `ceph-client` mirror, this header is AMDGPU display-controller metadata, not distributed filesystem code.

## Purpose

This header slice gives AMD DC display code the bit-level definitions needed to program the DCN 3.0 Multi-Plane Compositor (MPC), MPCC output gamma blocks, output color-space conversion, CRC/debug/status paths, and the beginning of RMU shaper programming. Driver code combines these constants with matching register offsets from `dcn_3_0_0_offset.h` through field helper macros such as `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.

Major hardware areas covered by this chunk:

- Tail of `MPCC_OGAM3` output gamma RAM A/RAM B region definitions and gamut remap coefficients.
- Complete `MPCC_OGAM4` and `MPCC_OGAM5` output gamma blocks, including LUT access, RAM A/RAM B piecewise-linear region setup, offsets, starts, ends, slopes, mode/current-state fields, and gamut remap matrices.
- MPC global configuration: clock gating, MPCC/SFR/SFT/MPC soft resets, CRC selection/result fields, bypass background color, host read rate, DPP/OPP/MPCC/DWB pending status, vupdate lock registers, and DWB muxing.
- MPC output-combiner color path for outputs 0 through 5: output mux, rate-control/error fields, denormalization clamps, output CSC coefficient format, CSC modes, and CSC matrix coefficient registers.
- Beginning of MPC RMU support: RMU mux/status, memory power controls for RMU0 through RMU2, RMU0 shaper mode, offset/scale/LUT access, LUT write mask, and the start of RMU0 shaper RAM A/RAM B PWL region programming.

## Important APIs, Types, And Constants

There are no callable APIs. The exported interface is the generated macro namespace:

- `REGISTER__FIELD__SHIFT`: the bit position for a field inside a DCN 3.0 register.
- `REGISTER__FIELD_MASK`: the field mask used to isolate or compose that field.
- Section comments such as `//MPCC_OGAM4_MPCC_OGAM_CONTROL` and address-block comments such as `// addressBlock: dce_dc_mpc_mpc_cfg_dispdec` group related constants by hardware register block.

Important macro families in this slice:

- `MPCC_OGAM[3-5]_MPCC_OGAM_RAMA_REGION_*` and `MPCC_OGAM[3-5]_MPCC_OGAM_RAMB_REGION_*`: LUT offset and segment-count fields for paired PWL regions 0 through 33. Each paired region normally has fields for even/odd region LUT offsets and segment counts.
- `MPCC_OGAM[3-5]_MPCC_OGAM_RAMA/RAMB_START_*`, `END_*`, and `OFFSET_*`: per-channel B/G/R start, start segment, start slope, start base, end base, end value, end slope, and offset fields for output gamma RAM interpolation.
- `MPCC_OGAM[4-5]_MPCC_OGAM_CONTROL`, `LUT_INDEX`, `LUT_DATA`, and `LUT_CONTROL`: output gamma mode/select/current-state, LUT host/read/write selection, color write masks, index, and 30-bit LUT payload access fields.
- `MPCC_OGAM[3-5]_MPCC_GAMUT_REMAP_*` and `MPC_GAMUT_REMAP_C*_C*_[AB]`: coefficient format/mode/current-state fields and packed signed coefficient fields for MPCC-local gamut remap matrices.
- `MPC_CLOCK_CONTROL`, `MPC_SOFT_RESET`, `MPC_CRC_*`, `MPC_BYPASS_BG_*`, `MPC_DPP_PENDING_STATUS`, and `MPC_PENDING_STATUS_MISC`: global MPC clock, reset, CRC capture, background, and pending-update status fields.
- `ADR_CFG_CUR_VUPDATE_LOCK_SET[0-5]`, `ADR_CFG_VUPDATE_LOCK_SET[0-5]`, `ADR_VUPDATE_LOCK_SET[0-5]`, `CFG_VUPDATE_LOCK_SET[0-5]`, and `CUR_VUPDATE_LOCK_SET[0-5]`: per-set vupdate lock controls used to coordinate atomic address/config/current updates.
- `MPC_OUT[0-5]_MUX`, `MPC_OUT[0-5]_DENORM_*`, `MPC_OUT_CSC_COEF_FORMAT`, and `MPC_OUT[0-5]_CSC_*`: output pipe selection, rate/flow control, denormalization clamp limits, output CSC mode, and packed CSC coefficient fields.
- `MPC_RMU_CONTROL`, `MPC_RMU_MEM_PWR_CTRL`, and `MPC_RMU0_SHAPER_*`: RMU mux/status, memory power controls, shaper mode/current state, offsets, scales, LUT index/data/write-mask, and first PWL region descriptors.

## Control Flow

This chunk has no runtime control flow. Its behavior is compile-time token expansion:

1. DCN 3.0 resource, MPC, DMUB, IRQ, GPIO, and clock code includes `dcn_3_0_0_sh_mask.h` with the matching offset header.
2. Register-table macros paste register and field tokens into names such as `MPCC_OGAM4_MPCC_OGAM_CONTROL__MPCC_OGAM_MODE_MASK` or `MPC_OUT2_CSC_C11_C12_A__MPC_OCSC_C11_A__SHIFT`.
3. Runtime code uses the generated field metadata through MMIO helpers to read, write, update, and poll the actual hardware registers.

The programming order is not encoded here. Consumers must still sequence MPCC disconnect/connect, LUT bank selection, gamma RAM programming, gamut remap enablement, output CSC update, CRC capture, vupdate locking, reset, memory power transitions, and RMU shaper writes according to the display hardware programming model.

## State And Persistence Behavior

The header stores no software state and persists nothing. It describes stateful MMIO fields owned by DCN hardware:

- MPCC OGAM fields hold output gamma mode, bank selection, LUT contents, interpolation region boundaries, slopes, bases, offsets, and gamut remap matrices. These affect color output until overwritten, power gated, reset, or replaced during a modeset/color-management update.
- MPC output fields hold the selected MPCC feeding each OPP, rate/flow-control configuration, denormalization clamp ranges, CSC mode, and CSC coefficients for each of six outputs.
- CRC fields control capture source, update locking, one-shot or continuous capture, stereo/interlace behavior, and expose CRC result channels.
- Pending-status and vupdate-lock fields expose or coordinate double-buffered update state across DPP, OPP, MPCC, DWB, address, configuration, and current parameters.
- Soft-reset and clock-gating fields can reset or gate compositor subblocks. Their effects are hardware-visible and may persist until explicitly changed or reset by the device.
- RMU memory power and shaper fields configure muxing, memory low-power behavior, LUT access, scaling, offsets, and PWL region layout for the RMU0 shaper path.

The macros do not distinguish read-only status, write-one-to-clear, sticky status, self-clearing command bits, or ordinary read/write controls. That semantic burden remains with the consuming driver code and hardware specification.

## Dependencies And Integration Points

This chunk depends on generated-name compatibility with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h` for register offsets.
- DC register helper infrastructure that builds field metadata from `FD_MASK`, `FD_SHIFT`, `SF`, `REG_GET`, `REG_SET`, `REG_UPDATE`, and indexed register-table macros.
- SOC/DCN base-address headers that map generated offsets to the correct MMIO segment.

Observed integration points in this tree include:

- `drivers/gpu/drm/amd/display/dc/resource/dcn30/dcn30_resource.c`, which includes this generated header to build DCN 3.0 resource register tables.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn30.c` and `dmub_dcn302.c`, which include the same offset and mask headers for DMUB-facing register metadata.
- `drivers/gpu/drm/amd/display/dc/irq/dcn30/irq_service_dcn30.c` and `irq/dcn302/irq_service_dcn302.c`, which consume DCN 3.0 field definitions for interrupt sources.
- MPC code and resource macros across DCN generations use the same naming pattern for `MPC_OUT*_MUX`, `MPC_CRC_*`, `MPCC_OGAM*`, and `MPC_RMU*` fields. For example, `dc/mpc/dcn32/dcn32_mpc.h` defines field lists for MPCC OGAM LUT/gamut/PWL fields, and `dc/mpc/dcn10/dcn10_mpc.c` updates `MPC_OUT_MUX` fields through generated register helpers.

## Risks And Edge Cases

- Wrong shifts or masks compile cleanly but corrupt MMIO field access at runtime. A bad mask can route the wrong MPCC to an output, apply bad color transforms, leave stale pending status, or reset/gate an unintended compositor block.
- The chunk starts and ends mid-family. Whole-file conclusions must merge adjacent chunks for the full `MPCC_OGAM3` RAM A tail and the rest of `MPC_RMU0_SHAPER_RAMB_*`.
- Repeated instance families are copy-sensitive. `MPCC_OGAM4` and `MPCC_OGAM5`, and `MPC_OUT0` through `MPC_OUT5`, share layouts but are not interchangeable; one bad instance macro may only fail on a specific pipe/output.
- Gamma and CSC fields are visual-quality critical. Incorrect LUT indices/data masks, PWL segment masks, coefficient masks, or coefficient formats can cause banding, clipping, wrong color space, HDR/SDR conversion errors, or black/washed-out output.
- Pending and vupdate lock fields affect atomic update sequencing. Misidentified bits can make updates appear complete too early or keep them stuck pending, which can surface as flicker, missed flips, cursor artifacts, or modeset timeouts.
- Reset, clock, and memory power fields are high risk because writes can disable active display paths or interact badly with power-gated hardware.
- CRC and debug/status fields may have mixed control/status semantics. Using a status field in an update path or holding update locks incorrectly can make validation signals misleading.
- The generated constants are untyped `long` literals with `L` suffixes. Consumers must keep 32-bit register semantics intact when composing masks, especially for high-bit masks such as `0x80000000L` and packed 16-bit coefficient/result fields.

## Test Signals

Useful validation signals for this chunk are mostly build-time consistency plus DCN 3.0 display behavior:

- Build AMDGPU display code with DCN 3.0/3.0.2 enabled; unresolved or renamed field macros should fail in resource, DMUB, IRQ, GPIO, clock, and MPC register-table compilation.
- Mechanically verify that each complete register group in this range has paired shift/mask definitions, allowing for the intentional boundary exceptions at the first `MPCC_OGAM3` group and final `MPC_RMU0_SHAPER_RAMB_END_CNTL_B` line.
- Compare the generated shifts/masks against AMD's authoritative DCN 3.0 register database and the matching `dcn_3_0_0_offset.h` register names.
- Exercise color-management paths: output gamma LUT programming, RAM A/RAM B bank selection, gamut remap matrices, output CSC coefficients/modes, denormalization clamps, HDR/SDR transitions, and suspend/resume restoration.
- Test multi-display and high-instance configurations that use MPCC/OPP outputs beyond 0-3, especially output paths 4 and 5 and `MPCC_OGAM4`/`MPCC_OGAM5`.
- Validate atomic update timing with page flips, cursor updates, surface/config/current updates, vupdate locking, and pending-status polling.
- Validate MPC CRC capture using one-shot and continuous modes, selected sources, stereo/interlace modes, and result readback.
- Test reset, clock gating, memory power, and RMU shaper flows during modeset, blanking, idle, suspend/resume, and color-pipeline reconfiguration.
- Watch kernel logs and display diagnostics for underflow, modeset timeout, stale pending bits, CRC mismatch, color corruption, black screens, flicker, or resume failures.

## Cross-Chunk Notes

The previous chunk owns the beginning of the `MPCC_OGAM3` output gamma block. This chunk begins at the tail of `MPCC_OGAM3_MPCC_OGAM_RAMA_REGION_28_29`, then covers the rest of `MPCC_OGAM3` RAM B/gamut fields and complete `MPCC_OGAM4`/`MPCC_OGAM5` blocks. The next chunk continues after `MPC_RMU0_SHAPER_RAMB_END_CNTL_B` and is required to complete RMU0 RAMB end/region definitions and the later RMU register layout.

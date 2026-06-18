# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 56455-58975

## Purpose

This chunk is generated AMD DCN 3.1.4 display-controller register field metadata for the MPC/MPCC portion of the display pipeline. It contains no executable C logic; it publishes preprocessor constants that describe bit positions and masks for fields inside DCN314 MPC output gamma, output color-space conversion, global MPC configuration, DWB routing, and RMU shaper registers. Runtime display code combines these field constants with register offsets from `dcn_3_1_4_offset.h` and DC register helper macros before issuing MMIO reads, writes, read-modify-writes, waits, or debug captures.

The requested range contains 2,089 `#define` lines: 1,044 `__SHIFT` macros and 1,045 `_MASK` macros. It starts in the tail of the `MPCC_OGAM0` RAMB region definitions, covers complete `MPCC_OGAM1`, `MPCC_OGAM2`, and `MPCC_OGAM3` field blocks, covers the MPC global configuration and output CSC/denorm blocks, and ends inside the first RMU0 shaper RAMA region table. Although this repository path is under a `ceph-client` source mirror, this file is AMDGPU display-driver hardware metadata, not Ceph filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, local variables, includes, allocation paths, or locks in this chunk. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position for a hardware field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the same field.

Major macro families covered here:

- `MPCC_OGAM0_*`: the chunk begins after the start of `MPCC_OGAM0_MPCC_OGAM_RAMB_REGION_14_15`, then completes RAMB region descriptors from regions 16 through 33 and the OGAM0 gamut-remap coefficient format, gamut-remap mode, and A/B matrix coefficient fields.
- `MPCC_OGAM1_*`, `MPCC_OGAM2_*`, and `MPCC_OGAM3_*`: complete per-MPCC output gamma controls for three instances, including `MPCC_OGAM_CONTROL`, host LUT index/data/control, RAMA/RAMB start/end/slope/base/offset fields, piecewise-linear region descriptors for regions 0 through 33, and per-MPCC gamut-remap coefficient format/mode and 3x4 matrix coefficient fields.
- `MPC_CLOCK_CONTROL` and `MPC_SOFT_RESET`: global MPC clock gating/test-clock and soft-reset fields for MPCC0-3 plus MPC SFR/SFT subblocks and the global MPC reset bit.
- `MPC_CRC_*`: fields for enabling MPC CRC, continuous and one-shot capture, stereo/interlace modes, CRC source selection, update lock/status, source selection for DPP/OPP/DWB, CRC mask, and AR/GB/C result registers.
- `MPC_BYPASS_BG_*`, `MPC_HOST_READ_CONTROL`, `MPC_DPP_PENDING_STATUS`, and `MPC_PENDING_STATUS_MISC`: fields for bypass background color, host-read throttling, pending surface/config/cursor updates for DPP0-3, pending OPP/MPCC/DWB updates, and DWB mux routing.
- `ADR_CFG_CUR_VUPDATE_LOCK_SET<n>`, `ADR_CFG_VUPDATE_LOCK_SET<n>`, `ADR_VUPDATE_LOCK_SET<n>`, `CFG_VUPDATE_LOCK_SET<n>`, and `CUR_VUPDATE_LOCK_SET<n>` for instances 0 through 3: one-bit vertical-update lock request fields used to coordinate address/config/cursor update timing.
- `MPC_OUT0_*` through `MPC_OUT3_*`: output mux selection, rate/flow-control fields, denormalization clamp min/max fields, denorm mode fields, output CSC coefficient-format selection, per-output CSC mode/current status, and A/B banks of 3x4 output CSC matrix coefficient fields.
- `MPC_RMU_*` and `MPC_RMU0_SHAPER_*`: RMU mux routing/status, RMU memory power control for RMU0/RMU1 shaper and 3D LUT memories, RMU0 shaper mode/current status, RGB offset/scale fields, shaper LUT index/data/write-enable fields, and the beginning of RMU0 shaper RAMA region descriptors.

Several field names intentionally produce repeated suffixes such as `MPC_CRC_SEL_CONTROL__MPC_CRC_MASK_MASK` and `MPC_RMU0_SHAPER_LUT_WRITE_EN_MASK__MPC_RMU_SHAPER_LUT_WRITE_EN_MASK_MASK`. These are generated from fields whose hardware names include `MASK`; they are not accidental duplicate-mask definitions.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by the AMD display driver:

1. DCN314 resource, IRQ, and DMUB code include `dcn_3_1_4_sh_mask.h` together with the matching `dcn_3_1_4_offset.h`.
2. Token-pasting helpers such as `SF(...)`, `SR(...)`, `SRI(...)`, `SRII(...)`, and `SRII_MPC_RMU(...)` bind offsets, shifts, and masks into typed register/shift/mask tables.
3. `dcn314_resource.c` builds the `dcn30_mpc_registers`, `dcn30_mpc_shift`, and `dcn30_mpc_mask` tables using `MPC_REG_LIST_DCN3_0(0..3)`, `MPC_OUT_MUX_REG_LIST_DCN3_0(0..3)`, `MPC_RMU_GLOBAL_REG_LIST_DCN3AG`, `MPC_RMU_REG_LIST_DCN3AG(0..1)`, `MPC_DWB_MUX_REG_LIST_DCN3_0(0)`, and `MPC_COMMON_MASK_SH_LIST_DCN30(...)`.
4. MPC implementation code uses those tables to program MPCC composition/output gamma, output muxing, OCSC/denorm, CRC/debug capture, pending-update coordination, RMU shaper state, and memory-power controls during modesets, color updates, pipe routing changes, diagnostics, and power transitions.

The macros themselves do not encode ordering. Consumers must still sequence clock enablement, soft reset, memory power-up, update locks, double-buffered register updates, LUT bank selection, LUT writes, CSC bank programming, current-mode polling, CRC capture, DWB/RMU routing, and suspend/resume restoration according to hardware rules.

## State And Persistence Behavior

The file stores no software state and persists nothing. It describes MMIO-backed hardware state whose lifetime and side effects are hardware-defined. Represented state includes:

- MPCC output gamma mode/select bits, current-mode/current-select status, PWL disable, host LUT addressing/data, LUT write-color/read-color/debug/host/config controls, and RAMA/RAMB piecewise-linear segmentation for blue, green, and red channels.
- MPCC gamut remap coefficient format, active/current remap mode, and A/B banks of gamut-remap matrix coefficients.
- Global MPC clock/test/reset state, CRC enable/source/mode/update-lock state, CRC result state, bypass background color, host-read rate control, update-pending status, and vertical-update lock request fields.
- Output routing from MPC outputs 0 through 3, including rate-control overflow/ack/disable bits, flow-control mode/count, denorm clamp ranges, OCSC coefficient format, OCSC mode/current status, and A/B OCSC matrix banks.
- RMU routing/status, RMU memory power force/disable/low-power/state bits, RMU0 shaper offset/scale/LUT data, and the beginning of RMU0 shaper RAMA region segmentation.

Configuration fields generally retain values until a modeset, color pipeline update, power-gating event, suspend/resume path, or ASIC reset changes them. Status/current fields, pending-update fields, CRC result/pending fields, clock-gating controls, soft-reset controls, memory-power controls, and LUT index/data ports may be read-only, write-sensitive, sticky, self-clearing, banked, or sequencing-sensitive. This generated header only gives bit layout; it does not encode access type, reset value, volatility, or clear semantics.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN314 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_offset.h`, which provides the matching register offsets and `_BASE_IDX` selectors.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c`, which includes this header and builds the DCN314 MPC register, shift, and mask tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn30/dcn30_mpc.h`, which defines the reusable MPC register-list and mask/shift-list macros consumed by the DCN314 resource layer.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn314/irq_service_dcn314.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn314.c`, which also include the generated DCN314 headers for register access and service tables.
- Common MPC, OPP, color-management, hardware sequencer, DMUB, CRC, DWB, and debug paths that reach these fields through the resource-layer register tables rather than by including this chunk directly.
- Enum headers such as `include/soc24_enum.h`, which document legal values for related MPC/MPCC concepts including CRC modes, VUPDATE lock booleans, OGAM LUT bank/select/mode values, and OGAM region segment counts.

The resource table exposes four MPC/MPCC/output instances for DCN314 and includes RMU global plus RMU0/RMU1 register lists while leaving a third RMU list commented out. Generated constants can therefore exist for broader hardware metadata than every actively instantiated path in a given ASIC configuration.

## Risks And Edge Cases

- Bitfield drift is the main risk. These are untyped constants; a wrong shift or mask can compile cleanly and cause read-modify-write operations to touch the wrong hardware bits.
- The range has artificial chunk boundaries. It starts after the first fields of `MPCC_OGAM0_MPCC_OGAM_RAMB_REGION_14_15` and ends before the rest of `MPC_RMU0_SHAPER_RAMA_REGION_12_13` and subsequent RMU shaper definitions, so adjacent chunks are required for complete OGAM0/RMU coverage.
- MPCC OGAM RAMA/RAMB definitions are highly repetitive. Instance or region copy-generation mistakes can affect only specific MPCCs, LUT banks, color channels, or high-index PWL regions.
- LUT programming is banked and port-based. Confusing LUT host selection, RAMA/RAMB selection, write-color masks, read-color selection, index width, data width, or region descriptors can produce incorrect gamma curves, channel swaps, stale bank activation, or visible color discontinuities.
- Gamut remap and output CSC use A/B coefficient banks plus current-mode fields. Writing the wrong bank or interpreting `*_CURRENT` fields as programming bits can lead to tearing during color updates or stale matrix activation.
- MPC soft reset, clock gating, memory power, and RMU power fields are sequencing-sensitive. Access while a block is gated or reset may be ignored, return stale status, or break polling paths.
- Pending-update and VUPDATE-lock fields affect atomic update timing. Incorrect masks can leave surface/config/cursor updates stuck, prematurely unlocked, or synchronized to the wrong pipe.
- CRC and output mux fields are diagnostic and routing critical. Wrong source select, result mask, rate-control ack, flow-control count, or DWB/RMU mux status fields can make CRC debugging misleading, hide output stalls, or route capture/composition paths incorrectly.
- Denorm and CSC masks are format-sensitive. Wrong clamp bounds, denorm mode, coefficient format, or matrix coefficient masks can cause clipped output, color-space conversion errors, HDR/SDR mismatch, or failures limited to particular pixel formats and output paths.
- Generated names containing `_MASK_MASK` are valid and should not be normalized away by cleanup scripts or manual edits.

## Test Signals

Useful validation combines generated-header consistency with display hardware behavior:

- Build AMDGPU/DC with DCN314 enabled; missing or renamed macros should fail in `dcn314_resource.c`, `irq_service_dcn314.c`, `dmub_dcn314.c`, or shared MPC headers.
- Mechanically verify that each complete in-range register field has a matching shift/mask pair, while allowing the documented boundary partials at `MPCC_OGAM0_MPCC_OGAM_RAMB_REGION_14_15` and `MPC_RMU0_SHAPER_RAMA_REGION_12_13`.
- Diff this range against AMD's authoritative DCN 3.1.4 register database and adjacent generated DCN 3.x headers where MPC/MPCC/RMU layouts are expected to match.
- Exercise MPCC output gamma programming on MPCC0-3, including RAMA/RAMB bank changes, PWL region programming, RGB write masks, LUT readback/debug paths, and transitions between bypassed and enabled modes.
- Exercise gamut remap and output CSC on outputs 0-3 with SDR, HDR, limited/full range, RGB/YCbCr, and color-management updates; watch for color shifts, clipping, stale matrices, or per-output-only failures.
- Test atomic modesets, plane updates, cursor movement, and multi-display configurations while checking DPP/OPP/MPCC/DWB pending-status bits and VUPDATE lock behavior.
- Validate MPC CRC capture in one-shot and continuous modes, different source selections, stereo/interlace modes, and CRC masks; compare against expected CRC stability and result registers.
- Test DWB and RMU routing plus RMU shaper programming where supported, including memory-power transitions, suspend/resume, runtime power management, and LUT/3D-LUT low-power behavior.
- Watch kernel logs and display diagnostics for stuck update locks, failed register waits, CRC mismatches, blank output after reset/power changes, color corruption, LUT bank mismatches, output mux overflow errors, or failures limited to higher-numbered MPC/MPCC instances.

## Cross-Chunk Notes

The previous chunk owns the beginning of `MPCC_OGAM0`, including the start of its RAMB region table. This chunk completes most of the OGAM0 tail and covers full OGAM1-3 generated field blocks plus MPC global/output metadata. The next chunk continues the RMU shaper region table after `MPC_RMU0_SHAPER_RAMA_REGION_12_13` and is required before making file-level claims about all RMU shaper and 3D LUT fields in `dcn_3_1_4_sh_mask.h`.

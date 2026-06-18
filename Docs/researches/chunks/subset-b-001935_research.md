# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 15196-17713

## Purpose

This chunk is part of the generated AMD DCN 3.2.0 register shift/mask header. It contains no executable C logic; it publishes preprocessor constants that describe field bit positions (`__SHIFT`) and masks (`_MASK`) for the DCN MPC/MPCC and MPCC output-gamma blocks. Consumers combine these definitions with the matching `dcn_3_2_0_offset.h` register offsets and AMD display register helpers to build per-ASIC register tables.

The range starts inside the `MPCC1_MPCC_MOVABLE_CM_LOCATION_CONTROL` block, then covers the tail of MPCC1, complete MPCC2 and MPCC3 blend-compositor blocks, the common `dcn_dc_mpc_mpc_cfg_dispdec` MPC configuration block, complete `MPCC_OGAM0`, `MPCC_OGAM1`, and `MPCC_OGAM2` output gamma/gamut blocks, and most of `MPCC_OGAM3`. It ends in the middle of `MPCC_OGAM3_MPC_GAMUT_REMAP_C33_C34_A`; the matching masks for those final two shift definitions fall immediately after this chunk.

Although this source tree is rooted under `ceph-client`, this file is AMDGPU display hardware metadata, not distributed-filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, allocation paths, locks, or direct MMIO operations in this chunk. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the low bit index of a hardware field.
- `<REGISTER>__<FIELD>_MASK`: the mask used to isolate or update that field.
- `// addressBlock: ...`: generated grouping comments that map groups of field definitions to DCN register blocks.

The chunk contains 2,083 `#define` entries: 1,042 shift definitions and 1,041 mask definitions. The count is intentionally uneven because the line range starts after one `MPCC1` shift definition and ends before two `MPCC_OGAM3` mask definitions.

Major register groups in this slice are:

- `MPCC1` tail fields: movable color-management location current/control state, background R/G/B or Cr/Y/Cb components, OGAM memory power control, and MPCC idle/busy/disabled status.
- `MPCC2` and `MPCC3`: complete per-compositor fields for top/bottom source selection, OPP routing, blend mode, alpha mode, premultiplied alpha, overlap-only blending, background bit depth, bottom gain mode, global alpha/gain, stereo mode control, update lock selection/status, top/bottom gains, movable color-management location, background color, OGAM memory power state, and idle/busy/disabled status.
- `MPC_*` common configuration: clock gating controls, soft-reset bits for MPC, MPCC, OPP, DPP, DWB, DSC, and shaper/filter units, CRC control and selection, CRC result registers, bypass background color, host-read control, DPP pending status, misc pending status, vertical-update lock set selectors/status, and DWB mux selection/status.
- `MPCC_OGAM0` through `MPCC_OGAM2`: complete per-MPCC output gamma blocks, including OGAM enable/select/current state, LUT index/data/control, RAM A and RAM B piecewise-linear region programming for B/G/R channels, per-channel offsets, region-pair tables for regions 0 through 33, gamut-remap coefficient format/mode, and A/B matrix coefficient registers.
- `MPCC_OGAM3`: the same OGAM and gamut-remap structure as instances 0-2 up to `MPC_GAMUT_REMAP_C33_C34_A` shifts; the following chunk contains the remaining masks and B-coefficient fields.

Representative fields include:

- MPCC routing and blending: `MPCC_TOP_SEL`, `MPCC_BOT_SEL`, `MPCC_OPP_ID`, `MPCC_MODE`, `MPCC_ALPHA_BLND_MODE`, `MPCC_ALPHA_MULTIPLIED_MODE`, `MPCC_BLND_ACTIVE_OVERLAP_ONLY`, `MPCC_GLOBAL_ALPHA`, and `MPCC_GLOBAL_GAIN`.
- Update and status fields: `MPCC_UPDATE_LOCK_SEL`, `MPCC_UPDATE_LOCKED_STATUS`, `MPCC_IDLE`, `MPCC_BUSY`, `MPCC_DISABLED`, `MPC_CRC_ONE_SHOT_PENDING`, `MPC_CRC_UPDATE_ENABLED`, and `MPC_CRC_UPDATE_LOCK`.
- Power-management fields: `MPCC_OGAM_MEM_PWR_FORCE`, `MPCC_OGAM_MEM_PWR_DIS`, `MPCC_OGAM_MEM_LOW_PWR_MODE`, and `MPCC_OGAM_MEM_PWR_STATE`.
- OGAM LUT fields: `MPCC_OGAM_MODE`, `MPCC_OGAM_SELECT`, `MPCC_OGAM_PWL_DISABLE`, current mode/select status, LUT index/data, LUT color write mask, host RAM selection, read color selection, and config mode.
- Piecewise-linear transfer-function fields: region start, start segment, start slope, start base, end base, end, end slope, offset, LUT offset, and number of segments for RAM A and RAM B.
- Gamut remap fields: coefficient format, active/current remap mode, and packed 16-bit matrix coefficients `C11` through `C34` for coefficient sets A and B.

## Control Flow

This header chunk has no runtime control flow. Runtime sequencing is supplied by AMDGPU display code that includes `dcn_3_2_0_offset.h` and `dcn_3_2_0_sh_mask.h`, then uses token-pasting macros to populate typed register-address and shift/mask tables.

The normal flow for these definitions is:

1. DCN32 resource construction builds MPC register lists with macros such as `SRII(...)`/`SRI_ARR(...)`, binding each indexed MPCC or MPCC_OGAM register to the matching offset macro.
2. DCN32 MPC code builds field tables with `SF(...)`, using this header's `__SHIFT` and `_MASK` constants to populate `mpc_shift` and `mpc_mask`.
3. Runtime MPC helpers call `REG_SET`, `REG_UPDATE`, `REG_UPDATE_2`, `REG_GET`, or `REG_WAIT`. Those helpers use the register table plus the shift/mask table to compose MMIO reads and writes.
4. Hardware state changes occur in the MPC/MPCC block: compositor topology, blending, update locks, CRC capture, DWB muxing, output gamma LUT programming, gamut remap matrices, and OGAM memory power state.

Important runtime paths using these field families include:

- `mpc3_mpc_init()` and `mpc3_mpc_init_single_inst()` in `display/dc/mpc/dcn30/dcn30_mpc.c`, which initialize MPC output mux/rate-control state.
- DWB mux helpers (`mpc3_set_dwb_mux()`, `mpc3_disable_dwb_mux()`, `mpc3_is_dwb_idle()`), which use the DWB mux fields defined in the MPC config portion of the chunk.
- OGAM helpers (`mpc3_get_ogam_current()`, `mpc3_power_on_ogam_lut()`, `mpc3_configure_ogam_lut()`, `mpc3_set_output_gamma()`), which use the OGAM control, memory-power, LUT, and RAM A/B region fields.
- Gamut-remap helpers (`mpc3_set_gamut_remap()` and related read/program helpers), which use the MPCC_OGAM gamut mode and coefficient fields.

The generated constants do not encode valid programming order, read/write access type, volatile behavior, locking, or side effects. Callers must still obey display-core sequencing around modesets, update locks, vupdate boundaries, power gating, CRC capture, and LUT double-buffering.

## State And Persistence Behavior

This chunk stores no software state and persists nothing to memory, disk, firmware, or kernel data structures by itself. It describes MMIO-backed state in the DCN 3.2 MPC hardware.

The represented hardware state includes:

- Per-MPCC compositor topology and blend state: selected top/bottom inputs, target OPP, blend mode, alpha mode, global alpha/gain, per-plane gains, background color, and active/idle/disabled status.
- Update synchronization state: selected update-lock domain and locked-status fields for MPCC programming.
- MPC configuration state: clock-gating controls, soft-reset bits, CRC enable/source/result state, bypass background color, host-read behavior, pending-status reporting, vupdate lock set selectors, and DWB mux routing.
- Output-gamma state: selected OGAM mode, active RAM bank, current RAM/mode status, LUT index and data writes, per-channel RAM A/B region tables, PWL offsets, and low-power memory state.
- Gamut-remap state: coefficient format, selected remap mode, current mode status, and packed 3x4 color-transform coefficients for A/B banks.

Persistence is hardware-defined. Programmed configuration generally survives until the next modeset, plane update, color-management update, power transition, suspend/resume, reset, or ASIC reinitialization. Status fields such as idle/busy, current mode/select, pending state, CRC pending/update state, and memory power state are live hardware observations and may change independently of software writes.

## Dependencies And Integration Points

This generated chunk must remain synchronized with the rest of the DCN 3.2 register database:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h` supplies the matching register offsets and base-index macros.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.h` maps MPCC, MPC, DWB, and MPCC_OGAM registers into DCN32 resource register lists.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn32/dcn32_mpc.h` extends the MPC register and shift/mask lists for DCN32, including movable color-management location, MPCC status/memory power, OGAM LUT control, region fields, and gamut remap fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn30/dcn30_mpc.c` contains the shared DCN3 runtime programming code that consumes these registers for OGAM LUT programming, memory power control, DWB muxing, denorm/gamma/gamut behavior, and MPC initialization.
- Other DCN32 include sites such as DMUB, IRQ, clock-manager, GPIO, and resource code include this header for their own register table construction, even if this specific chunk's fields are primarily MPC/MPCC-owned.

The key integration contract is name stability. Higher-level macros token-paste names such as `MPCC_OGAM0_MPCC_OGAM_RAMA_REGION_0_1__MPCC_OGAM_RAMA_EXP_REGION0_LUT_OFFSET_MASK`; if a generated register or field name drifts from the offset header or from the `SF`/`SRII` lists, the build fails. If a mask value or shift value is wrong while the name still matches, the build can succeed but runtime MMIO programming targets the wrong bits.

## Risks And Edge Cases

- Field drift is the main risk. These macros are untyped numeric constants, so an incorrect shift or mask can silently corrupt display hardware programming.
- The chunk is not aligned to register boundaries. It starts after the first `MPCC1_MPCC_MOVABLE_CM_LOCATION_CONTROL` shift and ends before the `MPCC_OGAM3_MPC_GAMUT_REMAP_C33_C34_A` masks; adjacent chunks are required for complete per-register accounting.
- Repeated MPCC/OGAM instances are copy-generation sensitive. A mismatch in only `MPCC2`, `MPCC3`, or one `MPCC_OGAM` instance can produce failures tied to a specific plane/compositor instance rather than all display pipelines.
- OGAM RAM A/B programming is double-buffered. Wrong masks for current/select fields, host RAM selection, LUT index/data, region tables, or memory power can cause stale gamma curves, visible color discontinuities, failed LUT uploads, or writes to the active RAM bank.
- `MPCC_OGAM_MEM_PWR_*` fields gate access to OGAM memory. If masks are wrong, code may write while RAM is powered down or fail to release low-power state after programming.
- Gamut-remap coefficient fields are packed 16-bit values. A wrong high/low-half mask or shift can transpose, truncate, or corrupt matrix coefficients, producing color-space errors while still leaving the display functional.
- MPC soft-reset and clock-control fields are high impact. Bad masks in this area can reset or gate the wrong display sub-block.
- CRC and pending-status fields are diagnostic and validation-facing. Wrong masks can make CRC tests, underrun/pending diagnostics, or debug captures misleading.
- Update-lock and vupdate-lock fields are timing sensitive. Incorrect masks can cause tearing, partially applied plane/compositor updates, or difficult-to-reproduce modeset artifacts.

## Test Signals

Useful validation should combine generated-header checks with hardware-oriented display tests:

- Build AMDGPU display code with DCN32 enabled. Token-paste mismatches should surface in `dcn32_mpc.h`, `dcn32_resource.h`, DMUB, IRQ, clock, GPIO, or resource compilation.
- Mechanically compare every field in this chunk against the authoritative DCN 3.2 register database and neighboring generated headers where layouts are expected to match.
- Verify that repeated `MPCC2` and `MPCC3` blocks match the `MPCC0/1` schema, apart from expected instance prefixes and line-range truncation at the chunk edges.
- Verify that `MPCC_OGAM0`, `MPCC_OGAM1`, and `MPCC_OGAM2` are structurally identical and that `MPCC_OGAM3` matches through the fields present in this chunk.
- Run display color-management tests on DCN32 hardware: gamma LUT updates, RAM A/B flipping, degamma/gamma bypass, gamut remap enable/disable, coefficient set A/B selection, and suspend/resume after color programming.
- Exercise multi-plane composition paths across MPCC instances: alpha blending, global alpha/gain, background color, update-lock behavior, movable color-management location, and plane enable/disable.
- Exercise DWB and CRC debug paths if available: DWB mux select/idle behavior, CRC source selection, one-shot and continuous CRC capture, and CRC result reads.
- Watch for display artifacts after modeset, plane updates, color-profile changes, HDR/SDR transitions, memory low-power toggling, and suspend/resume. Failures may be instance-specific because the register blocks are repeated per MPCC.

## Cross-Chunk Notes

This chunk is one slice of the large generated `dcn_3_2_0_sh_mask.h` file. The final per-file report should merge it with the previous chunk for the beginning of `MPCC1_MPCC_MOVABLE_CM_LOCATION_CONTROL` and with the following chunk for the rest of `MPCC_OGAM3` and subsequent MPCC MCM blocks before making complete claims about the DCN32 MPC/MPCC register namespace.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 17707-20193

## Scope And Purpose

This chunk is part of AMD's generated DCN 4.1.0 register shift/mask header. It contains C preprocessor constants for display hardware register fields, not executable driver logic. Each `#define` supplies either a bit position (`__SHIFT`) or an already-positioned bit mask (`_MASK`) used by AMD display register helpers when packing values into memory-mapped DCN registers.

The requested range contains 2,077 `#define` lines: 1,040 shift macros and 1,037 mask macros. The imbalance is from chunk boundaries: the range starts in the middle of `MPCC_OGAM0_MPCC_OGAM_RAMA_START_CNTL_R` after adjacent definitions in the previous chunk, and it ends before the final masks for `MPCC_MCM0_MPCC_MCM_SHAPER_RAMB_REGION_28_29`.

The hardware surface is color management inside the MPC/MPCC path:

- The tail of `addressBlock: dcn_dcec_mpc_mpcc_ogam0_dispdec`, then complete `MPCC_OGAM1`, `MPCC_OGAM2`, and `MPCC_OGAM3` output gamma/gamut-remap field groups.
- The beginning of `addressBlock: dcn_dcec_mpc_mpcc_mcm0_dispdec`, covering MCM shaper control, offsets, scale, LUT index/data/write control, RAM A region programming, and most of RAM B region programming.

## Important Constants And Register Areas

`MPCC_OGAM[0-3]_MPCC_OGAM_*` define the per-MPCC output gamma block. Each instance has control fields for `MPCC_OGAM_MODE`, `MPCC_OGAM_SELECT`, `MPCC_OGAM_PWL_DISABLE`, and corresponding current-status fields. The instances also expose `MPCC_OGAM_LUT_INDEX`, `MPCC_OGAM_LUT_DATA`, and `MPCC_OGAM_LUT_CONTROL` fields for host programming of LUT entries, write color masks, read color selection, debug readback, host RAM selection, and RGB configuration mode.

The OGAM RAM A/RAM B field groups describe double-buffered PWL transfer-function configuration. For each color channel, the chunk defines start control, start slope, start base, end base/end value/end slope, and channel offset fields. Region registers `REGION_0_1` through `REGION_32_33` pack two adjacent exponential regions per register, with LUT offset fields at bits 0 and 16 and 3-bit segment-count fields at bits 12 and 28. Common widths are 18-bit custom-float values (`0x0003FFFFL`), 7-bit start segment fields (`0x07F00000L`), 19-bit offsets (`0x0007FFFFL`), 16-bit end/slope fields, and 9-bit LUT offsets.

`MPCC_OGAM[0-3]_MPCC_GAMUT_REMAP_*` and `MPCC_OGAM[0-3]_MPC_GAMUT_REMAP_*` define the legacy MPCC gamut-remap matrix behind the OGAM block. The coefficient format register selects `MPCC_GAMUT_REMAP_COEF_FORMAT`, the mode register selects coefficient set A/B or bypass and exposes `MPCC_GAMUT_REMAP_MODE_CURRENT`, and six packed coefficient registers per bank hold C11/C12 through C33/C34 in 16-bit fields.

`MPCC_MCM0_MPCC_MCM_SHAPER_*` starts the newer movable color-management shaper block. The chunk includes shaper mode/current-mode, per-channel offsets and scale values, LUT index/data registers, `MPCC_MCM_SHAPER_LUT_WRITE_EN_MASK`, `MPCC_MCM_SHAPER_LUT_WRITE_SEL`, and RAM A/RAM B region descriptors. RAM A is complete through regions 32/33. RAM B is complete through regions 26/27 and includes the first five definitions of region 28/29, with the remaining three masks outside this requested range.

The MCM shaper field layout is similar to the older OGAM PWL layout but not identical. Its start controls include start value and start segment per channel; its end controls pack end value and end base, rather than the OGAM split of end base in `END_CNTL1` plus end value and end slope in `END_CNTL2`. The shaper region registers still use the same two-region packing pattern: LUT offsets in 9-bit fields and segment counts in 3-bit fields.

## APIs, Types, And Functions

There are no functions, structs, enums, or inline helpers in this chunk. The public surface is the generated macro namespace:

- `REGISTER__FIELD__SHIFT` gives the field bit position.
- `REGISTER__FIELD_MASK` gives the field mask already shifted into register position.

These macros feed generated register-address, shift, and mask tables consumed by AMD's `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_SET_2`, `REG_SET_4`, and related helpers. DCN401 display code includes this header from resource, clock, GPIO, IRQ, and DMUB paths; the color-management-specific use is through MPC register tables and the shared color-management helpers.

Relevant consumer types and helpers are outside this generated header. `struct dcn401_mpc_registers`, `struct dcn401_mpc_shift`, and `struct dcn401_mpc_mask` in `display/dc/mpc/dcn401/dcn401_mpc.h` hold the DCN401 MPC register offsets and bitfield metadata. Shared helper structures such as `struct color_matrices_reg` and transfer-function register structs in `dcn10_cm_common.h` carry register addresses plus shift/mask fields into helper routines such as `cm_helper_program_color_matrices()` and PWL transfer-function programming helpers.

## Control Flow And Runtime Behavior

This header has no local control flow. Runtime behavior happens when higher-level color-management code chooses a pipe/MPCC instance, selects a LUT bank or gamut-remap bank, writes the inactive bank through these bitfields, and then flips control bits so hardware uses the newly programmed state.

The OGAM flow is represented by older MPC implementations and inherited DCN401 function pointers. Output gamma code powers on OGAM memory, picks RAM A or RAM B based on current state, programs start/end/region metadata and per-point LUT data through `MPCC_OGAM_LUT_INDEX` and `MPCC_OGAM_LUT_DATA`, then updates `MPCC_OGAM_CONTROL` fields such as `MPCC_OGAM_MODE`, `MPCC_OGAM_SELECT`, and `MPCC_OGAM_PWL_DISABLE`. The field names in this chunk are the low-level layout that makes that double-buffered update possible for all four MPCC OGAM instances.

The gamut-remap flow in `dcn401_mpc.c` programs three possible matrix blocks: the legacy `MPCC_OGAM_GAMUT_REMAP`, `MPCC_MCM_FIRST_GAMUT_REMAP`, and `MPCC_MCM_SECOND_GAMUT_REMAP`. For each block, software reads the current mode, chooses coefficient set A or B, writes six packed coefficient registers through `cm_helper_program_color_matrices()`, then sets the mode register to select the new set or bypass the block. The OGAM gamut-remap fields in this chunk are directly part of that first case; the MCM first/second gamut-remap fields are adjacent in the same generated header but outside most of this line range.

The MCM shaper flow is used by DCN401 MCM LUT programming. `dcn401_set_mcm_luts()` chooses a bank by reading current 1D LUT, shaper, and 3D LUT mode state, fixes movable color management before blending, then calls MPC function hooks to program LUT mode and populate the selected LUT. For shaper programming, the MCM shaper start/end/region and LUT data fields in this chunk define how a PWL shaper function is loaded into RAM A or RAM B.

## State And Persistence

The file itself stores no mutable state. It defines how software addresses state stored in DCN 4.1.0 display hardware registers.

Persistent hardware state represented here includes OGAM enable/bypass mode, selected OGAM RAM bank, PWL disable state, current-mode readback, per-channel OGAM LUT contents, OGAM PWL start/end/base/slope/offset/region metadata, OGAM gamut-remap coefficient format, selected gamut-remap bank, gamut-remap matrix coefficients, MCM shaper enable/current mode, shaper offsets and scales, selected shaper write bank, shaper LUT contents, and shaper RAM A/RAM B region metadata. These values can remain active across frames and are changed by modeset, color-management updates, plane/stream updates, suspend/resume restore, or hardware reset.

Double buffering is central. The paired RAM A/RAM B and coefficient-set A/B definitions let software write inactive state while the current state is scanned out, then switch the mode/select field. Current-status fields such as `MPCC_OGAM_MODE_CURRENT`, `MPCC_OGAM_SELECT_CURRENT`, `MPCC_GAMUT_REMAP_MODE_CURRENT`, and `MPCC_MCM_SHAPER_MODE_CURRENT` are readback signals used to select the next inactive bank and avoid overwriting a live bank.

## Dependencies And Integration Points

This generated shift/mask header depends on the matching DCN 4.1.0 register-address header, especially `dcn_4_1_0_offset.h`, and on the AMD display register helper framework that combines register offsets, shifts, and masks. Numeric values are ASIC-generation-specific and must stay paired with the matching DCN401 offset and enum headers.

Important integration points include:

- `display/dc/resource/dcn401/dcn401_resource.c`, which includes `dcn_4_1_0_sh_mask.h` and builds DCN401 resource objects and register tables.
- `display/dc/mpc/dcn401/dcn401_mpc.h`, whose `MPC_COMMON_MASK_SH_LIST_DCN4_01()` and register-list macros map DCN401 MPC field names into typed shift/mask/register structures.
- `display/dc/mpc/dcn401/dcn401_mpc.c`, which uses those tables to program and read gamut-remap blocks, LUT modes, shaper/3D/1D LUT controls, and the DCN401 MPC function table.
- `display/dc/hwss/dcn401/dcn401_hwseq.c`, which calls MPC hooks for stream and plane gamut remap and MCM LUT programming.
- Shared color helpers in `display/dc/dcn10/dcn10_cm_common.c`, `display/dc/dcn30/dcn30_cm_common.c`, and older MPC implementations such as `display/dc/mpc/dcn30/dcn30_mpc.c`, which show the PWL start/end/region programming model used by the OGAM fields in this chunk.
- `include/soc24_enum.h`, which supplies enum values for OGAM LUT RAM selection, LUT color selection, PWL enable/disable, mode selection, coefficient format, and region segment counts.

## Risks And Edge Cases

Generated-header drift is the main risk. A wrong shift or mask can compile cleanly while writing the wrong hardware bits, because the register helper layer trusts the generated constants. Color symptoms can include incorrect transfer functions, bad gamut matrices, visible banding, wrong color temperature, invalid HDR/SDR mapping, or a blank/unstable pipe if bank switching and memory programming go wrong.

The chunk boundaries are incomplete. The opening lines only contain the red-channel tail of `MPCC_OGAM0_MPCC_OGAM_RAMA_START_CNTL_R`; the blue and green start-control fields and the comment header are in the previous chunk. The ending line stops at the first mask for `MPCC_MCM0_MPCC_MCM_SHAPER_RAMB_REGION_28_29`; masks for region 28 segment count and region 29 fields follow outside this range. Whole-file reconciliation must merge neighboring chunks before making complete claims about those two register groups.

Repeated instance layout is easy to mishandle. OGAM instances 0 through 3 largely repeat the same fields, but instance numbers select different MPCC hardware. A macro copied from the wrong instance can affect only one pipe, so validation must exercise more than MPCC0 and must include multi-plane or multi-display paths.

Bank selection is sequencing-sensitive. RAM A/B and coefficient set A/B are intended to avoid live updates to active color state. Programming the currently selected bank, changing mode before all LUT entries are written, or using stale current-mode readback can produce one-frame corruption or persistent color errors.

The MCM shaper and OGAM PWL layouts are similar but not interchangeable. Their start/end control names and field meanings differ, especially around end slope/base handling. Code that reuses OGAM assumptions for MCM shaper fields can write plausible-looking values to the wrong subfields.

Field widths need range discipline. Many fields use 18-bit or 19-bit custom-float/fixed fields, 16-bit coefficient or end fields, 9-bit LUT offsets, and 3-bit segment counts. Callers must rely on the conversion helpers and generated masks rather than passing arbitrary user values directly to register writes.

## Test And Validation Signals

Build validation should include DCN401 display objects that include this header and instantiate MPC shift/mask tables, especially `dcn401_resource.c`, `dcn401_mpc.c`, `dcn401_hwseq.c`, and the broader DCN401 display build. Missing or renamed macros usually surface as compile failures when table initializers reference the generated names.

Useful generated-data checks include:

- Verify each complete register group in this range has matching shift and mask definitions.
- Diff `MPCC_OGAM1`, `MPCC_OGAM2`, and `MPCC_OGAM3` against the complete parts of `MPCC_OGAM0` for structural consistency.
- Validate region registers use non-overlapping masks: region0/2/etc. LUT offset at `0x000001FFL`, segment count at `0x00007000L`, region1/3/etc. LUT offset at `0x01FF0000L`, and segment count at `0x70000000L`.
- Include adjacent chunks when checking `MPCC_OGAM0_MPCC_OGAM_RAMA_START_CNTL_R` and `MPCC_MCM0_MPCC_MCM_SHAPER_RAMB_REGION_28_29`.
- Compare DCN401 MPC shift/mask lists against the generated header so every referenced field has the expected shift and mask.

Runtime validation signals include correct stream and plane gamut-remap behavior, successful OGAM output gamma updates across RAM A/B transitions, stable MCM shaper programming for plane color-management updates, no visible flicker or one-frame color jumps during atomic commits, correct suspend/resume restoration of color state, and multi-display testing that exercises all available MPCC instances rather than only instance 0.

## Research Notes

This is source-tree-aligned chunk research only. It intentionally writes only `Docs/researches/chunks/subset-b-002158_research.md`. The final per-file research document for `dcn_4_1_0_sh_mask.h` should merge neighboring chunks to complete the partial opening OGAM start-control register and the partial trailing MCM shaper RAMB region register.

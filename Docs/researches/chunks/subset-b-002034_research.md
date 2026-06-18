# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h lines 17713-20169

## Scope And Purpose

This chunk is part of AMD's generated DCN 3.2.1 register shift/mask header. It contains C preprocessor constants for hardware register bitfields, not executable driver logic. The constants are used with matching DCN 3.2.1 register-address headers and AMD display register helpers to pack and unpack fields in memory-mapped display hardware registers.

The requested range contains 2,079 `#define` lines: 1,041 `__SHIFT` macros and 1,038 `_MASK` macros. The imbalance is caused by chunk boundaries. The range starts in the tail of `MPCC_OGAM3` gamut-remap bank-B coefficient fields and ends inside `MPCC_MCM2_MPCC_MCM_1DLUT_RAMA_REGION_6_7` before that register's final shift and mask lines. It also contains 372 comment lines, including address-block boundaries for `dce_dc_mpc_mpcc_mcm0_dispdec`, `dce_dc_mpc_mpcc_mcm1_dispdec`, and `dce_dc_mpc_mpcc_mcm2_dispdec`.

The substantive hardware covered here is the multi-plane compositor color-management register layout for `MPCC_MCM0`, `MPCC_MCM1`, and the beginning of `MPCC_MCM2`. These blocks describe shaper LUTs, 3D LUTs, 1D LUTs, RAM A/B piecewise LUT regions, LUT read/write data ports, and memory power-control fields for per-MPCC color processing.

## Important Constants And Register Areas

The opening lines complete the preceding `MPCC_OGAM3` gamut-remap matrix bank B. The visible fields are `MPCC_OGAM3_MPC_GAMUT_REMAP_C31_C32_B` and `C33_C34_B`, each packing two 16-bit gamut-remap coefficients with low and high halfword masks. The earlier matrix coefficients and control fields belong to the previous chunk.

`MPCC_MCM0_*` is complete in this range. It covers:

- `MPCC_MCM_SHAPER_CONTROL`, offsets, scales, LUT index/data, and shaper LUT write-enable selection.
- `MPCC_MCM_SHAPER_RAMA_*` and `MPCC_MCM_SHAPER_RAMB_*`, including per-channel start/end controls and region descriptors for regions 0 through 33.
- `MPCC_MCM_3DLUT_MODE`, index, data, 30-bit data, read/write control, output normalization, and per-channel output offset/scale fields.
- `MPCC_MCM_1DLUT_CONTROL`, LUT index/data/control, 1D LUT RAM A/B start, slope, base, end, offset, and region descriptors.
- `MPCC_MCM_MEM_PWR_CTRL`, which controls and reports memory power state for shaper, 3D LUT, and 1D LUT memories.

`MPCC_MCM1_*` repeats the same complete programming surface for MPCC MCM instance 1. The field layout is structurally parallel to MCM0, which makes instance-to-instance diffing a useful validation signal for generated-header changes.

`MPCC_MCM2_*` begins the same repeated register family for instance 2. This chunk includes its shaper control and RAM A/B definitions, 3D LUT definitions, 1D LUT control and LUT data/control definitions, and the start of 1D LUT RAM A programming through the first three shift macros of `MPCC_MCM2_MPCC_MCM_1DLUT_RAMA_REGION_6_7`. The masks for that final region register and the rest of MCM2 continue after the requested range.

Common bitfield shapes in this chunk include:

- Two halfword fields packed into one 32-bit register, such as 3D LUT data entries or coefficient pairs, using shifts `0x0` and `0x10`.
- Region descriptor registers that pack two regions per register: LUT offset at bit 0 or bit 16, and segment count at bit 12 or bit 28, with masks `0x000001FF`, `0x00007000`, `0x01FF0000`, and `0x70000000`.
- Per-channel B/G/R start, slope, base, end, and offset registers for piecewise LUT programming.
- Mode/current-mode pairs such as shaper mode, 3D LUT mode, and 1D LUT mode, where programmed state and active hardware state may be separately readable.
- Memory power-control fields grouped by shaper, 3D LUT, and 1D LUT memories, with force, disable, low-power mode, and status fields.

## APIs, Types, And Functions

There are no functions, structs, enums, or inline helpers in this chunk. The API surface is the generated macro namespace:

- `REGISTER__FIELD__SHIFT` gives the bit position of a field.
- `REGISTER__FIELD_MASK` gives the positioned field mask.
- `//REGISTER` and `// addressBlock: ...` comments group macros by hardware register and generated address block.

Consumers pair these masks and shifts with matching `reg...` offset macros from `dcn_3_2_1_offset.h`. For example, the corresponding offset header defines `regMPCC_MCM0_MPCC_MCM_MEM_PWR_CTRL` at base index 3, and similarly defines MCM1, MCM2, and MCM3 addresses. The shift/mask values in this file are only correct for the matching DCN 3.2.1 register map.

The larger AMD display stack typically consumes generated register metadata through register helper macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, register field lists, and ASIC-specific resource or block initialization tables. This chunk supplies the field layout for those helpers; it does not enforce valid enum values, sequencing, or read/write permissions.

## Control Flow And Runtime Behavior

This header has no local control flow. Runtime behavior occurs when display driver code writes or reads the described registers.

The implied control flows are color-pipeline programming flows. A caller selects LUT modes, writes LUT data through index/data ports, configures piecewise region descriptors, selects RAM A or RAM B banks, and then enables or observes the active color-management mode. Shaper LUTs and 1D LUTs use start/end/slope/base/offset fields and region tables to describe piecewise transfer functions. The 3D LUT path uses mode, size, RAM selection, 30-bit enable, data write-enable masks, read selection, output normalization, and output offset/scale fields.

The memory power-control registers introduce power-management flows. Driver code may force, disable, or observe low-power state for shaper, 3D LUT, and 1D LUT memories. These fields must be coordinated with LUT programming and active display timing because powering down a memory while its color path is selected can corrupt output or produce hardware-visible faults.

The region descriptor tables are mechanically regular, but the chunk boundary is not. The final visible MCM2 region register is incomplete in this research slice, so any whole-register validation of `MPCC_MCM2_MPCC_MCM_1DLUT_RAMA_REGION_6_7` must include the next source chunk.

## State And Persistence

The file itself stores no mutable state. It defines how software addresses state stored in DCN hardware registers and LUT RAMs.

Persistent hardware state represented in the chunk includes shaper offsets/scales, shaper LUT data, 3D LUT data and output normalization, 1D LUT data, RAM A/B start/end/slope/base/offset values, region segmentation tables, mode selections, active/current mode readbacks, and memory power state. These values can persist across frames and across parts of the display pipeline lifetime until reset or reprogrammed by modeset, color-management, power-management, or resume paths.

Double-buffered RAM A/B and mode/current fields are especially important. They imply that a driver can prepare one LUT bank while another is active, then switch or observe active state at a controlled point. The macros do not document the required synchronization point; that must come from higher-level DCN programming sequences.

## Dependencies And Integration Points

This generated header depends on the matching DCN 3.2.1 address header and the AMDGPU display register helper framework. Numeric masks are not portable across ASIC generations unless the corresponding hardware register database says the layouts match.

Important integration points include:

- DCN 3.2.1 MPC/MPCC color management, where these fields program shaper LUTs, 3D LUTs, 1D LUTs, and gamut/color transform state.
- Per-plane or per-compositor color pipelines that map logical MPCC instances to `MPCC_MCM0`, `MPCC_MCM1`, `MPCC_MCM2`, and later instances.
- Display color-management APIs that load 1D LUT, 3D LUT, shaper, degamma/gamma, or gamut-remap data.
- Runtime power-management code that coordinates memory power state with active color blocks.
- Generated register-list macros that rely on stable token naming across offset, shift, and mask headers.

The adjacent generated enum headers provide semantic values for many fields, including MCM 3D LUT size and 30-bit mode, gamma LUT mode, RAM selection, LUT segment counts, read color selection, LUT config mode, and memory power force/state values. This shift/mask file gives bit positions only; semantic interpretation comes from those enums and the caller's programming sequence.

## Risks And Edge Cases

Generated-header drift is the main risk. A wrong shift or mask compiles cleanly but can silently write the wrong register bits, causing bad color output, failed LUT updates, stale current-mode readback, or unsafe memory power transitions.

Chunk boundaries create local incompleteness. The start belongs to an earlier `MPCC_OGAM3` gamut-remap block, and the end cuts off `MPCC_MCM2_MPCC_MCM_1DLUT_RAMA_REGION_6_7` before its complete field set. Per-file reconciliation must merge neighboring chunks before making complete claims for either register family.

Repeated-instance consistency matters. MCM0 and MCM1 are complete and structurally parallel in this range; MCM2 begins the same pattern. A generator error that affects only one instance could produce output defects only on the corresponding MPCC path, so tests must cover multiple pipes and compositor instances.

RAM bank and write-enable fields are sequencing-sensitive. Writing LUT data to the wrong RAM bank, using the wrong color write mask, or switching modes before the table is fully programmed can create visible color discontinuities. Current-mode fields should not be assumed to update synchronously with programmed-mode writes unless the hardware sequence says so.

Memory power fields are side-effect-prone. Force, disable, low-power mode, and state fields for shaper, 3D LUT, and 1D LUT memories can affect retention and availability of color data. Callers should avoid ad hoc writes to these fields and should use established DCN power-management sequences.

Mask width and signedness are minor but real maintenance risks. Constants use `L` suffixes and full 32-bit masks such as `0xFFFF0000L` and `0x70000000L`; consumers should use unsigned register-width types and central field macros rather than open-coded arithmetic.

## Test And Validation Signals

Build validation should include all DCN 3.2.1 display objects that include `dcn_3_2_1_sh_mask.h` and use generated register lists. Missing or renamed macros usually surface at compile time; wrong numeric values usually require hardware or register-database validation.

Useful generated-data checks include:

- Compare the chunk against the authoritative DCN 3.2.1 register database.
- Diff repeated instances, especially `MPCC_MCM0` versus `MPCC_MCM1`, and continue into later chunks for `MPCC_MCM2` and `MPCC_MCM3`.
- Verify that each complete field has a non-overlapping mask and matching shift, allowing for the intentional incomplete first and last register groups.
- Cross-check adjacent ASIC generation headers only after accounting for intended generation-specific color-pipeline differences.

Runtime signals include successful modesets on DCN 3.2.1 hardware, correct color output with shaper LUT, 1D LUT, 3D LUT, and gamut/color transforms enabled, stable transitions between LUT RAM banks, correct readback of current mode and memory power state fields, and no visual artifacts across suspend/resume, hotplug, multi-monitor, and runtime power-management transitions.

## Research Notes

This is source-tree-aligned chunk research only. It intentionally writes only `Docs/researches/chunks/subset-b-002034_research.md`. Whole-file research for `dcn_3_2_1_sh_mask.h` must merge adjacent chunks to complete the preceding `MPCC_OGAM3` gamut-remap block and the following `MPCC_MCM2` register block.

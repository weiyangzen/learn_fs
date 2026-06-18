# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 20173-22680

## Scope And Purpose

This chunk is part of AMD's generated DCN 3.2.0 register shift/mask header. It contains C preprocessor constants for bitfield shifts and masks, not executable code. The constants describe hardware register layouts used by the AMDGPU display stack when programming DCN display blocks through register helper macros.

The range starts in the middle of the `dcn_dc_mpc_mpcc_mcm2_dispdec` register block, covering the tail of MPCC MCM2 1D LUT RAM A and RAM B controls. It then covers the full `dcn_dc_mpc_mpcc_mcm3_dispdec` block, the `dcn_dc_mpc_mpc_ocsc_dispdec` output color-space-conversion block, and the beginning of OPP adaptive backlight management blocks `dcn_dc_opp_abm0_dispdec`, `dcn_dc_opp_abm1_dispdec`, and `dcn_dc_opp_abm2_dispdec`.

The chunk defines 2,093 macros over 401 register names. Nearly every field has a paired `__SHIFT` and `_MASK` macro; the few apparent count differences are because this chunk starts and ends inside larger register sections. The main prefix families are `MPCC` for multi-plane compositor color management, `MPC` for output mux/denorm/CSC, and `ABM0`/`ABM1`/`ABM2` for adaptive backlight and histogram/light-sensor registers.

## Important Constants And Register Areas

The `MPCC_MCM2_*` tail covers 1D LUT RAM A region entries `REGION_2_3` through `REGION_32_33`, then RAM B start, slope, base, end, offset, and region controls. These constants describe per-channel RGB LUT start/end values, slopes, bases, offsets, and repeated region descriptors. Region registers pack two regions per register, using low fields for the first region and high fields for the next, for example LUT offset fields at bit 0 and bit 16 and segment-count fields at bit 12 and bit 28.

The `MPCC_MCM2_MPCC_MCM_MEM_PWR_CTRL` register exposes memory power-control fields for shaper RAM, 3D LUT RAM, and 1D LUT RAM A/B. These fields are integration-sensitive because they control low-power state, light sleep, deep sleep, shutdown, and power-status signaling for color-management memories.

The `MPCC_MCM3_*` block repeats the color-management programming surface for MPCC instance 3. It includes shaper controls, shaper offsets/scales, shaper LUT index/data/write-enable masks, shaper RAM A/B region programming, 3D LUT mode/index/data/read-write-control/output normalization/output offsets, 1D LUT mode/index/data/control, 1D LUT RAM A/B start/end/offset/region programming, and its own `MPCC_MCM3_MPCC_MCM_MEM_PWR_CTRL`.

The `MPC_OUT*` block covers output muxing and output color conversion for four MPC outputs. `MPC_OUT0_MUX` through `MPC_OUT3_MUX` select sources and stereo/secondary sources for each output. Denormalization controls and clamp registers expose pixel-format selection and clamp bounds for green/luma and blue/chroma channels. The CSC area defines coefficient-format control plus per-output CSC mode and matrix coefficient registers for coefficient sets A and B.

The `ABM0_*` and `ABM1_*` blocks are complete copies for adaptive backlight manager instances 0 and 1. They cover PWM ambient/user/target/current/final/minimum duty levels, ABM enable and auto-update controls, sample-rate controls, grouped register locking, ABM enable/bypass, input color-space coefficient selection, ACE offset/slope and threshold tables, missed-frame status/clear bits, HGLS read progress, histogram control, light-sensor luma statistics, histogram and light-sensor sampling controls, histogram bin shift flags/indexes, 24 histogram result registers, and a backlight master lock bit.

The `ABM2_*` block begins the same pattern for instance 2, from PWM level registers through `ABM2_DC_ABM1_HG_MISC_CTRL`. This chunk ends at the start of the `HG_MISC_CTRL` mask definitions, so the rest of ABM2 histogram, light-sensor, and result registers are expected in the next chunk.

## APIs, Types, And Functions

There are no functions, structs, enums, inline helpers, or exported symbols in this range. The public surface is a dense set of preprocessor definitions named using AMD's generated convention:

- `REGISTER__FIELD__SHIFT` gives the right-shift amount for a field.
- `REGISTER__FIELD_MASK` gives the already-positioned bitmask for the same field.
- Comment lines of the form `//REGISTER` and `// addressBlock: ...` group definitions by hardware register and decoded address block.

These constants are consumed indirectly by display driver register helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, field-list macros, and ASIC-specific register tables. The same header is included by DCN 3.2 display resource, clock, GPIO, IRQ, DMUB, and GMC paths, so changes here affect compile-time register programming across several display subsystems.

## Control Flow And Runtime Behavior

This chunk has no local control flow. Runtime behavior emerges when driver code uses these masks and shifts to read or write memory-mapped hardware registers.

For MPCC MCM programming, driver flows that configure shaper LUTs, 3D LUTs, 1D LUTs, or memory power states use these constants to pack mode, index, data, region, and power-control fields into register writes. The repeated RAM A/RAM B region fields encode piecewise LUT segmentation; incorrect packing can alter color pipeline transfer functions or corrupt the active/inactive LUT buffer selection.

For MPC output programming, driver flows that route MPC output sources, select denormalization formats, clamp output values, and program CSC matrices use this block to select source muxes and set matrix coefficient registers. The A/B coefficient register pairs imply double-buffered or selectable coefficient banks that must match the driver's update sequencing.

For ABM programming, runtime paths that manage panel backlight, ambient-light response, ACE curves, histogram/light-sensor accumulation, and register update locks use these constants to coordinate frame-boundary updates and readback. Several fields explicitly track pending updates, missed-frame events, register locks, master-lock bypasses, and clear bits.

## State And Persistence

The file itself stores no mutable state. Its constants define hardware state layout. Persistence is therefore in the DCN register file and display hardware, not in software data structures.

Stateful hardware areas represented in this chunk include MPCC color-management RAMs, shaper/1D/3D LUT indices and data ports, MPC output source selection and CSC coefficients, ABM PWM duty-cycle values, ACE thresholds, histogram bins/results, light-sensor accumulation registers, lock bits, update-pending bits, missed-frame latches, and memory power-state controls. These values can persist across frames and sometimes across low-power transitions until explicitly rewritten or reset by display initialization paths.

The lock and update fields are especially important state markers. `*_REG_LOCK`, `*_UPDATE_PENDING`, `*_UPDATE_AT_FRAME_START`, `*_READBACK_DB_REG_VALUE_EN`, `*_IGNORE_MASTER_LOCK_EN`, and missed-frame clear fields describe synchronization behavior between CPU register writes and display frame timing.

## Dependencies And Integration Points

This header is ASIC-specific generated data for DCN 3.2.0 and depends on matching register-address definitions elsewhere in the same generated include tree. The shift/mask macros are only correct when paired with the corresponding DCN 3.2.0 register offsets.

Direct include points found in this repository include:

- `drivers/gpu/drm/amd/amdgpu/gmc_v11_0.c`
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c`
- `drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c`
- `drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c`
- `drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`
- `drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_translate_dcn32.c`
- `drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_factory_dcn32.c`

The constants also mirror similar fields in other generated DCN headers such as DCN 3.1.2 and DCN 3.5.1, which is useful for spotting intentional hardware-generation differences versus accidental generator drift.

## Risks And Edge Cases

The primary risk is silent register corruption from an incorrect shift or mask. Since these are compile-time constants, a wrong value usually compiles cleanly but causes runtime display defects: wrong color conversion, broken LUT programming, failed backlight updates, stuck update-pending bits, missed-frame status that cannot be cleared, or invalid memory power transitions.

The chunk boundaries are a research risk: line 20173 starts after the first `MPCC_MCM2_MPCC_MCM_1DLUT_RAMA_REGION_0_1` definitions, and line 22680 ends before the full `ABM2_DC_ABM1_HG_MISC_CTRL` register and the remaining ABM2 register set. Any per-file reconciliation must merge adjacent chunks before drawing whole-file conclusions about complete register coverage.

Generated headers are also sensitive to naming stability. Driver code and register-list macros may form token names mechanically; renaming a field, changing a prefix, or changing a duplicated instance pattern can break builds even if the numeric value is unchanged.

Fields controlling locks and frame-start updates carry sequencing risk. Writing ABM or LUT fields without respecting lock/update bits can produce visible tearing, stale readback values, or missed-frame indicators. Memory power fields are similarly risky because entering sleep/shutdown while a LUT path is in use can cause hardware faults or visual corruption.

## Test And Validation Signals

Basic validation is compile-time: all DCN 3.2 display, DMUB, GPIO, IRQ, clock, and GMC users must still compile with this header. Because the macros are pure preprocessor constants, missing or renamed macros usually surface as build errors in the relevant ASIC-specific C files.

Runtime test signals include display bring-up on DCN 3.2 hardware, mode-set stability, color-management validation for shaper LUT, 1D LUT, 3D LUT, and output CSC programming, and panel backlight behavior when ABM is enabled, disabled, or driven by ambient-light inputs.

For register-definition changes, useful regression checks include comparing this generated header against the authoritative hardware register database, diffing repeated instances (`MPCC_MCM2` versus `MPCC_MCM3`, `ABM0` versus `ABM1` versus `ABM2`), and checking adjacent DCN generations for expected field-width differences. Hardware readback tests should focus on lock/update-pending bits, missed-frame clear bits, histogram result accumulation, PWM duty-cycle fields, and color-management RAM power-state fields.

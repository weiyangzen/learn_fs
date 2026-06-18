# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 59768-62225

## Scope And Purpose

This chunk is part of the generated DCN 4.2.0 register shift/mask header used by the AMD display driver. It contains only preprocessor constants, not executable control flow. The constants define bit positions and masks for hardware register fields so the display code can issue safe read-modify-write operations through `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, and the `SF(...)` register-table macros.

The range starts at the tail of the `DC_PERFMON22` performance monitor block, then covers the `dce_dc_mpc_mpcc_mcm0_dispdec` and `dce_dc_mpc_mpcc_mcm1_dispdec` address blocks for MPCC movable color-management hardware, and ends partway through `dce_dc_mpc_mpcc_mcm2_dispdec` shaper RAM A region definitions. The MPCC MCM blocks describe color pipeline controls behind the MPC/MPCC path: shaper LUTs, 3D LUTs, post 1D LUTs, two gamut remap matrices, LUT memory power control, and 3D LUT fast-load status.

Because this is a generated `*_sh_mask.h` file, the semantic contract is the exact pairing of every `__SHIFT` value with its corresponding `_MASK` value and the exact register/field names consumed by the DCN42 object headers. A mismatch here does not fail locally in this header; it causes later register writes to touch the wrong hardware bits.

## Important Register Families

`DC_PERFMON22_*` fields complete one display-core performance monitor instance. The visible registers include:

- `DC_PERFMON22_PERFCOUNTER_STATE`, with eight packed counter-state fields and state-select bits.
- `DC_PERFMON22_PERFMON_CNTL` and `DC_PERFMON22_PERFMON_CNTL2`, controlling monitor state, report count, count-off interrupt enable/status/ack, clock enable, run-enable start/stop selectors, and interrupt type.
- `DC_PERFMON22_PERFMON_CVALUE_INT_MISC`, packing per-counter interrupt status and ack bits plus the high bits of the current value.
- `DC_PERFMON22_PERFMON_CVALUE_LOW`, `DC_PERFMON22_PERFMON_HI`, and `DC_PERFMON22_PERFMON_LOW`, exposing counter value and read-selection fields.

`MPCC_MCM0_*` and `MPCC_MCM1_*` are full repeated MPCC MCM instances. Each instance includes the same broad field groups:

- Shaper control and LUT programming: `MPCC_MCM_SHAPER_LUT_MODE`, current mode, per-channel offsets/scales, LUT index/data, write color mask, RAM select, RAM A/B start/end controls, and RAM A/B region descriptors.
- `MPCC_MCM_3DLUT_*`: mode, size, current mode, index, 24-bit and 30-bit data paths, read/write controls, output normalization, per-channel output offset/scale, fast-load source selection, and fast-load status bits for done, soft underflow, and hard underflow.
- `MPCC_MCM_1DLUT_*`: mode/select/current mode, LUT index/data/control, RAM A/B start and end controls, region slope/base/offset fields, and region descriptor pairs from region 0/1 through 32/33.
- First and second gamut remap controls: coefficient format, mode/current mode, and packed matrix coefficients `C11` through `C34` for banks A and B.
- `MPCC_MCM_MEM_PWR_CTRL`: force, disable, low-power-mode, and power-state fields for shaper, 3DLUT, and 1DLUT memories.

`MPCC_MCM2_*` begins another repeated instance, but this chunk only covers the shaper setup through `MPCC_MCM2_MPCC_MCM_SHAPER_RAMA_REGION_26_27`. Its remaining RAM A fields, RAM B fields, 3DLUT, 1DLUT, gamut remap, and memory-power definitions fall outside this chunk.

## APIs, Types, And Integration

The header does not define C types or functions directly. Its API surface is the macro naming convention:

- `REGISTER__FIELD__SHIFT` gives the field shift used to position a value.
- `REGISTER__FIELD_MASK` gives the field mask used for extraction or read-modify-write preservation.

The main DCN42 integration point is `drivers/gpu/drm/amd/display/dc/mpc/dcn42/dcn42_mpc.h`. `MPC_COMMON_MASK_SH_LIST_DCN42(mask_sh)` references many fields from this chunk through `SF(MPCC_MCM0_..., FIELD, mask_sh)`. `drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.c` then instantiates:

- `static const struct dcn42_mpc_shift mpc_shift = { MPC_COMMON_MASK_SH_LIST_DCN42(__SHIFT) };`
- `static const struct dcn42_mpc_mask mpc_mask = { MPC_COMMON_MASK_SH_LIST_DCN42(_MASK) };`

At runtime, `dcn42_mpc_construct()` stores those tables in `struct dcn42_mpc`. MPC programming code then expands `FN(reg, field)` into `mpc42->mpc_shift->field` and `mpc42->mpc_mask->field`.

The actual programming paths are mostly in shared DCN32/DCN401 MPC code plus DCN42-specific RMCM code. Examples include shaper and post-1DLUT programming, 3DLUT programming, gamut remap programming, LUT fast-load setup, memory-power handling, and state readback. These paths depend on the generated macros in this chunk to address the right bits while writing `MPCC_MCM_*` registers.

The `DC_PERFMON22` definitions integrate with display performance-monitor and debug tooling through the same generated register model. This chunk provides field layout only; address constants live in `dcn_4_2_0_offset.h`, and enum values for performance events live in the SoC enum headers.

## Control Flow

There is no runtime control flow in this chunk. The effective flow is compile-time data generation:

1. The generated header exposes register-field shifts and masks.
2. DCN42 object headers collect selected fields into per-block shift and mask structs using `SF(...)`.
3. Resource construction binds register addresses, shifts, and masks into hardware objects.
4. Runtime display code calls register helper macros such as `REG_SET`, `REG_UPDATE`, `REG_UPDATE_2`, `REG_GET`, and `REG_WAIT`.
5. Those helpers combine the address from `*_offset.h` with shift/mask constants from this header to modify or read the intended field.

For the MCM color pipeline, the runtime sequence usually powers/ungates the relevant memory, selects a target RAM bank, writes index/data registers or matrix coefficient registers, switches mode/select fields, and later reads current-mode/status fields to confirm state. For 3DLUT fast load, the driver programs fast-load source selection and checks done/underflow status. For memory power, the driver writes disable/force/low-power-mode fields and may wait for power-state fields.

## State And Persistence Behavior

The header has no mutable state and performs no persistence. Persistence is entirely in hardware registers programmed through these definitions.

The fields in this chunk describe several hardware state classes:

- Performance monitor state: counter state, current values, interrupt status, interrupt ack, and monitor clock/run-enable controls.
- Active color-processing state: current shaper, 3DLUT, 1DLUT, and gamut-remap modes; selected LUT banks; coefficient formats; and selected fast-load source.
- LUT contents and region configuration: shaper/1DLUT RAM A/B region tables, LUT index/data ports, 3DLUT data ports, and output normalization/offset/scale fields.
- Power state: shaper, 3DLUT, and 1DLUT memory force/disable/low-power configuration plus readback state.

Many MCM registers are banked as RAM A/RAM B or matrix bank A/B. That banked layout lets software populate an inactive bank and flip a mode/select field after programming, reducing visible color-pipeline disruption. The generated masks must preserve that bank distinction precisely.

## Dependencies

This chunk depends on the generated DCN 4.2.0 register-address header for register offsets and base indices. It also depends on the AMD display register-helper framework that interprets shift/mask pairs.

Important local consumers include:

- `drivers/gpu/drm/amd/display/dc/mpc/dcn42/dcn42_mpc.h`, which names the MPCC MCM fields included in `struct dcn42_mpc_shift` and `struct dcn42_mpc_mask`.
- `drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.c`, which includes `dcn_4_2_0_sh_mask.h`, instantiates the shift/mask tables, and constructs the MPC object.
- `drivers/gpu/drm/amd/display/dc/mpc/dcn42/dcn42_mpc.c`, which uses those tables for DCN42 RMCM and MPCC state handling.
- Shared MPC implementations under `drivers/gpu/drm/amd/display/dc/mpc/dcn32` and `dcn401`, which program shaper, 3DLUT, 1DLUT, gamut remap, fast-load, and memory-power paths through the same abstract field names.

The repeated `MPCC_MCM0`, `MPCC_MCM1`, and `MPCC_MCM2` prefixes encode hardware instances. Driver arrays indexed by `mpcc_id` assume register lists, offset lists, and shift/mask definitions remain aligned across those repeated instances.

## Risks And Edge Cases

Generated-header drift is the main risk. If a register name or field name changes here but the DCN42 `SF(...)` list is not updated, compilation fails. If a shift or mask value is wrong but the name still matches, compilation succeeds and hardware programming corrupts adjacent fields.

Partial instance coverage matters for chunking. This range contains full MCM0 and MCM1 definitions but only the beginning of MCM2. Any per-file synthesis must merge the following chunk before claiming complete MCM2 behavior.

Packed channel fields are easy to misuse. Several registers pack two fields into one word, such as G/B scale fields, 3DLUT data lanes, output offset/scale pairs, gamut coefficients, and region pairs. Incorrect masks can silently swap or truncate color values.

Bank-selection and current-mode fields are sensitive. The shaper, 1DLUT, 3DLUT, and gamut-remap paths use mode/current and select/current pairs to avoid switching to partially programmed RAM. Programming the wrong bank select or using a stale current-mode field can produce visible color corruption or a black screen.

Memory-power fields must stay consistent with programming sequences. The runtime code may force or disable MCM memories, then wait for power-state fields before programming or enabling a LUT. Bad masks in `MPCC_MCM_MEM_PWR_CTRL` can leave LUT RAM powered down, prevent low-power entry, or make readback diagnostics misleading.

3DLUT fast-load status includes done, soft-underflow, and hard-underflow bits. If these masks are wrong, fast-load workflows can falsely report success or miss underflow, leading to incomplete LUT contents being used.

Performance-monitor fields include write-ack interrupt bits and packed high/low counter values. Incorrect ack masks can fail to clear interrupts; incorrect high/low extraction can make debug counters unreliable.

## Test Signals

Build coverage should compile DCN42 display code with `dcn_4_2_0_sh_mask.h` included by `dcn42_resource.c`, `dcn42_mpc.h`, and related hardware object sources. A missing or renamed macro in this chunk should fail at the shift/mask table initializers.

Runtime validation should focus on hardware-visible color and state-readback paths:

- Program shaper LUTs on MPCC MCM0 and MCM1 with both RAM A and RAM B, then verify current mode/select readback and color output.
- Program 3DLUT in 24-bit and 30-bit modes, including output offset/scale, fast-load source selection, and fast-load done/underflow status.
- Program post 1DLUT RAM A/B region tables and LUT data, then verify region boundaries and per-channel writes.
- Exercise first and second gamut-remap matrices with bank A/B coefficients and confirm mode/current-mode readback.
- Toggle MCM memory power controls and check power-state readback, especially around LUT programming sequences.
- Read MPCC state through DCN42 debug/readback paths and confirm MCM state fields decode consistently.
- Use display CRC or visual test patterns to catch color-channel swaps, coefficient packing mistakes, truncated LUT data, and wrong bank selection.
- Exercise `DC_PERFMON22` counters and interrupt ack/status paths through display performance-monitor/debug tooling, checking counter value consistency and interrupt clearing.

Good regression symptoms to watch for are compile failures in `MPC_COMMON_MASK_SH_LIST_DCN42`, incorrect colors after applying LUTs or gamut remap, LUT fast-load underflow not reported, hangs while waiting for memory power state, unexpected power residency changes, and misleading MPCC/perfmon debug readouts.

## Cross-Chunk Notes

The preceding chunk contains the start of the `DC_PERFMON22` block, including at least `PERFCOUNTER_CNTL` and `PERFCOUNTER_CNTL2`. This chunk starts at `DC_PERFMON22_PERFCOUNTER_STATE`.

The following chunk is required for a complete `MPCC_MCM2` description. This chunk stops after `MPCC_MCM2_MPCC_MCM_SHAPER_RAMA_REGION_26_27`; later MCM2 shaper region definitions, RAM B definitions, 3DLUT/1DLUT/gamut-remap definitions, memory-power fields, and fast-load fields are outside this range.

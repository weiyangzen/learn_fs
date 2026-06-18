# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 48831-51051

## Purpose

This chunk is generated AMD DCN 3.5.1 register field metadata for the MPCC MCM color-management block. It contains no executable logic; it exports preprocessor constants that define field shifts and masks for MMIO registers. The constants are paired with the corresponding DCN 3.5.1 offset header and consumed by AMD display register helpers to read, write, and update individual hardware fields.

The requested range covers the tail of the `MPCC_MCM1` block, the full `MPCC_MCM2` block, and most of the `MPCC_MCM3` block. These MPCC instances expose shaper LUT control, shaper RAM A/B piecewise regions, 3D LUT programming, 1D LUT programming, LUT RAM A/B region descriptors, and memory power controls. Although this repository path is under a local `ceph-client` mirror, this source is AMDGPU display hardware metadata and is unrelated to Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, callbacks, locks, allocations, or includes in this range. The exported interface is entirely generated macros:

- `MPCC_MCM*_REGISTER__FIELD__SHIFT`: the bit position for a field in an MPCC MCM register.
- `MPCC_MCM*_REGISTER__FIELD_MASK`: the bit mask for the same field.

Major macro families in this chunk:

- `MPCC_MCM1` tail: starts inside `MPCC_MCM_SHAPER_RAMA_REGION_12_13`, then completes shaper RAMA regions through `32_33`, all shaper RAMB start/end/region descriptors, 3D LUT control/data registers, 1D LUT control/data/register programming, 1D LUT RAMA/RAMB start/end/offset/region descriptors, and `MPCC_MCM_MEM_PWR_CTRL`.
- `MPCC_MCM2`: complete instance-local definitions for shaper control, shaper LUT index/data/write-enable/mode/selection/scales/offsets, shaper RAMA/RAMB start/end/region descriptors, 3D LUT mode/index/data/30-bit/read-write/norm-factor/output-offset fields, 1D LUT control/index/data/LUT-control fields, 1D LUT RAMA/RAMB start/end/slope/base/offset/region descriptors, and memory power control/state fields.
- `MPCC_MCM3`: complete definitions from shaper control through `MPCC_MCM_1DLUT_RAMB_REGION_20_21`, then starts `MPCC_MCM_1DLUT_RAMB_REGION_22_23` with shift fields only before the requested range ends.

Important represented fields include LUT bypass/mode/select/current status, read/write selection, host access selection, write color masks, LUT indices/data payloads, 3D LUT size/RAM select/config status/30-bit enable, output normalization and RGB offsets, per-channel shaper and 1D LUT start/end/base/slope/offset values, per-region LUT offsets and segment counts for regions 0 through 33, and low-power/power-disable/power-state fields for shaper, 3D LUT, and 1D LUT memories.

The repeated region registers use a consistent packed layout. For most `REGION_N_N` pairs, region N uses LUT offset bits starting at shift `0x0` and segment-count bits at `0xc`; region N+1 uses LUT offset bits at `0x10` and segment-count bits at `0x1c`. Masks are typically `0x000001FFL`, `0x00007000L`, `0x01FF0000L`, and `0x70000000L` for the four packed fields.

## Control Flow

This header has no runtime control flow. Runtime behavior comes from the display driver code that includes this generated metadata:

1. DCN 3.5.1 code includes `dcn_3_5_1_sh_mask.h` with the matching register offset header.
2. Register-list and field-list macros token-paste register and field names into per-block register, shift, and mask tables.
3. Runtime MPC/color-management code calls helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_2`, `REG_WAIT`, and table-building macros such as `SF`/`SRII`.
4. Those helpers use these shift/mask constants to isolate, compose, and preserve fields during MMIO read-modify-write sequences.

The implied runtime flows are MPCC MCM color-pipeline programming: selecting shaper and 1D LUT RAM banks, loading LUT entries through host-visible index/data windows, programming piecewise-linear region boundaries and segment counts, enabling or bypassing shaper/1D/3D LUTs, setting 3D LUT dimensions and precision, applying RGB output offsets, and managing SRAM power state around LUT use.

## State And Persistence Behavior

The chunk stores no software state and persists nothing on its own. It describes MMIO-backed GPU display state.

Represented hardware state includes active/pending LUT modes, selected RAM banks, current in-use RAM selections, LUT host access routing, 1D and shaper RAM contents through index/data windows, region geometry for piecewise LUT interpolation, RGB start/end/base/slope/offset values, 3D LUT configuration and data payloads, normalization factors, output offsets, and memory power force/disable/state bits.

Persistence is determined by the MPCC MCM hardware block. Control fields usually remain in hardware until reprogrammed, modeset, power-gate transition, suspend/resume, display reset, or ASIC reset. LUT RAM contents and region descriptors may be lost or invalid while the relevant memory is disabled or in a low-power state. Current/status fields are hardware-reflected and may lag requested state until the block has accepted new programming.

## Dependencies And Integration Points

This chunk depends on AMD's generated register database and must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_offset.h`, which provides the corresponding MMIO offsets and instance selectors.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc24_enum.h`, which defines symbolic values for MPCC MCM LUT modes, RAM selection, LUT segment counts, 3D LUT size/bit-depth, gamut remap modes, and memory power states.
- AMD display register helper infrastructure used by MPC/resource code to turn generated shift/mask macros into typed register tables.

Representative integration points in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn351.c`, which includes the DCN 3.5.1 offset and mask headers.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn32/dcn32_mpc.c`, where MPCC MCM fields are used for 1D LUT power control, LUT RAM selection, region programming, and shaper/3D LUT behavior inherited by later DCN versions.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.h`, which lists MPCC MCM register instances and fields for resource construction.
- DRM color-management paths such as `amdgpu_dm_color.c` and `amdgpu_dm_colorop.c`, which feed shaper LUT, 3D LUT, transfer-function, and plane color-operation state into lower-level DC programming.

The later merge lane should combine this with adjacent chunks because this range starts in the middle of `MPCC_MCM1_MPCC_MCM_SHAPER_RAMA_REGION_12_13` and ends in the middle of `MPCC_MCM3_MPCC_MCM_1DLUT_RAMB_REGION_22_23`.

## Risks And Edge Cases

- Shift/mask drift is the primary risk. These untyped constants can compile successfully while targeting the wrong hardware bits, causing subtle color-management failures.
- The repeated MPCC instances are copy-sensitive. `MPCC_MCM2` and `MPCC_MCM3` should be structurally equivalent; an instance-specific typo can affect only one blending/composition pipe and be missed by simple single-plane or single-display testing.
- The requested chunk has artificial boundaries. `MPCC_MCM1_SHAPER_RAMA_REGION_12_13` is missing its first shift definition from this range, and `MPCC_MCM3_1DLUT_RAMB_REGION_22_23` has shifts without the matching masks here. Complete validation needs adjacent chunks.
- Packed region descriptors are easy to corrupt. Bad LUT offset or segment-count masks can load the wrong piecewise region boundaries, producing banding, clipping, non-monotonic transfer curves, or channel-specific color errors.
- Host index/data programming is sequencing-sensitive. Wrong index, data, RAM-select, host-select, or write-color-mask fields can write the wrong RAM bank, wrong channel, or wrong LUT entry.
- Current/select status fields can be confused with request fields. Code must distinguish requested RAM/mode selections from hardware-current status before flipping active LUT banks.
- Memory power fields affect availability of LUT SRAMs. Incorrect power-disable/force/low-power masks can lose LUT contents, make writes ineffective, or cause `REG_WAIT` timeouts while waiting for power state.
- 3D LUT precision and size fields are compact control bits. Wrong masks can select the wrong cube size, 30-bit mode, RAM target, or read/write behavior, causing visible color transforms to differ from DRM color state.

## Test Signals

Useful validation signals combine generated-header checks and display color behavior:

- Build AMDGPU/DCN 3.5.1 paths with register-table construction enabled; missing or malformed macros should fail at compile time where `SF`, `SRII`, or `REG_*` users reference them.
- Mechanically verify each complete register group in this range has paired `__SHIFT` and `_MASK` definitions and that masks align with expected shifts and field widths. Exclude the known partial boundary groups until adjacent chunks are merged.
- Diff `MPCC_MCM2` and `MPCC_MCM3` definitions against each other and against nearby generated DCN generations, especially DCN 3.2/3.5 MPCC MCM headers, where most field layouts are expected to remain stable.
- Exercise DRM plane color pipelines that use shaper LUT, 3D LUT, and 1D LUT programming: bypass modes, identity LUTs, nontrivial transfer functions, per-channel curves, 17-cube 3D LUTs, and RAM bank flips.
- Validate visible output with color ramps and calibration patterns for banding, clipping, wrong channel mapping, wrong gamma, stale LUT contents, and differences between MPCC instances.
- Test modeset, plane enable/disable, atomic color property updates, suspend/resume, and display hotplug while color transforms are active to catch lost SRAM contents or incorrect power-state handling.
- Monitor kernel logs and DC debug output for register wait timeouts, color-management programming failures, blank frames during LUT updates, and mismatches between requested and current LUT mode/RAM selection.

## Cross-Chunk Notes

The previous chunk owns the beginning of `MPCC_MCM1`, including the omitted start of `MPCC_MCM1_MPCC_MCM_SHAPER_RAMA_REGION_12_13`. The next chunk owns the rest of `MPCC_MCM3_MPCC_MCM_1DLUT_RAMB_REGION_22_23`, later `MPCC_MCM3` region descriptors, and any remaining MPCC MCM fields. The final per-file report should merge those adjacent ranges before making complete claims about all MPCC MCM instance definitions in `dcn_3_5_1_sh_mask.h`.

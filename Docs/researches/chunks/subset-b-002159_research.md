# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 20194-22656

## Scope

This chunk is a generated-register slice of AMDGPU's DCN 4.1.0 shift/mask header. It contains C preprocessor constants only: no functions, structs, enums, storage objects, or local executable control flow. The public contract is the generated `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macro namespace used by display register-table initializers and MMIO field helpers.

The range starts at the tail of `MPCC_MCM0_MPCC_MCM_SHAPER_RAMB_REGION_28_29`, then completes the rest of the MPCC MCM0 color-management block. It then covers the complete `dcn_dcec_mpc_mpcc_mcm1_dispdec` address block and starts `dcn_dcec_mpc_mpcc_mcm2_dispdec`, ending in `MPCC_MCM2_MPCC_MCM_1DLUT_RAMA_REGION_28_29`. Adjacent chunks own the beginning of MCM0 shaper RAMB and the rest of MCM2 1D LUT RAMA/RAMB and later registers.

Although the repository path is under `sources/distributed-fs/ceph-client`, this source is AMD display hardware metadata. It has no Ceph, filesystem, distributed-storage, network, or persistent-disk behavior.

## Purpose

The purpose of this header range is to describe the exact bit positions and masks for Multi-Plane Compositor color-management (MPCC MCM) registers on DCN 4.1.0 hardware. Runtime display code uses these constants with companion register offsets to program per-MPCC shaper LUTs, 3D LUTs, 1D LUTs, gamut-remap matrices, memory-power controls, and fast-load status.

The covered hardware areas are:

- `MPCC_MCM0` tail: shaper RAMB region-pair descriptors for regions 30-33, 3D LUT mode/index/data/control/output normalization and offsets, 1D LUT control/index/data/control, 1D LUT RAM A/B PWL start/end/slope/base/offset registers, RAM A/B region-pair descriptors for regions 0-33, first and second gamut-remap coefficient format/mode/matrix coefficients for banks A/B, MCM memory power control, and 3D LUT fast-load select/status.
- `MPCC_MCM1`: full shaper control, shaper offsets/scales, shaper LUT index/data/write controls, shaper RAM A/B PWL descriptors and regions 0-33, 3D LUT controls/data/output factors, 1D LUT controls and RAM A/B descriptors, first and second gamut remap controls/matrices, memory power controls, and 3D LUT fast-load controls/status.
- `MPCC_MCM2` beginning: shaper controls, shaper RAM A/B descriptors and region-pair registers, 3D LUT controls/data/output factors, 1D LUT controls, and 1D LUT RAM A descriptors through region pair 28-29.

## Important APIs, Types, And Macros

There are no callable APIs or concrete types in this chunk. The interface is the generated macro pattern:

- `*_SHIFT` gives a register field's least-significant bit position.
- `*_MASK` gives the field mask already shifted into its register position.
- Register names encode both the hardware block and MPCC instance, such as `MPCC_MCM0_MPCC_MCM_3DLUT_MODE`, `MPCC_MCM1_MPCC_MCM_1DLUT_RAMB_REGION_32_33`, and `MPCC_MCM2_MPCC_MCM_SHAPER_RAMA_REGION_0_1`.

The shaper groups define the front-end transfer stage in the MPCC MCM path. Control fields include `MPCC_MCM_SHAPER_LUT_MODE` and `MPCC_MCM_SHAPER_MODE_CURRENT`; offset and scale fields use per-channel R/G/B masks; the indexed LUT interface exposes `MPCC_MCM_SHAPER_LUT_INDEX`, `MPCC_MCM_SHAPER_LUT_DATA`, `MPCC_MCM_SHAPER_LUT_WRITE_EN_MASK`, and `MPCC_MCM_SHAPER_LUT_WRITE_SEL`. RAM A and RAM B each have start, end, and region-pair registers. Region-pair registers pack two PWL region descriptors into one register using `LUT_OFFSET` at bits 0/16 and `NUM_SEGMENTS` at bits 12/28.

The 3D LUT groups define `MPCC_MCM_3DLUT_MODE`, `MPCC_MCM_3DLUT_SIZE`, current-mode readback, an 11-bit index field, packed 16-bit data words, an alternate 30-bit data path, RAM select, 30-bit enable, read selection, output normalization, and per-channel output offset/scale. The fast-load group adds `MPCC_MCM_3DLUT_FL_SEL`, `MPCC_MCM_3DLUT_FL_DONE`, and soft/hard underflow status fields.

The 1D LUT groups define mode/select/current readback, PWL disable, LUT index/data, LUT write color mask, read color selection, debug read, host RAM select, and config mode. RAM A and RAM B duplicate the PWL region metadata: per-channel start point, start segment, start slope, start base, end base, end value, end slope, offset, and region-pair descriptors from 0-1 through 32-33 where complete in this chunk.

The gamut remap groups define two matrix stages. Each stage has a coefficient-format bit, a mode field, a current-mode readback field, and banks A/B of packed coefficient-pair registers: `C11_C12`, `C13_C14`, `C21_C22`, `C23_C24`, `C31_C32`, and `C33_C34`. Each pair stores two 16-bit coefficients in one 32-bit register.

The memory-power control fields describe force, disable, low-power-mode, and state bits for shaper, 3D LUT, and 1D LUT memories. These fields are visible for MCM0 and MCM1 in this slice and are used by runtime power-management paths that gate MPCC color-management memories.

## Control Flow

This header has no local control flow. Runtime behavior is created by consumers that include `dcn_4_1_0_offset.h` and `dcn_4_1_0_sh_mask.h`, expand register/field table macros, and then use register helper operations such as `REG_SET`, `REG_UPDATE`, `REG_UPDATE_2`, `REG_SET_4`, `REG_GET`, and `REG_WAIT`.

A typical use path is:

1. DCN401 resource construction includes the DCN 4.1.0 offset and shift/mask headers and uses token-pasting macros such as `SRI_ARR` and field-list macros to bind logical MPCC MCM register names to generated instance offsets, masks, and shifts.
2. MPC/DPP shared color-management code selects an MPCC instance and programs shaper, 1D LUT, 3D LUT, gamut remap, and memory-power registers through helper macros, using the field geometry from this header.
3. LUT programming sequences select RAM A or RAM B, set index registers, write channel data, program PWL region descriptors, and switch mode/select fields only after the target bank is ready.
4. Status paths read current-mode/current-select, memory-power state, fast-load done, and underflow fields to confirm the hardware state or debug failures.

Visible integration patterns in this tree include `display/dc/resource/dcn401/dcn401_resource.c`, which includes this generated header and builds register tables from generated offsets and fields; `display/dmub/src/dmub_dcn401.c`, which initializes DMUB register masks and shifts through `FD_MASK` and `FD_SHIFT`; and shared MPC color code under `display/dc/mpc/dcn32/dcn32_mpc.c`, which uses `MPCC_MCM_*` register and field names to program MPCC MCM memories, 1D LUTs, shaper LUTs, and power state.

## State And Persistence Behavior

The file itself stores no mutable runtime state and persists nothing. It describes hardware register state whose lifetime is managed by display pipe programming, modesets, plane updates, color-management updates, memory-power transitions, suspend/resume restore, and GPU reset.

State represented by this chunk includes:

- Shaper LUT mode, current-mode status, indexed LUT contents, per-channel offsets/scales, RAM A/B region descriptors, and PWL curve endpoints.
- 3D LUT mode, size, active/current mode, indexed table data, RAM selection, 30-bit access mode, read selector, output normalization, output offsets/scales, fast-load selection, completion, and underflow status.
- 1D LUT active mode/select, current mode/select readback, PWL disable, indexed LUT contents, write masks, host RAM selection, config/read controls, RAM A/B PWL region descriptors, and per-channel offsets.
- First and second gamut-remap matrix format, active/current modes, and two coefficient banks for each remap stage.
- Memory-power controls and state bits for shaper, 3D LUT, and 1D LUT SRAMs.

Several fields are status-like readbacks rather than pure programming knobs, including `*_MODE_CURRENT`, `*_SELECT_CURRENT`, `*_MEM_PWR_STATE`, fast-load done, and underflow status. Indexed LUT and RAM-region registers are stateful because the selected index, selected RAM bank, and write color mask determine which table entries later writes affect. Incorrect values can remain active until the MPCC MCM instance is reprogrammed, reset, power-cycled, or restored by a modeset/suspend-resume path.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h`, which provides matching DCN 4.1.0 register offsets and base indices. These shift and mask macros are only correct when paired with that offset header and the DCN401/DCN 4.1.0 register database.

Important integration points include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn401/dcn401_resource.c`, where DCN401 hardware objects include the generated offset and shift/mask headers and construct per-block register tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn401.c`, where generated masks and shifts are expanded into DMUB service register metadata.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn401/irq_service_dcn401.c`, `display/dc/clk_mgr/dcn401/dcn401_clk_mgr.c`, and DCN401 GPIO translation/factory files, which include the same generated header for ASIC-specific register metadata.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn32/dcn32_mpc.c`, which shows the shared MPCC MCM programming model used for memory power, 1D LUT bank selection/programming, shaper LUT programming, RAM A/B PWL region setup, and status polling.
- Color pipeline data structures such as `enum dc_mpc_gamut_remap_select`, which distinguish first and second MPCC MCM gamut remap stages consumed by higher-level color-management policy.

The generated field names are an ABI-like contract between the hardware register database and the display driver helper tables. A missing token usually breaks compilation when a table references it; an incorrect numeric shift or mask can compile cleanly and only fail on DCN 4.1.0 hardware.

## Risks And Edge Cases

The main risk is silent display hardware misprogramming. Shift and mask constants are untyped preprocessor values; if one is wrong, a helper can write the wrong bits, leave stale bits in a packed register, corrupt a neighbor field, or decode a status bit incorrectly.

Chunk-boundary risk matters here. The first three lines are only the remaining masks for `MPCC_MCM0_MPCC_MCM_SHAPER_RAMB_REGION_28_29`; the shifts and first mask for that register live in the previous chunk. The final lines stop after `MPCC_MCM2_MPCC_MCM_1DLUT_RAMA_REGION_28_29`; later MCM2 RAM A regions, RAM B registers, gamut remap, memory power, and fast-load fields are outside this chunk. The final per-file report must merge neighboring chunk reports before making whole-file claims.

Instance pairing is critical. `MPCC_MCM0`, `MPCC_MCM1`, and `MPCC_MCM2` fields are structurally similar but must be paired with the matching generated offset table entry for the same instance. A mismatch can affect only one plane/compositor instance, making failures appear mode-specific or pipe-specific.

Color precision is sensitive. LUT data widths, 30-bit 3D LUT mode, matrix coefficient packing, output offset/scale fields, PWL start/end/slope/base fields, and region segment counts directly affect visible color. Bad constants can cause banding, clipping, wrong transfer functions, HDR/gamut errors, or bank-switches that appear to succeed but display stale tables.

Banked and indexed programming has sequencing hazards. The header defines the bit layout for RAM A/B selection, indexes, data ports, write color masks, and mode/select current readbacks, but it does not encode required ordering, synchronization, blanking/update-lock requirements, or polling. Callers must continue to use the established MPC color-management routines rather than open-coding register writes.

Memory-power fields can break live hardware if mishandled. Forcing or disabling shaper, 3D LUT, or 1D LUT memories while active can produce blank output, corrupted color, underflows, or stuck status bits. State fields should be polled with the intended helper logic and timeout behavior.

Repeated region-pair registers are easy to review mechanically but easy to damage during regeneration. The regular 9-bit LUT offset masks, 3-bit segment masks, and shifts at 0, 12, 16, and 28 must stay consistent across RAM A/B, shaper/1D LUT, and MPCC instances, except where a chunk boundary intentionally omits neighboring fields.

## Test Signals

Useful validation is mostly generated-header, build, and hardware-behavior oriented:

- Build coverage for DCN401 resource construction, DMUB register initialization, IRQ service, clock manager, GPIO support, and MPC color-management code that includes `dcn_4_1_0_sh_mask.h`.
- Generated-register consistency checks that every complete field in this slice has both a `__SHIFT` and `_MASK`, masks match the declared width, paired fields do not overlap unexpectedly, and every register referenced by DCN401 MPC resource tables exists in `dcn_4_1_0_offset.h`.
- Cross-checks against AMD's authoritative DCN 4.1.0 register database and nearby DCN 4.x/3.x generated headers, with expected instance or generation differences reviewed rather than blindly normalized.
- MPCC MCM shaper tests that program RAM A and RAM B, switch active banks, verify current-mode status, and validate visible transfer curves on multiple MPCC instances.
- 1D LUT tests for indexed writes, per-channel write masks, host RAM selection, PWL disable, RAM A/B region descriptors, current select/mode readback, and restore after modeset or suspend/resume.
- 3D LUT tests for normal and 30-bit data paths, RAM selection, output normalization/offset/scale, fast-load done, and soft/hard underflow status.
- Gamut-remap tests for first and second remap stages, coefficient-format selection, matrix banks A/B, current-mode status, HDR/wide-gamut paths, and no-op/bypass behavior.
- Memory-power tests that exercise shaper, 3D LUT, and 1D LUT memory force/disable/state fields during active display, idle transitions, hotplug, modeset, and GPU reset.

Regression symptoms from bad constants include blank or flickering output, color shifts, banding, clipped highlights/shadows, broken HDR or color-management policy, stale LUT bank selection, fast-load underflow reports, stuck memory-power state, failed suspend/resume restore, or failures isolated to one MPCC instance.

## Cross-Chunk Notes

This is a chunk-level research artifact only. The merge/reconciliation lane should combine it with neighboring chunks for the full `dcn_4_1_0_sh_mask.h` report. In particular, it should merge the preceding MCM0 shaper RAMB fields before line 20194 and the following MCM2 1D LUT RAMA/RAMB, gamut-remap, memory-power, and fast-load fields after line 22656.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 22520-24994

## Purpose

This chunk is a generated shift/mask register-field slice for AMD DCN 3.6 display hardware. It contains preprocessor constants only; there are no C functions, structs, enums, storage objects, or local executable paths. Its exported interface is the standard generated `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` namespace used by AMDGPU Display Core register-table code.

The range starts at the tail of the `MPCC_MCM1` movable color-management block, covers the full `MPCC_MCM2` block, begins the `MPCC_MCM3` block, then moves into MPC output mux/denorm/output-CSC fields and the beginning of `ABM0` ambient/backlight management fields. Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMD display hardware metadata and has no Ceph, filesystem, distributed-storage, network, or persistent-disk behavior.

## Important APIs, Types, And Macros

The only API surface is generated macros:

- `*_SHIFT` gives a register field's least-significant bit position.
- `*_MASK` gives the field mask in already-shifted register position.
- Register names encode hardware block and instance, such as `MPCC_MCM2_MPCC_MCM_SHAPER_CONTROL`, `MPCC_MCM3_MPCC_MCM_1DLUT_RAMA_REGION_8_9`, `MPC_OUT0_CSC_C11_C12_A`, and `ABM0_DC_ABM1_HG_MISC_CTRL`.

The `MPCC_MCM1_*` tail completes `MPCC_MCM1_MPCC_MCM_1DLUT_RAMB_REGION_32_33` and `MPCC_MCM1_MPCC_MCM_MEM_PWR_CTRL`. The memory-power register exposes force, disable, low-power-mode, and state fields for shaper, 3DLUT, and 1DLUT memories. This is a chunk-boundary continuation from the previous range, so complete `MCM1` analysis must merge adjacent chunks.

`MPCC_MCM2_*` is the largest complete block in this chunk. It defines movable color-management field geometry for MPC/MPCC instance 2:

- Shaper controls: `SHAPER_CONTROL`, per-channel offset/scale registers, LUT index/data registers, write color mask, RAM A/B selection, start/end controls for red/green/blue, and RAM A/B piecewise region descriptors from `REGION_0_1` through `REGION_32_33`.
- 3D LUT controls: `3DLUT_MODE`, `3DLUT_INDEX`, `3DLUT_DATA`, `3DLUT_DATA_30BIT`, `3DLUT_READ_WRITE_CONTROL`, output normalization, and output offset/scale fields for red, green, and blue.
- 1D LUT controls: `1DLUT_CONTROL`, `1DLUT_LUT_INDEX`, `1DLUT_LUT_DATA`, `1DLUT_LUT_CONTROL`, RAM A/B start controls, start slope controls, start base controls, end controls, offsets, and piecewise region descriptors from `REGION_0_1` through `REGION_32_33`.
- `MPCC_MCM_MEM_PWR_CTRL`, which carries memory force/disable/low-power/state fields for the shaper, 3DLUT, and 1DLUT memories.

`MPCC_MCM3_*` begins the same register family for instance 3. This chunk covers shaper setup, shaper RAM A/B regions, 3DLUT controls, 1DLUT control/index/data/control, and part of the 1DLUT RAM A/B region definitions. It stops before the complete `MCM3` block, so later chunks must reconcile the continuation before making whole-instance claims.

The `MPC_OUT*` block covers output-side muxing, denormalization, and output CSC for four MPC outputs:

- `MPC_OUT0_MUX` through `MPC_OUT3_MUX` provide `MPC_OUT_MUX`, rate-control enable/disable, flow-control mode, and flow-control count fields.
- `MPC_OUT*_DENORM_CONTROL` and clamp registers provide denorm mode plus min/max clamps for R/Cr, G/Y, and B/Cb.
- `MPC_OUT_CSC_COEF_FORMAT` selects coefficient format for output CSC.
- `MPC_OUT0_CSC_MODE` through `MPC_OUT3_CSC_MODE` select output CSC mode/current status.
- `MPC_OUT*_CSC_Cij_Ckl_A/B` registers pack pairs of 16-bit output CSC coefficients for two banks, allowing output color-space matrix programming per MPC output.

The `ABM0_*` block begins ambient backlight management instance 0:

- `BL1_PWM_AMBIENT_LIGHT_LEVEL`, `USER_LEVEL`, `TARGET_ABM_LEVEL`, `CURRENT_ABM_LEVEL`, `FINAL_DUTY_CYCLE`, and `MINIMUM_DUTY_CYCLE` are 17-bit-style PWM/backlight level fields.
- `BL1_PWM_ABM_CNTL` controls ABM use, ambient-light use, automatic current-level update, automatic final-duty calculation, and auto-update step size.
- `BL1_PWM_BL_UPDATE_SAMPLE_RATE` programs frame-count sampling and includes an ABM register-lock bit.
- `BL1_PWM_GRP2_REG_LOCK` defines group lock, update-pending, frame-start update, display selection, readback-double-buffer enable, and ignore-master-lock fields.
- `DC_ABM1_CNTL`, `IPCSC_COEFF_SEL`, ACE slope/offset and threshold registers, missed-frame status/clear fields, HGLS read-progress fields, and `HG_MISC_CTRL` define the first part of ABM image-statistics and adaptive contrast/enhancement controls.

## Control Flow And Usage Model

There is no local control flow. Runtime behavior is created by consumers that include `dcn_3_6_0_offset.h` and this header, then paste generated names into register tables and field-access helpers.

A typical DCN 3.6 path is:

1. Resource, IRQ, DMUB, MPC, and ABM code includes the matching DCN 3.6 offset and shift/mask headers.
2. Register-list macros such as `SR`, `SRI`, `SRI_ARR`, `SF`, `ABM_SF`, `FD_MASK`, and `FD_SHIFT` expand logical block fields into generated `reg*`, `*_MASK`, and `*__SHIFT` constants.
3. Runtime helpers such as `REG_SET`, `REG_UPDATE`, `REG_UPDATE_2`, `REG_GET`, `REG_WAIT`, and indexed register programming code use the masks and shifts to access MMIO fields without hardcoding bit positions.

Visible integration anchors in this tree include `display/dc/resource/dcn36/dcn36_resource.c`, which includes `dcn_3_6_0_offset.h` and `dcn_3_6_0_sh_mask.h`; `display/dmub/src/dmub_dcn36.c`, which initializes DCN 3.6 DMUB register offsets/masks/shifts; and `display/dc/irq/dcn36/irq_service_dcn36.c`, which builds the DCN 3.6 IRQ service metadata from the generated headers. Common MPC code under `display/dc/mpc/dcn32/` programs `MPCC_MCM_*` fields for shaper, 3DLUT, 1DLUT, and memory-power operations. Common ABM code uses `ABM_MASK_SH_LIST_DCN35` in the DCN 3.6 resource path, and those field-list macros reference the `ABM0_*` fields present in this chunk.

## State And Persistence Behavior

This header has no mutable state and persists nothing. The described state lives in display hardware registers and indexed LUT memories, with lifetime controlled by resource construction, modeset programming, plane/stream updates, color-management changes, backlight/ABM updates, runtime power transitions, suspend/resume, GPU reset, and display IP reset.

The `MPCC_MCM*` fields describe stateful color pipeline resources. Shaper LUTs, 3D LUT contents, 1D LUT contents, RAM A/B selection, current-mode readbacks, per-channel offsets/scales, and piecewise-linear region descriptors remain in hardware until overwritten or reset. Memory-power force/disable/low-power/state fields determine whether those LUT memories are available and whether status polling can complete.

The `MPC_OUT*` fields define output routing and color transforms. Mux selection controls which MPC tree output feeds each output path. Denorm clamp and output CSC registers affect live scanout color conversion and can persist across modeset boundaries if not reprogrammed by the owning display path.

The `ABM0_*` fields represent backlight and ambient-light processing state. PWM target/current/final/minimum levels, automatic update step size, register locks, frame-start update behavior, ACE thresholds, missed-frame flags, read-progress flags, and histogram/luma statistics are hardware-owned or software-programmed display state. Several ABM fields are status or clear-on-write style fields rather than ordinary persistent controls.

## Dependencies And Integration Points

- The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h`. Representative matching offsets include `regMPCC_MCM2_MPCC_MCM_SHAPER_CONTROL`, `regMPCC_MCM3_MPCC_MCM_SHAPER_CONTROL`, `regMPC_OUT0_MUX`, `regABM0_BL1_PWM_AMBIENT_LIGHT_LEVEL`, and `regABM0_DC_ABM1_HG_MISC_CTRL`.
- The generated macros depend on AMDGPU Display Core's register-helper infrastructure. Field names must match the logical field-list macros exactly; compile-time failures catch many spelling errors, but a stale or cross-generation mask with a valid name can still misprogram hardware if paired with the wrong offset.
- DCN 3.6 resource construction (`dcn36_resource.c`) binds this header to hardware blocks for the ASIC revision selected by `ASICREV_IS_DCN36`.
- DMUB integration (`dmub_dcn36.c`) uses this header with generated field lists to initialize firmware-visible register metadata.
- IRQ integration (`irq_service_dcn36.c`) uses the same generated offset and mask headers for display interrupt source metadata.
- MPC color management integrates through common DCN32-era MPC code and field lists. The fields in this chunk back runtime programming of MPCC MCM shaper LUTs, 3DLUTs, 1DLUTs, RAM bank selection, memory power, and output CSC/denorm.
- ABM/backlight integration flows through `dce_abm.h` field-list macros and resource-specific ABM mask/shift tables; DCN 3.6 uses the DCN35 ABM field-list subset for the fields present here.

## Risks And Edge Cases

- Generated-header drift is the main risk. `dcn_3_6_0_offset.h` and `dcn_3_6_0_sh_mask.h` must remain paired; a valid mask with a stale offset silently writes the wrong register field.
- Chunk-boundary incompleteness matters. This slice starts after most of `MPCC_MCM1` and ends before the rest of `ABM0` and `MPCC_MCM3`; final per-file analysis must merge adjacent chunks before making complete per-block claims.
- Instance mixups are easy. `MPCC_MCM1`, `MPCC_MCM2`, `MPCC_MCM3`, and `MPC_OUT0` through `MPC_OUT3` repeat near-identical fields. Using one instance's register offset with another instance's mask can create pipe-specific color or routing failures.
- Indexed LUT programming is sequencing-sensitive. Shaper, 3DLUT, and 1DLUT registers require correct host selection, bank selection, write-color masks, index resets, and data writes. Wrong masks can produce visible color artifacts only under HDR, color-managed, or multi-plane configurations.
- Packed field widths must be respected. This chunk includes 9-bit LUT offsets, 3-bit segment counts, 16-bit matrix coefficients, 17-bit PWM/backlight levels, 19-bit shaper offsets, and 24-bit LUT data. Unclamped inputs can truncate into neighboring fields or be silently masked.
- Status and control fields are adjacent. Fields named `*_CURRENT`, `*_STATE`, `*_UPDATE_PENDING`, `*_READ_PROGRESS`, `*_MISSED_FRAME`, and `*_CLEAR` should not be treated as ordinary writable configuration.
- Memory-power hazards can cause hangs or stale programming. Forcing MCM memories off while programming or reading LUTs can make register waits fail, leave color tables incomplete, or increase power if force-on is left set.
- ABM lock/update fields are frame-synchronized. Misusing `HGLS_REG_LOCK`, group locks, frame-start update selection, or ignore-master-lock fields can miss updates, expose stale readback, or cause one-frame backlight/contrast glitches.
- Output CSC and denorm mistakes are visually subtle. Matrix coefficient bank selection, coefficient format, clamp limits, and mux selection can yield color shifts, clipping, or only-output-specific failures while the rest of the pipe appears healthy.

## Test Signals

- Build with DCN 3.6 enabled and ensure `dcn36_resource.c`, `dmub_dcn36.c`, `irq_service_dcn36.c`, MPC, and ABM consumers compile against matching `dcn_3_6_0_offset.h` and `dcn_3_6_0_sh_mask.h`.
- Static consistency checks should compare repeated `MPCC_MCM2`/`MPCC_MCM3` and `MPC_OUT0`-`MPC_OUT3` shift/mask layouts where hardware instances are expected to match, and should verify representative masks align with their offsets.
- Color-management tests should load shaper, 3DLUT, and 1DLUT tables on MPCC instances 2 and 3, switch RAM A/B banks, check current-mode readbacks, and validate SDR/HDR/color-managed output for visible artifacts.
- MPC output tests should exercise all four outputs, mux selection, denorm clamp programming, output CSC enable/mode selection, coefficient bank programming, and color-space conversion scenarios.
- Power-management tests should cover MCM memory power force/disable/low-power/state behavior across modeset, runtime idle, suspend/resume, and GPU reset.
- ABM/backlight tests should cover PWM user/target/current/final/minimum levels, automatic ABM update, ambient-light input, register lock/update-at-frame-start behavior, missed-frame clear fields, and HGLS read-progress reporting.
- Runtime diagnostics should inspect register dumps around `MPCC_MCM*_MEM_PWR_CTRL`, `MPCC_MCM*_SHAPER_CONTROL`, `MPCC_MCM*_3DLUT_MODE`, `MPCC_MCM*_1DLUT_CONTROL`, `MPC_OUT*_CSC_MODE`, and `ABM0_DC_ABM1_HG_MISC_CTRL` when debugging color artifacts, stuck LUT programming, output-routing problems, or ABM/backlight regressions.

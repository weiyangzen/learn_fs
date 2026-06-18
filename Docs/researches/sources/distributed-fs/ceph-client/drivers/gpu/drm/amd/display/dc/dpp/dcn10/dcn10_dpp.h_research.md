# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn10/dcn10_dpp.h

## Purpose
`dcn10_dpp.h` is the register, field, object, and function contract for the DCN 1.0 display pipe processor. It defines how generated register addresses and masks are gathered into C structs, exposes the `struct dcn10_dpp` hardware object, and declares the color-management, scaler, cursor, conversion, clock, reset, and constructor entry points used by the display core.

## Important APIs, types, and functions
- Register-list macros are the core API surface: `TF_REG_LIST_DCN()`, `TF_REG_LIST_DCN10()`, `TF_REG_LIST_SH_MASK_DCN()`, and `TF_REG_LIST_SH_MASK_DCN10()` enumerate CM, DSCL, CNVC, cursor, and DPP_TOP registers and fields for a pipe instance.
- `TF_REG_FIELD_LIST(type)` expands all shared field names into either `struct dcn_dpp_shift` or `struct dcn_dpp_mask`.
- `DPP_COMMON_REG_VARIABLE_LIST` expands into `struct dcn_dpp_registers`, the register-address table consumed by `REG_*` helpers in implementation files.
- `struct dcn10_dpp` embeds the public `struct dpp` base and stores register tables, cached scaler filter pointers, line-buffer capability fields, the current scaler snapshot, and transfer-function parameters.
- Public prototypes include `dpp1_construct()`, `dpp_read_state()`, `dpp_reset()`, `dpp1_dscl_set_scaler_manual_scale()`, `dpp1_get_optimal_number_of_taps()`, `dpp1_program_input_csc()`, `dpp1_cm_set_gamut_remap()`, regamma/degamma programming helpers, cursor programming helpers, `dpp1_cnv_setup()`, `dpp1_dppclk_control()`, `dpp1_set_hdr_multiplier()`, and `dpp_force_disable_cursor()`.

## Control flow
This header has no executable flow, but it determines the implementation flow by shaping how each DPP instance is constructed and then accessed. ASIC-specific code instantiates static register, shift, and mask tables from these macros, passes them to `dpp1_construct()`, and the implementation accesses hardware by dereferencing `dpp->tf_regs`, `dpp->tf_shift`, and `dpp->tf_mask`. The `TO_DCN10_DPP()` macro downcasts a generic `struct dpp *` from the display core function table back to the DCN10 concrete object.

The declared operation set splits into several pipelines. DSCL functions consume `struct scaler_data`, derive tap and line-buffer settings, and program scaler registers. CM functions consume gamma, CSC, gamut, bias/scale, and HDR multiplier data and program the color-management registers. CNVC and cursor functions program pixel-format conversion, alpha behavior, and cursor registers. Constructor and reset/read-state functions connect those pieces to the generic DPP vtable.

## State and persistence behavior
All state is volatile kernel/hardware state. `struct dcn10_dpp` persists only while the display device is active. It caches the last filter coefficient tables (`filter_h`, `filter_v`, chroma variants) and the last `scl_data` to avoid redundant scaler programming. It also records line-buffer capabilities and a `pwl_data` scratch/cached transfer-function payload. Real display state is persisted in MMIO registers represented by the generated address/field tables; there is no disk or cross-boot persistence.

## Dependencies and integration points
The header depends on the generic display pipe processor interface in `dpp.h`, Linux `container_of`, generated ASIC register naming conventions such as `SRI()` and field macro naming, and DC fixed-point/color/scaler structures included indirectly from display core headers. It is included by DCN10 implementation files and inherited by DCN20/DCN201 headers, so additions here affect later-generation DPP code as well.

## Risks and edge cases
The biggest risk is register-contract drift. The field list is very large and spans DCN10 plus fields later reused by DCN20; a missing or incorrectly named field causes either build failures or incorrect hardware programming through a valid-looking `REG_UPDATE()`. Several fields use `TF2_SF()` to handle naming corner cases, making generated-name consistency important. The embedded object layout also matters because DCN20/DCN201 define similar but not identical objects and cast through generation-specific macros.

## Test signals
Useful validation includes building all DCN ASIC variants that include this header, display bring-up on DCN10 hardware or emulation, register trace comparison for scaler/color/cursor programming, hotplug modeset tests that exercise reset/read-state paths, and static checks that generated register headers still provide every symbol expanded by the macros.

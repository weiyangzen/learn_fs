# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn35/dcn35_resource.h

## Purpose
This header declares the DCN 3.5 resource-pool interface and DCN35-specific register-list macros. It layers DCN35 register additions on top of shared DCN32 macro families so the DCN35 constructor can initialize updated OPP, VPG, AFMT, stream/link encoder, MCIF writeback, HWSEQ, OPTC, and DPP register tables.

## Important APIs, Types, And Functions
- `DCN3_5_VMIN_DISPCLK_HZ` records the DCN35 VMIN display clock constant used by policy and bounding-box code.
- `TO_DCN35_RES_POOL(pool)` converts from generic pool to `struct dcn35_resource_pool`.
- `extern dcn3_5_ip` and `extern dcn3_5_soc` expose DCN35 DML bounding-box globals.
- `dcn35_patch_unknown_plane_state` and `dcn35_update_bw_bounding_box` are exported DCN35 behavior hooks.
- `dcn35_create_resource_pool` is the Display Core factory for this ASIC generation.
- Register macros extend or replace shared lists: `OPP_REG_LIST_DCN35_RI`, `VPG_DCN31_REG_LIST_RI`, `AFMT_DCN31_REG_LIST_RI`, `SE_DCN35_REG_LIST_RI`, `LE_DCN35_REG_LIST_RI`, `MCIF_WB_COMMON_REG_LIST_DCN3_5_RI`, `HWSEQ_DCN35_REG_LIST`, `OPTC_COMMON_REG_LIST_DCN3_5_RI`, and `DPP_REG_LIST_DCN35_RI`.

## Control Flow
The header has no direct execution. Runtime flow occurs when `dcn35_resource.c` sets `REG_STRUCT`, expands these macros for each hardware instance, and passes the resulting tables to DCN35 block constructors. The exported factory and update/patch functions are installed into `resource_funcs` so generic Display Core validation and initialization paths can dispatch to DCN35-specific behavior.

## State And Persistence
No storage is allocated here beyond compile-time declarations. The macros define which MMIO addresses become persistent in static register tables inside `dcn35_resource.c`. The pool structure preserves the generic-resource embedding contract, and the extern DML globals persist in FPU/DML implementation files.

## Dependencies And Integration Points
This header depends on `core_types.h` and on shared DCN32/DCN20 macro definitions being visible to consumers. It integrates with generated DCN35 register names, DCN35 hardware block constructors, DML bounding-box update code, DML2 validation, and generic Display Core resource-pool lifecycle.

## Risks And Edge Cases
Macro composition is the main risk. Several DCN35 lists intentionally include inherited DCN32/DCN20 pieces plus new fields such as OPP clock control, VPG memory power, DIG front-end clock controls, HPO/DMU HWSEQ registers, OPTC CRC/readback fields, and MMHUBBUB clock control. Missing one field can break only a narrow feature such as clock gating, Replay/PSR timing, CRC capture, or writeback. Because these macros rely on caller-provided `SRI`, `SR`, `SRI2_ARR`, and related helpers, they are sensitive to macro namespace changes in implementation files.

## Test Signals
Compile DCN35 resource files with generated register headers, trace register table values during resource construction, validate OPP/DPP/OPTC/HWSEQ programming on modeset, test clock-gating and power-gating transitions, exercise VPG/AFMT metadata/audio packets, run writeback through MCIF, test unknown-plane patching, and confirm DML bounding-box update after clock table changes.

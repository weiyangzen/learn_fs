# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn401/dcn401_resource.h

## Purpose

`dcn401_resource.h` declares the DCN401 resource-pool API and exports the large register-list macros needed for runtime initialization of DCN401 hardware blocks. It is both a public constructor header and a generation-specific register binding contract shared by `dcn401_resource.c` and DCN401 block constructors.

## Important APIs, Types, And Functions

- `TO_DCN401_RES_POOL(pool)` and `struct dcn401_resource_pool`: typed wrapper around generic `struct resource_pool`.
- `dcn401_create_resource_pool()`: creates the DCN401 pool.
- Exported helpers: `dcn401_patch_unknown_plane_state()`, `dcn401_validate_bandwidth()`, `dcn401_prepare_mcache_programming()`, `dcn401_get_default_tiling_info()`, `dcn401_get_vstartup_for_pipe()`, and `dcn401_get_power_profile()`.
- Register-list macros: `HUBP_REG_LIST_DCN401_RI`, `ABM_DCN401_REG_LIST_RI`, `VPG_DCN401_REG_LIST_RI`, `SE_DCN4_01_REG_LIST_RI`, `LE_DCN401_REG_LIST_RI`, `DPP_REG_LIST_DCN401_COMMON_RI`, `OPP_REG_LIST_DCN401_RI`, `DSC_REG_LIST_DCN401_RI`, MPC mux macros, and `OPTC_COMMON_REG_LIST_DCN401_RI`.

## Control Flow

The header has no executable flow. Its macros expand inside C-file register initialization after `REG_STRUCT`, `SRI_ARR`, `SR_ARR`, NBIO accessors, and related macros are defined. The exported function declarations let other DC code call DCN401-specific validation, tiling, mcache, vstartup, and power-profile behavior through direct references or `resource_funcs`.

## State And Persistence Behavior

The header owns no state. Its register macros define which hardware register offsets are stored into static register-table structures at runtime. The declared functions mutate runtime `dc`, `dc_state`, `pipe_ctx`, or `dc_plane_state` objects in the C implementation.

## Dependencies And Integration Points

It depends on `core_types.h`, `dcn32/dcn32_resource.h`, and `dcn401/dcn401_hubp.h`. The register macros integrate DCN401 blocks with HUBP, ABM, VPG, stream encoder, link encoder, DPP/SPL/sharpener, OPP, DSC, MPC, and OPTC constructors. The exported helpers are used by generic DC resource management and validation paths.

## Risks And Edge Cases

- The register-list macros are highly sensitive to the macro environment in the including C file; missing or differently named helper macros break compilation or silently bind wrong fields if reused incorrectly.
- The macros contain very broad hardware coverage, including cursor, DMDATA, flip, mcache, 3D LUT, EASF, iSharp, DSC PPS/error counters, and timing-generator registers. Omissions can surface as feature-specific runtime failures rather than compile failures if structure fields still match.
- Header declarations must remain synchronized with `dcn401_res_pool_funcs`; otherwise generic callers can lose access to DCN401-specific behavior.

## Test Signals

- Build tests catch most macro/field drift.
- Feature tests should cover every macro-heavy block family: HUBP flip/mcache/cursor, ABM backlight, VPG/AFMT/APG packets, stream/link encoders, DPP color/SPL/sharpener, DSC PPS/status, MPC muxing, and OPTC timing/interrupts.
- API-level tests should call exported helpers through both direct symbols and the resource function table where applicable.

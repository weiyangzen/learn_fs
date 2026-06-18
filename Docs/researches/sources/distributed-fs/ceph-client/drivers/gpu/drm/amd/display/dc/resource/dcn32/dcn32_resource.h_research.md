# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.h

## Purpose
This header is the shared DCN 3.2 resource contract for AMD Display Core. It exposes the DCN32 resource pool entry points, SubVP/FPO/MALL helper APIs, bandwidth and DML hooks, pipe acquisition helpers, and the large runtime register-list macros used by DCN32-family resource constructors. DCN321 and DCN35 both consume parts of this header, so it acts as a common compatibility layer between hardware-specific constructors and the generic `resource_pool` interface.

## Important APIs, Types, And Functions
- `struct dcn32_resource_pool` embeds `struct resource_pool`; `TO_DCN32_RES_POOL` recovers the containing pool.
- Constants define DET sizing, MALL block geometry, low DCFCLK defaults, SubVP limits, and VMIN display clock values.
- `struct subvp_high_refresh_list` and `struct subvp_active_margin_list` describe resolution/refresh allow-list entries used by SubVP admission policy.
- `dcn32_create_resource_pool`, `dcn32_panel_cntl_create`, `dcn32_validate_bandwidth`, `dcn32_populate_dml_pipes_from_context`, and `dcn32_calculate_wm_and_dlg` are the core DCN32 bring-up and validation hooks.
- Pipe and color-resource helpers include 3D LUT acquire/release, phantom-pipe creation, free pipe acquisition as secondary DPP or OPP head, release, ODM policy updates, DET allocation, and hardware cursor sizing.
- MALL/SubVP/FPO helpers expose cursor allocation, cache-way conversion, SubVP presence/admissibility, MCLK switch support by firmware vblank stretch, and minimum DCFCLK override.
- Register-list macros cover clock sources, ABM, audio, VPG, AFMT, APG, stream/link encoders, HPO DP encoders, DPP, OPP, AUX/I2C, DWB, MCIF writeback, DSC, MPC, OPTC, HUBP, HUBBUB, DCCG, and VMID blocks.

## Control Flow
The header has no executable control flow, but it shapes runtime flow in resource constructors. Hardware-specific `.c` files select a `REG_STRUCT`, invoke these macros for every instance, then pass the populated register tables plus mask/shift tables into block constructors such as HUBP, DPP, OPP, OPTC, HUBBUB, DCCG, DSC, AUX, and I2C. Resource function tables use the declared APIs to connect validation, DML pipe population, pipe management, writeback, color, and SubVP behavior into Display Core.

## State And Persistence
No runtime state is stored directly in this header. Persistent effects are produced by code that uses it: resource pools retain object pointers, `dc->caps`/`dc->config`/`dc->debug` retain capability policy, and DML/DML2 contexts consume constants such as DET segment size and MALL block geometry. Externs `dcn3_2_ip` and `dcn3_2_soc` are shared DML bounding-box inputs defined elsewhere.

## Dependencies And Integration Points
The header depends on `core_types.h` and on register-helper macro names supplied by including resource files. It integrates with DML, DML2 callback setup, DC state/resource contexts, pipe context topology, Display Core link/stream/resource construction, and generated ASIC register offset and mask headers.

## Risks And Edge Cases
The register macros are high-risk because malformed instance indices, base-index names, or duplicated fields can silently map a block to the wrong MMIO address. Shared constants must remain synchronized with DML assumptions and firmware behavior, especially DET segment size, MALL block size, and vblank-stretch timing. Since many macros rely on caller-defined `REG_STRUCT`, `BASE`, `SRI`, and related helpers, include-order or macro redefinition mistakes can break unrelated ASIC constructors. Header-level prototypes also create ABI-like coupling: changing signatures affects several DCN generation files.

## Test Signals
Useful signals include compile coverage for all DCN32-family resource files, successful resource-pool construction on DCN32/DCN321/DCN35 paths, correct register table initialization in MMIO tracing, DML validation passing for multi-display and DSC/HPO configurations, SubVP/FPO admission tests, MALL cache-way calculations, and modeset tests that exercise pipe split/merge, ODM, writeback, AUX/I2C, and PSR/Replay-related paths.

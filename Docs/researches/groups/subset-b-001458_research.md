# subset-b-001458 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource_helpers.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource_helpers.c

## Purpose
This file implements DCN32 policy helpers for SubVP, MALL allocation, DET override, pipe cleanup, MPO/rotation checks, and firmware-assisted MCLK switching through vblank stretch. These routines are consumed by DCN32/DCN321 resource function tables and DML/DML2 callback configuration to turn a proposed `dc_state` into hardware allocation and power-management decisions.

## Important APIs, Types, And Functions
- `dcn32_helper_calculate_mall_bytes_for_cursor` computes cursor MALL bytes from HUBP cursor attributes and stream cursor format, rounding up to DCN3.2 MALL block size and adding an alignment block.
- `dcn32_helper_calculate_num_ways_for_subvp` converts DML-computed SubVP MALL bytes into cache ways, honoring `dc->debug.force_subvp_num_ways`.
- `dcn32_merge_pipes_for_subvp` tears down ODM and pipe-split topology not supported for SubVP, releasing DSC when needed and clearing plane/stream resources.
- State predicates include `dcn32_all_pipes_have_stream_and_plane`, `dcn32_subvp_in_use`, `dcn32_mpo_in_use`, `dcn32_any_surfaces_rotated`, `dcn32_is_center_timing`, and `dcn32_is_psr_capable`.
- DET policy lives in `dcn32_determine_det_override`, `dcn32_set_det_allocations`, and the private `override_det_for_subvp`.
- FPO support is evaluated by `dcn32_can_support_mclk_switch_using_fw_based_vblank_stretch`, with private refresh-rate helpers.
- Admission helpers `dcn32_subvp_drr_admissable` and `dcn32_subvp_vblank_admissable` reject unsafe active-plus-blank combinations and PSR/Freesync conflicts.
- `dcn32_update_dml_pipes_odm_policy_based_on_context` mirrors existing ODM slice topology into DML pipes, while `dcn32_override_min_req_dcfclk` raises DCFCLK for SubVP.

## Control Flow
Most helpers iterate `dc->res_pool->pipe_count` over `context->res_ctx.pipe_ctx`. DET allocation first counts non-phantom streams, divides 18 DET segments per stream, then divides per plane and per split pipe before applying a special two-display high-refresh FHD override. Single-pipe non-linear, non-dual-plane cases prefer unbounded requesting with smaller DET unless disabled by debug flags. FPO evaluation rejects null contexts, disabled debug/cap flags, existing shutdown requests, more than two streams, no-plane candidates, EDID panel disable flags, low refresh, unsupported vblank stretch range, non-Freesync streams, and gaming VRR combinations blocked by policy. SubVP DRR/Vblank admission counts one SubVP main and one non-SubVP pipe, rejects 1080p active-plus-blank cases, screens PSR/Freesync state, checks refresh below 120 Hz, and for Vblank requires DML to report `dm_dram_clock_change_vblank_w_mall_sub_vp`.

## State And Persistence
The functions mutate only caller-owned transient state: pipe links/resources during SubVP merge, `display_e2e_pipe_params_st` fields for DET and ODM policy, and `context->bw_ctx.bw.dcn.clk.dcfclk_khz` when SubVP needs a minimum clock. They read persistent policy from `dc->debug`, capability flags from `dc->caps`, and DML results from `context->bw_ctx`.

## Dependencies And Integration Points
This file depends on DC state private helpers, stream internals, DML FPU helpers, display mode VBA utilities, resource topology helpers, and DCN20 DSC release. It integrates with validation paths that populate DML pipes, DML2 SubVP callbacks, hardware sequencing that later programs DET/ODM values, and policy gates for PSR, Freesync, MALL, and firmware-assisted MCLK switching.

## Risks And Edge Cases
Pipe-topology mutation is delicate: stale `top_pipe`, `bottom_pipe`, ODM links, DSC pointers, or resource structs could leak resources or corrupt later programming. DET division uses integer truncation and assumes an 18-segment policy, so unusual stream/plane splits can under-allocate unless DML catches it. Cursor MALL sizing assumes cursor attributes are initialized when enabled. FPO math depends on pixel-clock and timing totals and has several zero/null guards, but policy mistakes can cause flicker or unsupported memory-clock switching. SubVP DRR/Vblank admission relies on pipe type checks and stream flags that must match Display Core semantics.

## Test Signals
Exercise single-pipe non-linear surfaces, dual-plane video, pipe split, ODM split/merge, SubVP phantom streams, two-display SubVP plus DRR/Vblank, 1080p60 active-plus-blank rejection, PSR-capable secondary displays, Freesync/VRR gaming policy, FPO one- and two-display cases, cursor formats and large cursor sizes, rotated surfaces, center timing, and DML pipe DET/ODM field output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c

## Purpose
This file constructs, configures, and destroys the DCN 3.2.1 Display Core resource pool. It maps generated DCN321 register offsets into block-specific register tables, creates all hardware abstraction objects, fills ASIC capability/default policy fields, initializes DML and DML2 options, and exposes a `resource_funcs` table that lets generic Display Core code drive this ASIC generation.

## Important APIs, Types, And Functions
- `dcn321_create_resource_pool` allocates `struct dcn321_resource_pool` and delegates construction.
- `dcn321_resource_construct` is the main bring-up path. It initializes BIOS/clock/ABM/DCCG registers, handles pipe fuses, fills `dc->caps`, `dc->config`, `dc->debug`, creates hardware blocks, calls `resource_construct`, installs sequencer functions, and configures DML2.
- Factory helpers create AUX/I2C engines, clock sources, DIO, HUBBUB/VMID, HUBP, DPP, MPC, OPP, timing generators, link encoders, audio, VPG/AFMT/APG, stream encoders, HPO DP stream/link encoders, HW sequencer, DWB, MMHUBBUB, and DSC.
- `dcn321_resource_destruct` releases all objects allocated by construction, including nested VPG/AFMT/APG objects and shared services.
- `dcn321_update_bw_bounding_box` calls the FPU bounding-box update and reinitializes active DML2 contexts when enabled.
- `read_pipe_fuses` reads `CC_DC_PIPE_DIS` and reduces usable pipe count.
- `dcn321_res_pool_funcs` wires generic resource operations to DCN32/DCN30/DCN20 implementations plus DCN321-specific link creation and bounding-box update.

## Control Flow
Construction starts by populating static register tables through macros from `dcn32_resource.h`, then assigns `ctx->dc_bios->regs`. It reads pipe fuses, asserts if pipe 0 or full DCN is disabled, adjusts `dcn3_21_ip.max_num_dpp/max_num_otg`, and sets pool counts based on remaining pipes. It fills capability fields for cursor, MALL/CAB, SubVP timing margins, DP/HPO, DSC, color, LTTPR, VM, and ODM behavior. It creates five PLL clock sources plus a DP DTO source, DCCG, DML instance, IRQ service, HUBBUB, DIO, then loops over non-fused pipe instances to create HUBP/DPP/OPP/TG/ABM entries compacted into pool arrays. It then creates PSR, MPC, DSCs, DWB/MMHUBBUB, AUX/I2C engines, and delegates audio/stream/HPO/virtual encoder creation to `resource_construct`. Failure at any step jumps to `create_fail`, destructs partial state, and returns false.

## State And Persistence
Persistent driver state includes `pool->base` object arrays, counts, function pointers, `dc->caps`, `dc->config`, `dc->debug`, DML state, DML2 options, optional OEM DDC service, and BIOS register pointers. Static register tables are rewritten during construction and then referenced by hardware objects. Pipe fuses persist in the chosen pipe count and compacted hardware-object arrays.

## Dependencies And Integration Points
The file depends on generated DCN321/NBIO register headers, shared DCN32 register-list macros, DML DCN321 FPU code, IRQ service DCN32, DMUB ABM/PSR, DC link service, DCE clock/audio/AUX/I2C, DWB/MMHUBBUB, and many DCN20/30/31/32 block constructors. It integrates with Display Core through `resource_pool`, `resource_create_funcs`, `resource_funcs`, DML/DML2, HW sequencer initialization, BIOS LTTPR queries, and link encoder assignment.

## Risks And Edge Cases
Partial-construction cleanup must match allocation order; an object missed by `dcn321_resource_destruct` leaks on failure. The IRQ destructor is inside the pipe loop and guarded by a null pointer, which is unusual and should be checked for repeated destroy safety. Pipe-fuse compaction means logical pool indexes differ from physical pipe instances, so any code assuming equal indexes can misprogram registers. Register-table macros depend on generated names and correct `REG_STRUCT`. Hard-coded caps, cursor limits, MALL sizing, and SubVP margins must stay synchronized with firmware, DML, and ASIC characterization.

## Test Signals
Key signals include successful probe on all fuse configurations, failure-injection for each factory allocation, modeset with four and fewer pipes, HPO DP and HDMI link bring-up, DSC allocation/release, AUX/I2C/DDC transactions, ABM/PSR operation, MALL/SubVP validation, DML/DML2 reinitialization after clock table updates, writeback operation, and teardown without leaks or double frees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.h

## Purpose
This header declares the public DCN 3.2.1 resource-pool interface. It is intentionally small: DCN321 mostly reuses DCN32 infrastructure, so the header provides only the container type, conversion macro, external DML bounding-box inputs, and resource-pool creation entry point.

## Important APIs, Types, And Functions
- `TO_DCN321_RES_POOL(pool)` converts a generic `struct resource_pool *` to `struct dcn321_resource_pool *` with `container_of`.
- `extern struct _vcs_dpi_ip_params_st dcn3_21_ip` and `extern struct _vcs_dpi_soc_bounding_box_st dcn3_21_soc` provide DCN321 DML IP/SOC bounding boxes owned by the FPU/DML implementation.
- `struct dcn321_resource_pool` embeds the generic `struct resource_pool`.
- `dcn321_create_resource_pool(const struct dc_init_data *init_data, struct dc *dc)` is the ASIC-specific factory used by Display Core initialization.

## Control Flow
The header has no executable flow. Runtime flow enters through `dcn321_create_resource_pool`, which allocates a DCN321 pool, invokes the constructor in `dcn321_resource.c`, and returns the embedded generic pool on success. The DML externs are passed to DML initialization during construction and can be adjusted for pipe fusing before use.

## State And Persistence
No state is stored in the header. The embedded-pool layout is an ABI contract between generic resource cleanup, `TO_DCN321_RES_POOL`, and DCN321-specific destructors. The extern DML structures are persistent globals defined elsewhere; constructor code mutates fields such as maximum pipe counts after reading fuses.

## Dependencies And Integration Points
The header depends on `core_types.h` for Display Core resource and DC type definitions. It integrates with the DCN321 resource constructor, DML DCN321 bounding-box implementation, and generic Display Core resource-pool ownership model.

## Risks And Edge Cases
The main risk is layout coupling: `TO_DCN321_RES_POOL` assumes `base` remains a direct member of `struct dcn321_resource_pool`. If the create function signature or extern DML object names change, initialization code and ASIC selection tables must be updated together. Because this header exposes mutable global DML structures, cross-file users must avoid inconsistent assumptions about when fuse-adjusted fields are valid.

## Test Signals
Build tests should include every translation unit that includes this header. Runtime signals include ASIC selection choosing `dcn321_create_resource_pool`, successful construction/destruction through the generic `resource_pool` pointer, correct DML initialization using `dcn3_21_soc/ip`, and pipe-fuse tests showing adjusted DML pipe limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn35/dcn35_resource.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn35/dcn35_resource.c

## Purpose
This file builds the DCN 3.5 Display Core resource pool. It is the ASIC-specific factory for newer DCN35 blocks, adding DML2-first bandwidth validation, Replay support, power-gating control, fine-grain clock-gating defaults, DPIA preferences, DCN35 register maps, and updated block constructors while still reusing large pieces of DCN31/DCN32/DCN20 infrastructure.

## Important APIs, Types, And Functions
- `dcn35_create_resource_pool` allocates `struct dcn35_resource_pool` and returns the embedded generic pool after construction.
- `dcn35_resource_construct` initializes register tables, capabilities, debug defaults, hardware objects, DML/DML2 options, and sequencer state.
- Factory helpers create DPP/OPP/AUX/I2C/MPC/DIO/HUBBUB/HUBP/TG/link encoders/minimal link encoders/panel control/audio/VPG/AFMT/APG/stream encoders/HPO DP encoders/HWSEQ/DWB/MMHUBBUB/DSC/clock sources.
- `dcn35_validate_bandwidth` calls `dml2_validate`, then decides z-state support when validation includes programming.
- `dcn35_patch_unknown_plane_state` sets unknown plane tiling to `DcGfxVersion9` before delegating to DCN20 patching.
- `dcn35_update_bw_bounding_box` updates DCN35 bandwidth bounding boxes through FPU code.
- `dcn35_res_pool_funcs` exposes DCN35 behavior to generic Display Core, including link encoder assignment/unassignment, DML2 validation, panel defaults, DPIA preferred encoder selection, DET size callback, and encoder-switch state update.

## Control Flow
Construction populates BIOS/clock/ABM/DCCG register tables, enables 4:1 MPC by default, assigns DCN35 resource caps, and fills broad capability/config/debug defaults including APU, zstate, IPS, seamless ODM, host-router/DPIA counts, root clock optimization, power-gating policy, and fine-grain clock gating. It creates five clock-source entries plus DP DTO, initializes a temporary DML1 instance for compatibility, creates DCCG and PG control, IRQ service, HUBBUB, DIO, all HUBPs/DPPs/OPPs/TGs, PSR, Replay, ABMs, MPC, DSCs, DWB/MMHUBBUB, AUX/I2C, and then uses `resource_construct` for audio and encoder families. It sets USB4 DPIA count unless disabled by debug, constructs the DCN35 HW sequencer, publishes plane caps, and configures DML2 options. Any allocation or constructor failure jumps to cleanup via `dcn35_resource_destruct`.

## State And Persistence
Persistent state includes the `resource_pool` object arrays, PG control, PSR/Replay, DCCG, DIO, DML/DML2 option fields, `dc->caps`, `dc->config`, and `dc->debug`. Static register tables are initialized for the active context and referenced by constructed blocks. Debug defaults deliberately keep several power gates disabled or ignored while enabling fine-grain clock-gating masks.

## Dependencies And Integration Points
The file depends on DCN35 generated offset/mask headers, MMHUB/NBIO headers, DML2 wrapper, DCN35 FPU, DCN35 HUBBUB/HUBP/DPP/OPTC/OPP/DSC/DCCG/PG/DWB/MMHUBBUB/HWSEQ blocks, IRQ service DCN35, DMUB ABM/PSR/Replay, link encoder configuration, and shared DCN32 register macros. It integrates with Display Core resource initialization, link assignment, DML2 validation, HW sequencing, BIOS LTTPR queries, USB4 DPIA routing, PSR/Replay panel features, and writeback.

## Risks And Edge Cases
The constructor has many hard-coded caps and debug policies, so ASIC characterization changes can cause regressions without compiler signals. `res_cap_dcn35.num_pll` is four while the clock-source array creates five entries plus DP DTO; this may be intentional naming but is a review point. `dcn31_link_enc_create_minimal` uses an engine-id bounds check that should be validated around off-by-one behavior. Destruction must free newer Replay and PG control objects as well as inherited nested encoder sub-blocks. DML2 validation requires a valid `context->bw_ctx.dml2` or DC-power variant; callers must initialize those contexts before validation. Register table correctness is critical because DCN35 adds new clock-gating and power-domain registers.

## Test Signals
Run probe and teardown on DCN35 hardware or emulation, DML2 bandwidth validation for AC/DC power sources, zstate/IPS transitions, PSR and Replay enablement, USB4 DPIA routing with preferred DIGC/DIGD encoders, HPO DP and legacy link encoders, DSC and ODM modes, fine-grain clock gating toggles, DWB/MMHUBBUB writeback, AUX/I2C, panel default propagation, unknown-plane patching, and failure injection across all factory helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn35/dcn35_resource.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn35/dcn35_resource.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn35/dcn35_resource.h -->

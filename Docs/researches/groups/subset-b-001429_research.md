# Research: subset-b-001429

This grouped report covers DML21 core, DPMM, MCG, and PMO source files for the DCN4/DCN42 display-mode calculation path. Each file section is delimited for reconciliation into its source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_core/dml2_core_dcn4_calcs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_core/dml2_core_dcn4_calcs.h

## Purpose
Declares the DCN4 core calculation API used by DML21 mode support and mode programming. The header is the public face of the core calculator implementation: callers pass display configuration, mode-lib state, and output register/programming structures, and the implementation emits support decisions, watermarks, arbiter registers, pipe registers, stream programming, MALL/MCACHE data, FAMS2 data, and debug string conversions.

## Important APIs, types, and functions
- `dml2_core_calcs_mode_support_ex()` evaluates a `dml2_display_cfg` against a min-clock table and project id, updating `dml2_core_internal_display_mode_lib` and returning a support result status.
- `dml2_core_calcs_mode_programming_ex()` consumes the selected support state and emits `dml2_display_cfg_programming`.
- `dml2_core_calcs_get_watermarks()`, `dml2_core_calcs_get_arb_params()`, `dml2_core_calcs_get_pipe_regs()`, and `dml2_core_calcs_get_stream_programming()` map the internal mode-programming state into DC hub/display programming structures.
- `dml2_core_calcs_get_global_sync_programming()`, `dml2_core_calcs_get_stream_fams2_programming()`, and `dml2_core_calcs_get_global_fams2_programming()` expose synchronization and FAMS2 programming derived by core calculations.
- `dml2_core_calcs_get_mcache_allocation()`, `dml2_core_calcs_get_mall_allocation()`, `dml2_core_calcs_get_plane_support_info()`, `dml2_core_calcs_get_stream_support_info()`, and `dml2_core_calcs_get_informative()` expose support and informational state to the top layer.
- `dml2_core_calcs_get_dpte_row_height()` and `dml2_core_calcs_cursor_dlg_reg()` are narrower helpers for DPTE row and cursor DLG programming.

## Control flow and integration
The expected flow is mode support first, mode programming second, then register/programming getters. It includes only prototypes and forward declarations, so state ownership is external: `dml2_core_internal_display_mode_lib` is allocated and initialized by the core instance selected through the core factory, while output structures are supplied by top-level DML code or DPMM.

## State and persistence behavior
This header stores no data. It defines access points into the persistent per-core `mode_lib`, whose `ms`, `mp`, and `scratch` fields are defined in `dml2_core_shared_types.h`. Callers must preserve the mode-lib instance across support/programming/getter calls for coherent outputs.

## Dependencies
Includes `dml2_core_shared_types.h` and relies on DCN/DML top-level structures such as `dml2_display_cfg`, `dml2_display_cfg_programming`, DCHUB register sets, DMUB FAMS2 commands, and p-state enums. It forward-declares several register/support structures to reduce include coupling.

## Risks and edge cases
The API relies on strict call ordering and valid array indices for `pipe_index` and `plane_index`; the header does not encode bounds. Several getters expose data produced by prior calculations, so using them before successful mode programming may return stale or uninitialized values. FAMS2 functions depend on `display_configuation_with_meta`, making implicit SubVP/FAMS metadata part of the contract.

## Test signals
Useful tests instantiate supported project ids, run mode support/programming for representative single-stream, multi-stream, DSC, ODM, SubVP/FAMS2, and cursor cases, then compare emitted watermarks/registers/support info against known-good values. Negative tests should call unsupported formats or invalid indices only in harnesses that can catch assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_core/dml2_core_dcn4_calcs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_core/dml2_core_factory.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_core/dml2_core_factory.c

## Purpose
Constructs a `dml2_core_instance` by project id and wires the correct DCN4/DCN42 implementation callbacks. It is the dispatch boundary between project selection in the top layer and core mode-support/mode-programming code.

## Important APIs, types, and functions
- `dml2_core_create(enum dml2_project_id project_id, struct dml2_core_instance *out)` is the only exported function.
- For `dml2_project_dcn40`, `dml2_project_dcn4x_stage2`, and `dml2_project_dcn4x_stage2_auto_drr_svp`, it selects `core_dcn4_initialize`, `core_dcn4_mode_support`, `core_dcn4_mode_programming`, `core_dcn4_populate_informative`, and `core_dcn4_calculate_mcache_allocation`.
- For `dml2_project_dcn42`, it swaps only initialization to `core_dcn42_initialize` while reusing the DCN4 support/programming/populate/MCACHE hooks.
- `dml2_project_dcn4x_stage1` explicitly returns false; invalid/default ids also fail.

## Control flow and integration
The function validates `out`, zeroes the instance with `memset`, records the project id, then fills callback slots based on a switch. The resulting instance is consumed by DML top-level initialization and later invoked through function pointers.

## State and persistence behavior
The only persistent state initialized here is the function table and `project_id` inside `dml2_core_instance`. Previous contents of `out` are intentionally discarded. No heap allocation or external registration occurs.

## Dependencies
Depends on `dml2_core_factory.h`, `dml2_core_dcn4.h` for implementation symbols, and `dml2_external_lib_deps.h` for `memset`/bool support.

## Risks and edge cases
Callers must check the boolean result before using callback pointers. Stage1 returns false without dummy callbacks, so treating zeroed callbacks as usable would crash. DCN42 shares DCN4 core algorithms after DCN42-specific initialization, so changes to shared DCN4 algorithms also affect DCN42 behavior.

## Test signals
Factory tests should cover null output, invalid project id, unsupported stage1, DCN40/stage2/stage2_auto_drr_svp callback identity, and DCN42 initialization callback identity. A smoke test should invoke `initialize` after creation for each supported project.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_core/dml2_core_factory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_core/dml2_core_factory.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_core/dml2_core_factory.h

## Purpose
Declares the core factory entry point for constructing a `dml2_core_instance` from a `dml2_project_id`.

## Important APIs, types, and functions
- `dml2_core_create()` is the single exported API.
- It depends on `struct dml2_core_instance` from internal shared types and `enum dml2_project_id` from top-level DML types.

## Control flow and integration
The header is included by top-level DML initialization code that needs to bind core callbacks and by the implementation file. It hides project-specific callback selection behind one factory call.

## State and persistence behavior
No state is stored in the header. The function it declares mutates caller-provided `out` storage.

## Dependencies
Includes `dml2_internal_shared_types.h` and `dml_top_types.h`.

## Risks and edge cases
The API returns only bool and leaves error reason implicit, so callers need project-id validation or logging around failed creation. Because the header exposes no capability query, code must track supported project ids in sync with the implementation switch.

## Test signals
Compile-time test coverage is mostly include/link coverage. Runtime factory tests should verify the implementation fills valid callbacks for supported ids and returns false for null/invalid inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_core/dml2_core_factory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_core/dml2_core_shared_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_core/dml2_core_shared_types.h

## Purpose
Defines the internal data model for DML21 core calculations. This is the largest contract in the group: it captures IP capabilities, SoC and bandwidth classes, pipe descriptors, mode-support fail reasons and outputs, mode-programming outputs, scratch locals, parameter bundles for shared calculators, and the `dml2_core_internal_display_mode_lib` state object that persists across calculator calls.

## Important APIs, types, and functions
- Constants include prefetch vratio limits, the DCFCLK factor, invalid DPP marker, and pipe-to-plane sentinel `__DML2_CALCS_PIPE_NO_PLANE__`.
- `struct dml2_core_ip_params` models DCN hardware capabilities and policy knobs: ROB/config/compressed buffers, chunk sizes, DPP/OPP/OTG/DSC/writeback counts, scaler limits, MALL/SubVP timing, MRQ, DCHUB arbitration delay, and host VM mode.
- `struct dml2_core_internal_DmlPipe` is the per-surface/pipe normalized input used by calculations: clocks, scaler state, rotation, viewport, tiling, DCC, ODM, format, bytes-per-pixel, swath, pitch, and metadata pitch.
- Enums classify request type, bandwidth domain (`sdp`, `dram`), SoC calculation state (`sys_active`, `svp_prefetch`, `sys_idle`), output type, and output rate.
- `struct dml2_core_internal_mode_support_info` records both global support booleans and detailed failure reasons: scaling, format, DSC, link, MALL, clocks, bandwidth, prefetch, latency hiding, VM/PTE/DCC buffer, cursor, writeback, and p-state support. It also carries chosen per-plane outputs such as DPP count, ODM mode, DSC/FEC, aligned pitches, request sizes, bandwidth matrices, watermarks, and QoS support.
- `struct dml2_core_internal_mode_support` stores the mode-support working state and final recommended state: selected min-clock indices, required clocks, fabric/UCLK/DRAM bandwidth, DET/swath/VM/PTE/MCACHE/MALL metrics, urgent bandwidth, latency margins, DSC/backend state, p-state byte requirements, and chosen `uclk_pstate_switch_modes`.
- `struct dml2_core_internal_mode_program` mirrors many support fields for the programming pass and adds emitted programming data such as pipe-plane mapping, active pipe count, DLG/TTU timings, RQ register inputs, watermarks, stutter efficiency, sync values, DET/swath sizes, MCACHE offsets, and urgent bandwidth fractions.
- Parameter structs such as `dml2_core_calcs_CalculateVMRowAndSwath_params`, `dml2_core_calcs_CalculatePrefetchSchedule_params`, `dml2_core_calcs_CalculateWatermarksMALLUseAndDRAMSpeedChangeSupport_params`, and `dml2_core_calcs_calculate_mcache_setting_params` define explicit input/output bundles for shared algorithms.
- `struct dml2_core_shared_calculation_funcs` provides an overridable hook for `calculate_det_buffer_size`.
- `struct dml2_core_internal_scratch` centralizes locals and parameter structs, avoiding large stack allocations in deep calculator paths.
- `struct dml2_core_internal_display_mode_lib` aggregates IP/SoC capabilities, support/programming state, overridable functions, and scratch.
- `struct dml2_core_calcs_mode_support_ex` and `struct dml2_core_calcs_mode_programming_ex` are top-level call bundles for the public calculator APIs.

## Control flow and integration
The top-level DML flow initializes `dml2_core_internal_display_mode_lib`, runs mode support using `dml2_core_calcs_mode_support_ex`, then runs programming using `dml2_core_calcs_mode_programming_ex`. Support fills `ms` and support info; programming fills `mp` and final programming output. DPMM later consumes core outputs for min-clock and watermark mapping, while PMO can request alternate display configurations and min-clock indices that feed back into core support/programming.

## State and persistence behavior
The key persistent state is `dml2_core_internal_display_mode_lib`. Its `ms` and `mp` fields persist support/programming results; `scratch` is reusable transient storage. Most arrays are fixed-size by `DML2_MAX_PLANES`, `DML2_MAX_DCN_PIPES`, `DML2_MAX_MCACHES`, and similar constants, so consumers depend on consistent `num_planes`, `num_streams`, and support-info indexing.

## Dependencies
Includes external library dependencies plus `dml_top_display_cfg_types.h` and `dml_top_types.h`. It references many display configuration enums and structs: source format, swizzle, rotation, p-state methods/types, QoS parameter types, stream timing/output, MALL, DSC, writeback, MCACHE, and min-clock tables.

## Risks and edge cases
This header is high blast-radius: any field rename, array-size mismatch, or semantic change affects core calculators, DPMM, PMO, and top-level programming. Many structs use parallel arrays indexed by plane or stream, which makes off-by-one and stale index mapping likely if `num_planes` changes during implicit SubVP expansion. Scratch reuse assumes single-threaded or externally serialized use of a mode-lib instance. Optional clocks and table sizes must be handled carefully because some downstream code has guards for zero-entry DTB/DSC/PHY tables.

## Test signals
Tests should cover representative mode-support and programming passes across single/multi-plane, dual-plane formats, DCC enabled/disabled, VM enabled, MALL/SubVP, DSC, ODM/MPC combine, writeback, cursor, and p-state cases. ABI-style tests should at least compile all users after field changes. Invariants worth asserting include valid pipe-plane mappings, bounded array indices, non-negative bandwidth/watermark results, and coherent support booleans versus detailed failure flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_core/dml2_core_shared_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_core/dml2_core_utils.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_core/dml2_core_utils.c

## Purpose
Implements reusable core helpers for display format classification, logging support reasons, clock/table lookup, swizzle/tile traits, implicit SubVP expansion, encoder/link classification, ODM classification, and frame-time calculation. These helpers reduce duplication across DCN4 core calculators.

## Important APIs, types, and functions
- Format helpers: `dml2_core_utils_is_420()`, `dml2_core_utils_is_422_planar()`, `dml2_core_utils_is_422_packed()`, and `dml2_core_utils_is_dual_plane()` classify DML source formats and assert on unknown cases.
- Debug/string helpers: `dml2_core_utils_internal_bw_type_str()`, `dml2_core_utils_internal_soc_state_type_str()`, and `dml2_core_utils_print_mode_support_info()` map enums/support flags to verbose log text.
- Numeric helpers: `dml2_core_utils_div_rem()`, `dml2_core_utils_round_to_multiple()`, and `dml2_core_utils_log_and_substract_if_non_zero()` wrap common arithmetic.
- Mapping helpers: `dml2_core_util_get_num_active_pipes()` sums `dpps_used`; `dml2_core_utils_pipe_plane_mapping()` expands plane support into a pipe-to-plane array using the no-plane sentinel.
- Surface/tile helpers: `dml2_core_utils_is_phantom_pipe()`, `dml2_core_utils_get_tile_block_size_bytes()`, `dml2_core_utils_get_segment_horizontal_contiguous()`, `dml2_core_utils_is_linear()`, `dml2_core_utils_is_vertical_rotation()`, and `dml2_core_utils_get_gfx_version()` classify tiling, rotation, and phantom pipes.
- Clock/QoS helpers: `dml2_core_utils_get_qos_param_index()` and `dml2_core_utils_get_active_min_uclk_dpm_index()` map UCLK values to QoS/min-clock indices.
- Output/link helpers: `dml2_core_utils_get_stream_output_bpp()`, `dml2_core_utils_is_stream_encoder_required()`, `dml2_core_utils_is_encoder_dsc_capable()`, `dml2_core_utils_is_dp_encoder()`, `dml2_core_utils_is_dio_dp_encoder()`, `dml2_core_utils_is_hpo_dp_encoder()`, `dml2_core_utils_is_dp_8b_10b_link_rate()`, and `dml2_core_utils_is_dp_128b_132b_link_rate()`.
- `dml2_core_utils_expand_implict_subvp()` copies a display config and adds phantom streams/planes for implicit SubVP stage3 metadata.
- `dml2_core_utils_is_odm_split()` identifies split/MSO ODM modes, and `dml2_core_utils_get_frame_time_us()` derives frame duration from timing.

## Control flow and integration
Most functions are pure classifiers or mutators of caller-owned arrays. The notable multi-step flow is implicit SubVP expansion: copy the base config, reset scratch maps, optionally force unbounded requesting off before stage3, create phantom streams from valid `stage3.stream_svp_meta`, create matching phantom planes with MALL refresh disabled/no-data-return SVP mode, map phantom/main indices in scratch, and mark original planes as main pipes.

## State and persistence behavior
The helpers do not own persistent state. They mutate supplied arrays, `dml2_display_cfg`, and `dml2_core_scratch` structures. `expand_implict_subvp()` is stateful through scratch mapping arrays and increments `num_streams`/`num_planes` in the expanded config.

## Dependencies
Includes `dml2_core_utils.h`, which pulls internal shared types, debug logging, and float math. It relies on DML enums for source format, swizzle, rotation, encoder, DP link rate, ODM mode, p-state, and SubVP/MALL overrides.

## Risks and edge cases
Several format classifiers assert on unknown formats, so adding a new source format requires updating all switch statements. `dml2_core_utils_get_segment_horizontal_contiguous()` ignores `sw_mode` and returns `byte_per_pixel != 2`, which may be intentional but should be validated against future tiling modes. `get_active_min_uclk_dpm_index()` asserts if the exact UCLK is absent. `expand_implict_subvp()` can increase stream/plane counts and depends on capacity in fixed arrays; it also disables unbounded requesting before stage3 is performed.

## Test signals
Unit tests should exercise every source format, swizzle, encoder, link-rate, and ODM enum value. Integration tests should verify implicit SubVP expansion for no metadata, one SVP stream, multiple planes on a stream, stage3-performed versus not performed, and phantom-plane viewport height math. Clock-index tests should include exact matches, missing UCLK assertion paths, and zero-terminated QoS parameter tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_core/dml2_core_utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_core/dml2_core_utils.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_core/dml2_core_utils.h

## Purpose
Declares the core utility functions implemented in `dml2_core_utils.c`, giving core calculators access to shared arithmetic, enum classification, logging, clock lookup, implicit SubVP expansion, encoder/link helpers, and frame-time helpers.

## Important APIs, types, and functions
The header exports utility families for source-format classification, mode-support logging, output-bpp calculation, pipe/plane mapping, phantom/linear/rotation/swizzle classification, QoS/UCLK table indexing, implicit SubVP expansion, stream encoder and DP link-rate classification, ODM split detection, and frame time calculation.

## Control flow and integration
Core calculation code includes this header whenever it needs shared helper logic. `dml2_core_utils_expand_implict_subvp()` is the most integration-heavy declaration because it links `display_configuation_with_meta`, an expanded `dml2_display_cfg`, and `dml2_core_scratch`.

## State and persistence behavior
No state is stored in the header. Declared functions operate on caller-owned structs and arrays; many output arrays are indexed by plane or stream.

## Dependencies
Includes `dml2_internal_shared_types.h`, `dml2_debug.h`, and `lib_float_math.h`. The declarations reference internal support info, display config, plane/stream parameters, SoC state tables, QoS parameter tables, and display metadata.

## Risks and edge cases
Because this header is broadly included, any signature change can force widespread updates. Function names and semantics must stay aligned with utility implementation and with public core-calcs wrappers that expose similar enum-to-string helpers.

## Test signals
Compile coverage across core calculators is the first signal. Runtime tests should target the implementation behavior described in the `.c` research, especially enum coverage and implicit SubVP expansion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_core/dml2_core_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_dpmm/dml2_dpmm_dcn4.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_dpmm/dml2_dpmm_dcn4.c

## Purpose
Implements DCN3/DCN4/DCN42 display power management mapping. It converts core mode-support bandwidth/latency results into SoC DPM clock requests, rounds those requests to DPM table or DFS granularity, decides p-state and stutter feature support, and maps core watermarks into DCHUB register sets.

## Important APIs, types, and functions
- `dpmm_dcn3_map_mode_to_soc_dpm()` and `dpmm_dcn4_map_mode_to_soc_dpm()` are exported clock/power-feature mappers.
- `dpmm_dcn4_map_watermarks()` emits two DCHUB watermark sets from `mode_lib->mp.Watermark` and urgent bandwidth fractions.
- `dpmm_dcn42_map_watermarks()` emits four identical watermark sets for DCN42.
- `dram_bw_kbps_to_uclk_khz()` converts bandwidth to UCLK using DRAM geometry or an alternate bandwidth-to-clock table.
- `calculate_system_active_minimums()`, `calculate_svp_prefetch_minimums()`, and `calculate_idle_minimums()` compute UCLK/FCLK/DCFCLK requirements from active, SVP-prefetch, and idle bandwidth domains plus latency floor.
- `map_min_clocks_to_dpm()` chooses fine-grained or coarse-grained mapping and rounds global, per-plane DPPCLK, and per-stream DSC/DTB/PHY clocks.
- `add_margin_and_round_to_dfs_grainularity()`, `round_to_non_dfs_granularity()`, `round_up_and_copy_to_next_dpm()`, and `round_up_to_next_dpm()` implement clock quantization.
- `are_timings_trivially_synchronizable()`, `find_smallest_idle_time_in_vblank_us()`, and power-management feature helpers decide whether UCLK/FCLK p-state changes can be supported through blank/vactive/FAMS margin.

## Control flow and integration
The common `map_mode_to_soc_dpm()` first calculates active/SVP/idle minimums, boosts active clocks to prefetch requirements for NV4-like constraints, computes DISPCLK/DPPREFCLK/DTBREFCLK with downspread and ramp margins, rounds with DFS or non-DFS rules, derives per-plane DPPCLK ratios, copies deepsleep DCFCLK/SOCCLK, and maps all clocks to the SoC table. DCN3 then tries vblank, vactive+vblank, and FAMS-based p-state support before clamping unsupported UCLK/FCLK to max. DCN4 trusts successful stage3 for UCLK p-state, evaluates FCLK via vactive/vblank margin, clamps unsupported clocks, and evaluates stutter/Z8 blank support.

## State and persistence behavior
All state is written into caller-owned `dml2_display_cfg_programming`: `min_clocks.dcn4x`, per-plane/per-stream min clocks, p-state support booleans, stutter/Z8 support flags, global watermark register sets, and watermark-set count. Inputs are `display_cfg` mode-support results, SoC bounding box, min-clock table, IP params, and core mode-lib.

## Dependencies
Includes DPMM and internal shared types, top DML types, and float math. It consumes `dml2_core_mode_support_result`, `dml2_soc_state_table`, `dml2_mcg_min_clock_table`, `dml2_dram_params`, DCHUB global register sets, and core mode-lib watermark fields.

## Risks and edge cases
Clock table handling is sensitive. `round_up_and_copy_to_next_dpm()` includes a guard for zero-entry clock tables, avoiding an unsigned wrap/out-of-bounds read for absent clocks such as tied-off DTBCLK; similar code should preserve that behavior. Coarse-grained mapping assumes aligned UCLK/FCLK/DCFCLK table indices. `get_displays_with_fams_mask()` indexes `plane_descriptors->overrides` instead of `plane_descriptors[i].overrides`, which means it checks the first plane repeatedly and may under/over-report FAMS coverage. Watermark conversion truncates doubles to unsigned ref cycles.

## Test signals
Tests should cover fine-grained and coarse-grained clock tables, zero-entry optional clocks with zero and non-zero requested values, alternate DRAM bandwidth conversion, DFS and no-DFS rounding, downspread/ramp margin clamping, SVP prefetch boosting, p-state clamping paths, vblank/vactive support paths, all-stream timing sync/DRR cases, and DCN4 versus DCN42 watermark-set counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_dpmm/dml2_dpmm_dcn4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_dpmm/dml2_dpmm_dcn4.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_dpmm/dml2_dpmm_dcn4.h

## Purpose
Declares the DCN3/DCN4/DCN42 DPMM mapping functions used by the DPMM factory and top-level display programming.

## Important APIs, types, and functions
- `dpmm_dcn3_map_mode_to_soc_dpm()`
- `dpmm_dcn4_map_mode_to_soc_dpm()`
- `dpmm_dcn4_map_watermarks()`
- `dpmm_dcn42_map_watermarks()`
All functions operate on in/out parameter bundles from `dml2_internal_shared_types.h`.

## Control flow and integration
The factory assigns these functions into `dml2_dpmm_instance` callbacks by project id. Mode-to-DPM mapping is called after core mode-support/programming has produced bandwidth, clock, and latency data; watermark mapping is called when programming global DCHUB registers.

## State and persistence behavior
The functions declared here mutate caller-owned programming structures and do not own storage.

## Dependencies
Includes `dml2_internal_shared_types.h` for `dml2_dpmm_map_mode_to_soc_dpm_params_in_out` and `dml2_dpmm_map_watermarks_params_in_out`.

## Risks and edge cases
DCN3 and DCN4 function names coexist in a DCN4 header because DCN40/stage2 projects reuse the DCN3 policy path while later projects use DCN4 policy. Callers should not infer ASIC generation solely from the header name.

## Test signals
Factory wiring tests should verify the intended function is selected for each project id, and DPMM integration tests should confirm both DPM and watermark callbacks are non-null for supported projects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_dpmm/dml2_dpmm_dcn4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_dpmm/dml2_dpmm_factory.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_dpmm/dml2_dpmm_factory.c

## Purpose
Builds a `dml2_dpmm_instance` by project id and wires mode-to-DPM and watermark callbacks for the power-management mapping layer.

## Important APIs, types, and functions
- `dml2_dpmm_create()` is the exported factory.
- Dummy callbacks return true without mutating inputs and are used for stage1 and for projects where watermark mapping is intentionally inactive.
- DCN40 and DCN4 stage2 use `dpmm_dcn3_map_mode_to_soc_dpm()` plus dummy watermarks.
- DCN4 stage2 auto-DRR/SVP uses `dpmm_dcn4_map_mode_to_soc_dpm()` and `dpmm_dcn4_map_watermarks()`.
- DCN42 uses `dpmm_dcn4_map_mode_to_soc_dpm()` and `dpmm_dcn42_map_watermarks()`.

## Control flow and integration
The function validates `out`, clears it, switches on project id, assigns callbacks, and returns success. Top-level DML creation later invokes these callbacks through `dml2_dpmm_instance`.

## State and persistence behavior
Only the callback table inside caller-provided `out` persists. The factory does not store project id in the instance in this implementation.

## Dependencies
Includes the factory header, DCN4 DPMM declarations, and external library dependencies for `memset`.

## Risks and edge cases
Stage1 succeeds with dummy callbacks, unlike the core factory where stage1 fails. DCN40/stage2 mode mapping uses the DCN3 policy path but has no real watermark mapping. Callers must tolerate dummy watermarks for those projects or explicitly skip watermark programming.

## Test signals
Factory tests should assert callback identity for each project id, null-output failure, invalid-id failure, and that dummy callbacks return true. Integration tests should confirm projects expecting real watermark programming receive non-dummy callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_dpmm/dml2_dpmm_factory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_dpmm/dml2_dpmm_factory.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_dpmm/dml2_dpmm_factory.h

## Purpose
Declares the DPMM factory API for project-specific display power management mapping.

## Important APIs, types, and functions
- `dml2_dpmm_create(enum dml2_project_id project_id, struct dml2_dpmm_instance *out)` fills a caller-provided DPMM instance.

## Control flow and integration
The header is included by top-level initialization code that needs to bind DPMM callbacks and by the factory implementation.

## State and persistence behavior
No header-owned state. The declared function mutates `out`.

## Dependencies
Includes `dml2_internal_shared_types.h` and `dml_top_types.h`.

## Risks and edge cases
As with other DML factories, failure details are compressed into a bool. Unsupported projects leave the zeroed callback table unusable.

## Test signals
Compile/link coverage plus runtime creation tests for supported, unsupported, and null-output inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_dpmm/dml2_dpmm_factory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_mcg/dml2_mcg_dcn4.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_mcg/dml2_mcg_dcn4.c

## Purpose
Builds the DCN4 min-clock table used by core mode support and DPMM latency/bandwidth mapping. It derives DRAM bandwidth rows and associated minimum FCLK/DCFCLK requirements from SoC clock tables, derate factors, and fabric/return bus widths.

## Important APIs, types, and functions
- `mcg_dcn4_build_min_clock_table()` is the exported wrapper around `build_min_clock_table()`.
- `uclk_to_dram_bw_kbps()` converts UCLK and DRAM geometry into pre-derate DRAM bandwidth.
- `round_up_to_quantized_values()` maps computed clocks to the next provided clock-table value.
- `build_min_clk_table_fine_grained()` handles fine-grained or unequal DCFCLK/FCLK/UCLK table shapes by computing balanced bandwidth rows, shifting FCLK requirements upward, clamping to minimums and maximums, deriving DCFCLK from FCLK and bus ratios, pruning invalid rows, and pruning duplicate rows.
- `build_min_clk_table_coarse_grained()` copies aligned UCLK/FCLK/DCFCLK table rows directly.
- `build_min_clock_table()` validates inputs, fills fixed clocks, max clocks, spread-spectrum adjusted max clocks, chooses fine/coarse construction, and returns success.

## Control flow and integration
The MCG factory selects this builder for DCN40, DCN4 stage2, and DCN4 stage2 auto-DRR/SVP projects. The generated `dml2_mcg_min_clock_table` feeds core mode support and DPMM's latency minimum selection.

## State and persistence behavior
All persistent output is written to caller-provided `min_table`: fixed clocks, max clocks, max spread-spectrum clocks, and `dram_bw_table`. No static mutable state is used.

## Dependencies
Includes `dml2_mcg_dcn4.h` and SoC parameter types. It depends on SoC bounding-box clock tables, DRAM config, QoS derate percentages, fabric data-return width, return bus width, downspread percent, and max FCLK constraints.

## Risks and edge cases
The function rejects missing SoC/min-table pointers, DCFCLK/FCLK tables with fewer than two values, and UCLK tables larger than `DML_MCG_MAX_CLK_TABLE_SIZE`. It assumes max clock tables for DISPCLK/DPPCLK have at least one entry. Fine-grained duplicate pruning shifts entries using `entries[j + 1]`, so table bounds and row counts must remain valid. `round_up_to_quantized_values()` returns 0 if no value is larger than the input, which can later be pruned or misinterpreted if not expected.

## Test signals
Tests should cover coarse aligned tables, fine-grained two-entry DCFCLK/FCLK tables, unequal table counts, max-FCLK clamping, duplicate pruning, invalid over-max pruning, downspread max-SS calculations, and invalid input/table-size failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_mcg/dml2_mcg_dcn4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_mcg/dml2_mcg_dcn4.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_mcg/dml2_mcg_dcn4.h

## Purpose
Declares the DCN4 MCG min-clock table builder and a unit-test hook.

## Important APIs, types, and functions
- `mcg_dcn4_build_min_clock_table()` fills a `dml2_mcg_min_clock_table` from SoC bounding-box data.
- `mcg_dcn4_unit_test()` is declared but not implemented in the researched file set, suggesting a legacy or external test hook.

## Control flow and integration
The MCG factory wires `mcg_dcn4_build_min_clock_table()` for DCN40 and DCN4 stage2 variants. The unit-test declaration is not used in the nearby source files inspected.

## State and persistence behavior
No header-owned state. The builder mutates its in/out parameter bundle.

## Dependencies
Includes `dml2_internal_shared_types.h` for MCG parameter and table structures.

## Risks and edge cases
The declared `mcg_dcn4_unit_test()` can cause link failures if referenced without an implementation. Keep declaration/implementation status in sync if adding automated tests.

## Test signals
Compile/link tests should ensure the factory-visible builder resolves. Dedicated MCG tests should target the implementation behavior from `dml2_mcg_dcn4.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_mcg/dml2_mcg_dcn4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_mcg/dml2_mcg_dcn42.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_mcg/dml2_mcg_dcn42.c

## Purpose
Builds a DCN42-specific min-clock table. Unlike the DCN4 builder, this version uses FCLK table rows as the primary row count and computes DRAM bandwidth from UCLK plus WCK ratio, matching the newer memory-clock representation.

## Important APIs, types, and functions
- `mcg_dcn42_build_min_clock_table()` is the exported wrapper.
- `uclk_to_dram_bw_kbps()` computes bandwidth as `uclk * channel_count * channel_width_bytes * wck_ratio * 2`.
- `build_min_clk_table_coarse_grained()` iterates over FCLK rows, uses matching UCLK/WCK rows where available, and repeats the last UCLK bandwidth/min-UCLK for extra FCLK rows.
- `build_min_clock_table()` validates pointers and UCLK table size, fills fixed clocks, max clocks, spread-spectrum max clocks, DCFCLK/FCLK max, and invokes coarse table construction.

## Control flow and integration
The MCG factory routes `dml2_project_dcn42` to this builder. Its output is consumed by core support and DPMM the same way as the DCN4 min-clock table, but the `dram_bw_table.entries[].min_uclk_khz` field is explicitly populated for alternate DRAM bandwidth conversion.

## State and persistence behavior
All state is written into caller-provided `dml2_mcg_min_clock_table`. No static mutable state is used.

## Dependencies
Includes the DCN42 MCG header and SoC parameter types. It depends on SoC clock tables for UCLK, WCK ratio, DCFCLK, FCLK, DISPCLK, DPPCLK, DSC/DTB/PHY clocks, and fixed ref clocks.

## Risks and edge cases
The implementation assumes FCLK, DCFCLK, DISPCLK, and DPPCLK tables have entries; only optional DSC/DTB/PHY max clocks guard zero entries. If FCLK has more entries than UCLK, the last UCLK entry is reused, so table ordering and WCK ratio alignment are critical. It validates UCLK count against `DML_MCG_MAX_CLK_TABLE_SIZE` but not FCLK count explicitly.

## Test signals
Tests should include equal UCLK/FCLK row counts, extra FCLK rows, WCK ratio changes, optional zero-entry DSC/DTB/PHY clocks, downspread max-SS calculations, and invalid null/oversized UCLK inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_mcg/dml2_mcg_dcn42.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_mcg/dml2_mcg_dcn42.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_mcg/dml2_mcg_dcn42.h

## Purpose
Declares the DCN42 min-clock table builder.

## Important APIs, types, and functions
- `mcg_dcn42_build_min_clock_table(struct dml2_mcg_build_min_clock_table_params_in_out *in_out)`.

## Control flow and integration
The MCG factory includes this header and assigns the function for `dml2_project_dcn42`.

## State and persistence behavior
No header-owned state. The builder mutates the supplied min-clock table through the in/out bundle.

## Dependencies
Includes `dml2_internal_shared_types.h`.

## Risks and edge cases
The header intentionally exposes only the builder. DCN42 behavior differences live entirely in the implementation, so any new DCN42 min-clock policy entry points need explicit additions.

## Test signals
Compile/link coverage through `dml2_mcg_factory.c` and runtime DCN42 min-clock table tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_mcg/dml2_mcg_dcn42.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_mcg/dml2_mcg_factory.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_mcg/dml2_mcg_factory.c

## Purpose
Constructs a `dml2_mcg_instance` and assigns the project-specific min-clock table builder.

## Important APIs, types, and functions
- `dml2_mcg_create()` is the exported factory.
- Stage1 receives a dummy builder that returns true without building a table.
- DCN40, DCN4 stage2, and DCN4 stage2 auto-DRR/SVP use `mcg_dcn4_build_min_clock_table()`.
- DCN42 uses `mcg_dcn42_build_min_clock_table()`.

## Control flow and integration
The function validates `out`, zeroes the instance, switches on project id, fills `build_min_clock_table`, and returns success. Top-level DML initialization uses this instance before core mode-support/DPMM mapping.

## State and persistence behavior
The only persistent state is the callback pointer in `dml2_mcg_instance`. No project id is stored.

## Dependencies
Includes MCG factory, DCN4/DCN42 builder headers, and external library dependencies.

## Risks and edge cases
Stage1 succeeds with a dummy builder, which can leave downstream code with an uninitialized or unchanged min-clock table if it expects real entries. Unsupported/invalid projects return false with zeroed callbacks.

## Test signals
Factory tests should cover null output, invalid id, stage1 dummy behavior, DCN4-family callback assignment, and DCN42 callback assignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_mcg/dml2_mcg_factory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_mcg/dml2_mcg_factory.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_mcg/dml2_mcg_factory.h

## Purpose
Declares the MCG factory API.

## Important APIs, types, and functions
- `dml2_mcg_create(enum dml2_project_id project_id, struct dml2_mcg_instance *out)`.

## Control flow and integration
Top-level DML setup includes this header to create the min-clock generator instance before building min-clock tables used by core and DPMM.

## State and persistence behavior
No header-owned state; the declared function writes the callback table into `out`.

## Dependencies
Includes `dml2_internal_shared_types.h` and `dml_top_types.h`.

## Risks and edge cases
Factory failure is boolean-only. Consumers must not call the callback unless creation succeeds and the callback is non-null.

## Test signals
Compile/link coverage and factory runtime tests for supported/unsupported project ids.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_mcg/dml2_mcg_factory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_pmo/dml2_pmo_dcn3.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_pmo/dml2_pmo_dcn3.c

## Purpose
Implements the DCN3-style PMO optimizer used by DCN40/DCN4 stage2 projects in this tree. It adjusts display configurations for DCC/MCACHE admissibility, dynamic ODM voltage-minimum optimization, and UCLK p-state support through reserved vblank time and min-clock latency index search.

## Important APIs, types, and functions
- `pmo_dcn3_initialize()` stores SoC/IP/options pointers, combine limits, and MCG table size in the PMO instance.
- `pmo_dcn3_optimize_dcc_mcache()` increases MPC combine or ODM combine factors when planes fail DCC/MCACHE support and free pipes are available.
- `pmo_dcn3_init_for_vmin()`, `pmo_dcn3_test_for_vmin()`, and `pmo_dcn3_optimize_for_vmin()` implement dynamic ODM optimization to reduce DISPCLK below vmin limits.
- `pmo_dcn3_init_for_pstate_support()`, `pmo_dcn3_test_for_pstate_support()`, and `pmo_dcn3_optimize_for_pstate_support()` build and iterate reserved-vblank-time/min-latency candidates for p-state support.
- Helpers include sorting/deduplicating candidate times, getting/setting reserved vblank time per stream, increasing MPC/ODM combine factors, testing horizontal timing divisibility, DP encoder eligibility, synchronizability, and highest ODM load selection.

## Control flow and integration
Initialization is first. DCC/MCACHE optimization copies the display config when needed, counts used/free pipes, then either applies no-ODM MPC expansion or single-stream ODM expansion depending on stream/ODM state. Vmin init marks unoptimizable streams based on disable options, existing MPC combine, SVP, horizontal divisibility, and non-DP encoders; optimization then chooses the stream with highest pixel-clock-per-ODM load and tries the next legal ODM combine mode. P-state init builds per-stream candidate reserved times from existing reservations and optional FCLK/UCLK/stutter requirements, then optimization iterates latency index upward first and falls back to lower reserved-time candidate combinations.

## State and persistence behavior
Persistent PMO state lives in `dml2_pmo_instance`: SoC/IP/options pointers, combine limits, MCG table size, and `scratch.pmo_dcn3` search state (`min_latency_index`, `max_latency_index`, `cur_latency_index`, stream mask, reserved-time candidates/counts, current candidate indices). Optimizers mutate copied `display_configuation_with_meta` or `dml2_display_cfg` outputs, especially stage3/stage4 metadata, `reserved_vblank_time_ns`, `odm_mode`, and `mpcc_combine_factor`.

## Dependencies
Includes PMO factory and DCN3 PMO header. Uses internal shared structures for display configs, stage3/stage4 metadata, SoC power-management blackout times, mode-support result, cfg support info, stream/plane descriptors, PMO options, and IP pipe counts.

## Risks and edge cases
The code assumes fixed stream/plane masks fit in small integer masks (`0xF`). `optimize_dcc_mcache()` has single-stream ODM logic that indexes `stream_descriptors[i]` while iterating planes, which is only safe when plane and stream indices align in the intended single-stream case. Dynamic ODM legality depends on horizontal timing divisibility and DSC slice divisibility; missing a case can cause unsupported transitions. Candidate iteration spelling aside, the search order can reduce reserved time only after exhausting latency indices. Stage3 `performed` is set during p-state init, so downstream code sees optimization as active even before a successful final candidate.

## Test signals
Tests should cover no free pipes, MPC combine limit, ODM combine limit, multi-stream no-ODM optimization, single-stream ODM expansion, vmin disabled options, non-DP encoder rejection, horizontal divisibility by 2/4, DSC slice divisibility by 3/4, vmin DISPCLK threshold, p-state candidate sorting/deduplication, latency-index iteration, and reserved-vblank propagation to all planes on a stream.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_pmo/dml2_pmo_dcn3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_pmo/dml2_pmo_dcn3.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_pmo/dml2_pmo_dcn3.h

## Purpose
Declares the DCN3 PMO callback set used by the PMO factory for DCN40/DCN4 stage2 projects.

## Important APIs, types, and functions
Exports initialization, DCC/MCACHE optimization, vmin init/test/optimize, and p-state init/test/optimize functions. All use in/out bundles from `dml2_internal_shared_types.h`.

## Control flow and integration
The PMO factory assigns these functions into `dml2_pmo_instance` callbacks. The top-level optimizer calls the init/test/optimize triples during staged optimization loops.

## State and persistence behavior
No header-owned state. The functions mutate PMO instance scratch and optimized display configuration outputs.

## Dependencies
Includes `dml2_internal_shared_types.h`.

## Risks and edge cases
The header exposes only UCLK p-state callback names; factory users map them to `init_for_uclk_pstate`/`test_for_uclk_pstate`/`optimize_for_uclk_pstate`. Any FCLK/stutter extension would require new declarations or reuse of generic callback slots.

## Test signals
Compile/link coverage through `dml2_pmo_factory.c` plus runtime tests for each callback family described in the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_pmo/dml2_pmo_dcn3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_pmo/dml2_pmo_dcn42.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_pmo/dml2_pmo_dcn42.c

## Purpose
Defines a DCN42 PMO policy implementation that uses vblank-only p-state strategies for one to four displays. It initializes DCN4-style PMO strategy lists while disabling FAMS-specific parameter ranges and provides a strict DCN42 p-state support test.

## Important APIs, types, and functions
- Static `dcn42_strategy_list_1_display` through `_4_display` each contain one strategy: all active streams use `dml2_pstate_method_vblank`, inactive slots use `dml2_pstate_method_na`, and `allow_state_increase` is true.
- `pmo_dcn42_initialize()` stores PMO instance pointers/limits/options, zeros FAMS refresh-rate limits, selects override strategy lists or built-in DCN42 lists, and expands them with `pmo_dcn4_fams2_expand_base_pstate_strategies()`.
- `pmo_dcn42_test_for_pstate_support()` accepts all-streams-blanked configs, rejects missing candidates, then requires every active stream candidate to be vblank method with enough reserved time and no positive vactive p-state margin.

## Control flow and integration
The code is structurally compatible with the DCN4 FAMS2 PMO scratch/init data. Initialization iterates display counts 1..4, selects a base list from options or static defaults, chooses the corresponding expanded output array, asserts base list size, and calls the FAMS2 strategy expander. The test function reads `scratch.pmo_dcn4.cur_pstate_candidate`, `pstate_strategy_candidates`, and stream plane masks to validate current strategy state.

## State and persistence behavior
Writes into `dml2_pmo_instance`: SoC/IP/options pointers, combine limits, MCG table size, FAMS parameter defaults, and expanded DCN4 strategy-list storage in `init_data.pmo_dcn4`. Test reads PMO scratch but does not mutate it.

## Dependencies
Includes DCN42 PMO header, float math, debug logging, and `dml2_pmo_dcn4_fams2.h`. It depends on FAMS2 helper functions `pmo_dcn4_fams2_expand_base_pstate_strategies()`, `dcn4_get_minimum_reserved_time_us_for_planes()`, and `dcn4_get_vactive_pstate_margin()`.

## Risks and edge cases
In the researched factory, `dml2_project_dcn42` is routed to `pmo_dcn4_fams2_initialize()` and related FAMS2 callbacks, not to `pmo_dcn42_initialize()` or `pmo_dcn42_test_for_pstate_support()`. That makes this file potentially unused unless another factory or build path wires it. If enabled, its policy intentionally rejects non-vblank methods and any positive vactive p-state margin, so it is stricter than FAMS-capable policies. Override strategy lists can change behavior but still pass through the same expander.

## Test signals
Tests should first verify whether the build/factory actually wires these functions. Direct unit tests should cover one to four streams, override and default strategies, all-streams-blanked bypass, invalid `cur_pstate_candidate`, insufficient reserved time, positive vactive margin, and non-vblank candidate rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_pmo/dml2_pmo_dcn42.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_pmo/dml2_pmo_dcn42.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_pmo/dml2_pmo_dcn42.h

## Purpose
Declares DCN42-specific PMO initialization and p-state support test functions.

## Important APIs, types, and functions
- Forward declares `struct dml2_pmo_initialize_in_out` and `struct dml2_pmo_test_for_pstate_support_in_out`.
- Exports `pmo_dcn42_initialize()` and `pmo_dcn42_test_for_pstate_support()`.

## Control flow and integration
The header is intended for factory or project-specific PMO wiring. In the researched factory, the DCN42 project currently uses DCN4 FAMS2 callbacks instead of these declarations, so integration should be verified before relying on them.

## State and persistence behavior
No header-owned state. Declared functions mutate/read `dml2_pmo_instance` through their in/out bundles.

## Dependencies
Includes `dml2_internal_shared_types.h`.

## Risks and edge cases
Forward declarations keep the header narrow but can hide mismatches until implementation compile time. The apparent lack of factory wiring is the main integration risk.

## Test signals
Compile/link coverage if factory wiring is added, plus direct DCN42 PMO policy tests described for the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_pmo/dml2_pmo_dcn42.h -->

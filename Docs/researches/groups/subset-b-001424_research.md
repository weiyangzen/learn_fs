# subset-b-001424 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/display_mode_core.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/display_mode_core.h

## Purpose
`display_mode_core.h` is the public C interface for the legacy DML 2.0 display mode core. It exposes mode-support evaluation, mode-programming generation, bandwidth helpers, row-height calculation, and many accessor functions for computed watermarks, clocks, pipe timing, request queue, DCC, MALL, and DET values.

## Important APIs, types, and functions
The main entry points are `dml_core_mode_support()`, `dml_core_mode_support_partial()`, `dml_core_mode_programming()`, `dml_mode_support()`, `dml_mode_programming()`, and `dml_mode_support_ex()`. `dml_core_get_row_heights()` computes DPTE/meta row heights for a plane and tiling mode. `dml_get_return_bw_mbps()` and `dml_get_return_bw_mbps_vm_only()` expose return bandwidth formulas. The `dml_get_var_decl` and `dml_get_per_surface_var_decl` macros declare a broad getter surface for values stored in `struct display_mode_lib_st`.

## Control flow
This header has no implementation logic, but it defines the expected flow for callers: fill `display_mode_lib_st` with SoC/IP/policy/display state, call support evaluation for a state or display config, optionally call programming with a clock policy, then consume register/programming outputs through getters. The `dml_mode_support_ex_params_st` path wraps support evaluation with input and output pointers.

## State and persistence behavior
All state is caller-owned in `struct display_mode_lib_st`. The API mutates only in-memory mode support/programming fields; it has no durable persistence and no independent allocation contract in this header.

## Dependencies and integration points
It depends on `display_mode_core_structs.h` for the full DML data model and integrates with DML calculation implementations elsewhere in `dml2_0`. Consumers include wrapper layers that translate driver `dc_state` into DML inputs and consume DCHUB/HUBP timing outputs.

## Risks and edge cases
The getter set is macro-declared and easy to desynchronize from implementation fields. Many getters are per-surface and assume valid plane indices under `__DML_NUM_PLANES__`. Clock and bandwidth helpers operate on model units, so kHz/MHz/Mbps conversion mistakes at wrapper boundaries can produce invalid programming.

## Test signals
Useful signals are build coverage for every getter implementation, mode-support/programming tests over single and multi-plane configs, bandwidth unit checks, row-height checks for linear/tiled/rotated/420 cases, and comparison of generated RQ/DLG/TTU values against known DML vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/display_mode_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/display_mode_core_structs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/display_mode_core_structs.h

## Purpose
`display_mode_core_structs.h` is the central schema for DML 2.0 mode evaluation and programming. It defines project, output, tiling, format, rotation, MALL, p-state, ODM/MPC, and clock-policy enums; SoC and IP bounding-box structures; display input configuration; support-failure reporting; programming outputs; parameter blocks; scratch storage; and register layout structures.

## Important APIs, types, and functions
Key types are `struct display_mode_lib_st`, `struct dml_display_cfg_st`, `struct dml_mode_eval_policy_st`, `struct dml_mode_support_info_st`, `struct mode_support_st`, and `struct mode_program_st`. Input is split across `dml_surface_cfg_st`, `dml_plane_cfg_st`, `dml_timing_cfg_st`, `dml_output_cfg_st`, `dml_writeback_cfg_st`, `dml_hw_resource_st`, and `dml_clk_cfg_st`. Calculation helper parameter blocks include `UseMinimumDCFCLK_params_st`, `CalculateWatermarksMALLUseAndDRAMSpeedChangeSupport_params_st`, `CalculateVMRowAndSwath_params_st`, `CalculateSwathAndDETConfiguration_params_st`, `CalculateStutterEfficiency_params_st`, and `CalculatePrefetchSchedule_params_st`. Register ABI structures include `dml_display_rq_regs_st`, `dml_display_dlg_regs_st`, `dml_display_ttu_regs_st`, and `dml_display_arb_params_st`.

## Control flow
The file has no executable flow, but it encodes the data flow through the core: SoC/IP/policy/display inputs enter `display_mode_lib_st`; mode support fills `mode_support_st` and `dml_mode_support_info_st` with pass/fail reasons, resource choices, bandwidths, p-state support, and intermediate swath/DET values; mode programming fills `mode_program_st` with clocks, watermarks, DLG/TTU/RQ timing, DCC blocks, MALL use, p-state support, and pipe-to-plane mapping.

## State and persistence behavior
All structures are in-memory state owned by a DML context or caller. Large local-state blocks are explicitly aggregated under `display_mode_lib_scratch_st` to reduce stack pressure. There is no persistence outside the caller's lifetime.

## Dependencies and integration points
The header depends on `display_mode_lib_defines.h` and `dml_top_display_cfg_types.h`. It is the common contract between DML calculation code, debug dump helpers, and driver wrappers that translate kernel display state into model inputs and map model outputs to hardware programming.

## Risks and edge cases
Most arrays are fixed at `__DML_NUM_PLANES__` or two combine-state slots, so overflow depends on wrappers correctly bounding stream/plane counts. The schema mixes units such as MHz, kHz, MBytes, KBytes, bytes, cycles, lines, and microseconds. Support booleans include both positive and negative semantics, making debug output and guard logic easy to invert. Layout changes can silently break consumers that memcpy register structures or scratch sub-blocks.

## Test signals
Validation should cover structure-size/layout-sensitive builds, maximum-plane configs, no-plane/blank-stream configs, 420/422/RGB formats, DSC/ODM/MPC combinations, hostvm/gpuvm page-table levels, MALL/subviewport p-state modes, immediate flip, dynamic metadata, and known-vector comparisons for support reasons and programming fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/display_mode_core_structs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/display_mode_lib_defines.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/display_mode_lib_defines.h

## Purpose
`display_mode_lib_defines.h` provides compile-time constants, common typedefs, and base DML dependencies for the legacy DML 2.0 core. It fixes the model dimensions and feature presence expected by the rest of the DML source.

## Important APIs, types, and functions
Important defines include `DCN_DML__NUM_PLANE` as 8, `DCN_DML__NUM_CURSOR` as 1, `DCN_DML__NUM_PWR_STATE` as 30, `DCN_DML__VM_PRESENT`, `DCN_DML__HOST_VM_PRESENT`, `__DML_MIN_DCFCLK_FACTOR__`, `__DML_MAX_VRATIO_PRE__`, `__DML_MAX_VRATIO_PRE_ENHANCE_PREFETCH_ACC__`, and `__DML_PIPE_NO_PLANE__`. It defines `dml_int_t`, `dml_uint_t`, `dml_float_t`, and `dml_bool_t`.

## Control flow
There is no runtime control flow. Preprocessor constants determine array sizes, debug inclusion, and formula limits used by calculation and debug helper code.

## State and persistence behavior
The file creates no runtime state. It constrains the memory layout of every structure that uses the fixed plane, cursor, and power-state constants.

## Dependencies and integration points
It includes `dml_depedencies.h`, `dml_logging.h`, and `dml_assert.h`, making logging and assertion behavior available to all including DML headers. It is included by `display_mode_core_structs.h` and thereby becomes a core dependency for most DML code.

## Risks and edge cases
Changing plane or power-state counts is ABI-like for the local DML structures. `__DML_VBA_DEBUG__` is enabled unconditionally here, so debug print paths can be compiled into builds depending on downstream macro handling. The comments note historical VBA type compatibility; changing typedef widths would break layout and formula assumptions.

## Test signals
Build tests should verify all DML users compile with the fixed dimensions. Runtime tests should include eight-plane stress cases, power-state table bounds, and debug logging builds with assertions enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/display_mode_lib_defines.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/display_mode_util.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/display_mode_util.c

## Purpose
`display_mode_util.c` implements common DML math, format, mapping, and debug-print utilities. It is support code for formula implementation and for dumping DML inputs, support status, bounding boxes, clock policies, and generated register structures.

## Important APIs, types, and functions
Math helpers include `dml_ceil()`, `dml_floor()`, `dml_min*()`, `dml_max*()`, `dml_log()`, `dml_log2()`, `dml_round()`, `dml_pow()`, and `dml_round_to_multiple()`. Format and mapping helpers include `dml_util_is_420()`, `dml_is_vertical_rotation()`, `dml_get_cursor_bit_per_pixel()`, `dml_get_num_active_planes()`, `dml_get_num_active_pipes()`, `dml_get_plane_idx()`, `dml_get_pipe_idx()`, and `dml_calc_pipe_plane_mapping()`. Debug routines print RQ, DLG, TTU, policy, mode-support, display-config, SoC bounding-box, and clock-config structures.

## Control flow
The math functions are direct formula helpers. Debug functions walk fixed-size or caller-supplied plane counts and emit fields with `dml_print()`, with `fail_only` filtering in `dml_print_dml_mode_support_info()`. Mapping functions count active planes from nonzero viewport width, sum `DPPPerSurface` for active planes, and build `pipe_plane` by expanding each plane's DPP count.

## State and persistence behavior
The file has no persistent state. It reads caller-provided DML structures and may depend on `ASSERT()` for invalid formats or missing pipe mappings. It writes only to logging output and output arrays supplied by callers.

## Dependencies and integration points
It depends on `display_mode_util.h`, the DML core structures, `dml_print()`, and `ASSERT()`. Its outputs feed diagnostics and the pipe-plane mapping used by mode programming consumers.

## Risks and edge cases
The private `_log()` type-puns a `float` through `int *`, which is sensitive to aliasing and IEEE layout assumptions. `dml_util_is_420()` asserts on several source formats rather than returning false. `dml_get_num_active_planes()` treats a zero viewport width as inactive. `dml_calc_pipe_plane_mapping()` does not bounds-check the expanded DPP count against `__DML_NUM_PLANES__`. Debug dumps have many fields and can drift from structure changes.

## Test signals
Useful signals include formula regression vectors, NaN behavior for min/max, zero granularity handling, 420/rotation/cursor mappings, pipe-plane mapping with ODM/MPC multi-DPP cases, invalid enum assertion tests, and debug-output smoke tests for populated support and programming structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/display_mode_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/display_mode_util.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/display_mode_util.h

## Purpose
`display_mode_util.h` declares the legacy DML utility surface for math helpers, format classifiers, debug dump functions, and pipe/plane mapping helpers.

## Important APIs, types, and functions
It exports arithmetic helpers, `dml_util_is_420()`, `dml_is_vertical_rotation()`, cursor bpp conversion, print helpers for DML register/config/support/bounding-box structures, active plane/pipe counters, `dml_get_plane_idx()`, `dml_get_pipe_idx()`, and `dml_calc_pipe_plane_mapping()`.

## Control flow
The header has no control flow. It groups utility prototypes behind `__DML_DLL_EXPORT__` so the same signatures can be shared by standalone/tool and in-driver builds.

## State and persistence behavior
The header defines no state. Function implementations operate on caller-owned in-memory DML structures and logging callbacks.

## Dependencies and integration points
It includes `display_mode_core_structs.h`, `cmntypes.h`, `dml_assert.h`, and `dml_logging.h`. It is a low-level dependency for calculation code and debug consumers.

## Risks and edge cases
Because it exposes debug routines for many structure types, any schema change in `display_mode_core_structs.h` may require prototype or implementation updates. Callers must pass valid plane counts and pipe indices; the utility contract does not encode bounds in types.

## Test signals
Build coverage across standalone and kernel-style inclusion, function-level regression tests for math/mapping helpers, and debug dump smoke tests are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/display_mode_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/dml21_translation_helper.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/dml21_translation_helper.c

## Purpose
`dml21_translation_helper.c` translates AMD DC driver state into DML 2.1 display configuration and translates DML programming results back into `dc_state` bandwidth, watermark, p-state, and mcache-related fields. It is the bridge between kernel display objects and the DML2.1 core.

## Important APIs, types, and functions
Public functions include `dml21_populate_dml_init_params()`, `dml21_map_dc_state_into_dml_display_cfg()`, `map_plane_to_dml21_display_cfg()`, `dml21_copy_clocks_to_dc_state()`, `dml21_extract_watermark_sets()`, `dml21_map_hw_resources()`, `dml21_get_pipe_mcache_config()`, `dml21_set_dc_p_state_type()`, and `dml21_init_min_clocks_for_dc_state()`. Internal helpers map DCN revision to DML project ID, populate PMO options, convert timings/output formats/swizzles, derive scaler and plane descriptors, create dummy planes for blank streams, and map forced p-state policies.

## Control flow
Initialization selects a DML project from `in_dc->ctx->dce_version`, gets native or externally supplied SoC/IP data, and applies debug/config PMO options. Display mapping clears prior mappings, seeds GPUVM/HostVM/global overrides, iterates DC streams, populates stream timing/output/override descriptors, and then either creates a dummy plane for blank streams or maps each real plane through surface and plane descriptor population. Stable mappings are kept with stream IDs and synthesized plane IDs. Output copy functions then transfer DML clocks, watermarks, mcache pipe geometry, hardware resource mapping, and p-state method decisions into DC structures.

## State and persistence behavior
State is stored inside `dml2_context->v21`: `dml_init`, `display_config`, `dml_to_dc_pipe_mapping`, and mode-programming outputs. The file mutates `dc_state->bw_ctx` and `pipe_ctx` fields but has no durable persistence.

## Dependencies and integration points
It depends on DC core structures, debug flags, `soc_and_ip_translator`, DML internal shared types, DML2 top-level API structures, scaler callbacks, SVP/FAMS callbacks, and DC resource callbacks. It integrates with `dml21_wrapper_fpu.c` for validate/programming flow and `dml21_utils.c` for pipe programming.

## Risks and edge cases
Unsupported DCN revisions map to invalid project ID after logging. Timing conversion includes DSC padding, frame packing, DRR min refresh clamping, and optional flickerless vtotal callbacks. Swizzle conversion asserts for unsupported Addr3 modes and defaults some GFX9 unsupported modes to 64KB 2D for test compatibility. Blank streams get dummy planes and can affect counts. `dml21_map_hw_resources()` marks every mapping slot valid even when source validity is sparse. Plane ID encoding depends on stream/plane ordering remaining stable during validation.

## Test signals
Coverage should include DCN4.01 and DCN4.2 initialization, native and external SoC/IP paths, blank streams, multi-plane streams, DSC padding, VRR/Freesync/DRR, DP2.0 detection, HDMI/eDP/DP output mapping, Addr3 and GFX9 swizzles, forced p-state methods, HostVM/GPUVM levels, watermark set copies, mcache plane1 enablement, and p-state type mapping for vactive/vblank/SVP/DRR.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/dml21_translation_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/dml21_translation_helper.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/dml21_translation_helper.h

## Purpose
`dml21_translation_helper.h` declares the translation boundary between DC state and the DML 2.1 model. It keeps most dependencies as forward declarations while exposing the functions needed by the wrapper and utility layers.

## Important APIs, types, and functions
The header declares initialization translation, display-config mapping, clock/watermark extraction, hardware-resource mapping, mcache pipe config generation, p-state type mapping, display-config plane lookup, and minimum-clock initialization.

## Control flow
There is no executable flow. The intended sequence is initialize DML input parameters, map a `dc_state` into `dml2_display_cfg`, run DML core checks/programming, then copy clocks/watermarks/resources back.

## State and persistence behavior
No state is defined here. Implementations operate on `dml2_context`, `dc_state`, `pipe_ctx`, and DML programming objects owned by callers.

## Dependencies and integration points
It forward declares DC and DML types and is included by `dml21_wrapper_fpu.c` and `dml21_utils.c`. It is also part of the local contract for resource-management code that needs plane/display-config mapping.

## Risks and edge cases
The prototypes expose several DML internal types, so include order must provide complete definitions before use in C files. `map_plane_to_dml21_display_cfg()` returns an unsigned value but uses `UINT_MAX` as the invalid sentinel in implementation, requiring callers to compare carefully.

## Test signals
Build coverage of every including translation unit and validation paths that exercise each declared function are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/dml21_translation_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/dml21_utils.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/dml21_utils.c

## Purpose
`dml21_utils.c` contains DML2.1 wrapper utilities that resolve DML-to-DC mappings, program DC pipe contexts from DML outputs, create SubVP phantom streams/planes, accumulate MALL allocation sizes, detect DP2.0, and build FAMS2 firmware programming payloads.

## Important APIs, types, and functions
Lookup helpers include `dml21_helper_find_dml_pipe_idx_by_stream_id()`, `dml21_find_dml_pipe_idx_by_plane_id()`, `dml21_get_plane_id()`, `dml21_get_dc_plane_idx_from_plane_id()`, `find_valid_pipe_idx_for_stream_index()`, and `find_pipe_regs_idx()`. Programming helpers include `dml21_find_dc_pipes_for_plane()`, `dml21_pipe_populate_global_sync()`, `dml21_populate_mall_allocation_size()`, `dml21_program_dc_pipe()`, `dml21_handle_phantom_streams_planes()`, `dml21_build_fams2_programming()`, and `dml21_is_plane1_enabled()`.

## Control flow
Pipe resolution uses DML mapping tables to find the DC stream, plane index, real DPP pipes, and optional paired phantom pipes. Pipe programming copies global sync, selects pipe-register slice by ODM/MPC indices, copies normal or phantom HUBP register sets, updates unbounded request and DET sizes, records max DPP clock, accumulates MALL usage, and sets DC p-state type. Phantom handling creates paired streams and planes for DML-programmed SubVP, then remaps DC pipes. FAMS2 building resets firmware payloads, skips blank/phantom streams, copies DML static state, fills DC pipe masks and OTG IDs, and adds SubVP phantom mask details.

## State and persistence behavior
The file mutates only in-memory `dc_state` and `pipe_ctx` state: global sync, hubp registers, mcache/MALL accounting, FAMS2 payloads, pipe masks, and p-state type. Phantom streams/planes are created through callback-owned DC state mechanisms and removed by wrapper validation before subsequent runs.

## Dependencies and integration points
It depends on DML2 internal types, DML core DCN4 calculations, translation helpers, DC resource management, and callback tables in `dml2_context->config`. It integrates directly with `dml21_wrapper_fpu.c` after DML mode programming succeeds.

## Risks and edge cases
Several functions assume mapping tables and `plane_descriptor` pointers are valid. `find_valid_pipe_idx_for_stream_index()` dereferences `plane_descriptor` without checking null. Phantom plane creation duplicates many main-plane fields but adjusts only clip height. FAMS2 bit masks assume pipe indices fit in the mask width. `is_sub_vp_enabled()` scans all pipes and relies on paired-stream callbacks. Plane1 enablement uses a broad enum range that includes more than classic 420 formats.

## Test signals
Validation should cover multi-DPP/ODM/MPC pipe-register indexing, blank streams, SubVP phantom creation/removal/remapping, real and phantom MALL accounting, DP2.0 encoder detection with missing HPO link encoders, FAMS2 vblank/vactive/DRR/SubVP payloads, pipe mask correctness, p-state type assignment, and null/invalid mapping resilience.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/dml21_utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/dml21_utils.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/dml21_utils.h

## Purpose
`dml21_utils.h` declares the DML2.1 utility functions used to map DML programming results onto DC pipe state and firmware payload state.

## Important APIs, types, and functions
It declares mapping lookup helpers, pipe-register index helpers, `dml21_find_dc_pipes_for_plane()`, `dml21_program_dc_pipe()`, phantom stream/plane handling, FAMS2 programming, DP2.0 detection, MALL allocation accounting, and plane1 enablement.

## Control flow
The header has no logic. It organizes the utility sequence used after DML mode programming: resolve mappings, find pipes, program pipe-level state, add phantoms when needed, and build firmware programming.

## State and persistence behavior
No state is declared here. Callers pass `dml2_context`, `dc_state`, `pipe_ctx`, and DML programming objects to implementation functions.

## Dependencies and integration points
It forward declares DC and DML types and is included by DML2.1 translation, wrapper, and resource-management code. Its prototypes rely on `__DML2_WRAPPER_MAX_STREAMS_PLANES__` and DML enum definitions being visible before inclusion in some compile units.

## Risks and edge cases
Because several APIs accept raw arrays sized by a macro, callers must allocate the expected number of entries. Invalid mapping return values use signed `int` for some functions and unsigned for others elsewhere, so comparisons need care.

## Test signals
Compile coverage plus DML2.1 programming tests with normal, ODM/MPC split, blank, and SubVP states exercise the declared surface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/dml21_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/dml21_wrapper.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/dml21_wrapper.c

## Purpose
`dml21_wrapper.c` owns non-FPU DML2.1 context allocation, destruction, and copy semantics. It allocates the persistent DML2.1 context, embedded DML instance, and programming buffer used by validation and programming flows.

## Important APIs, types, and functions
Public APIs are `dml21_create()`, `dml21_destroy()`, `dml21_copy()`, and `dml21_create_copy()`. The internal `dml21_allocate_memory()` allocates `struct dml2_context`, `struct dml2_instance`, and `struct dml2_display_cfg_programming`, then wires mode-support and mode-programming pointers to the shared instance/display config.

## Control flow
Creation allocates memory and then calls FPU-side `dml21_init()`. Destroy frees the inner DML instance and programming buffer. Copy preserves destination-owned internal allocation pointers, memcpy-copies the source context and nested objects into destination allocations, restores all internal self-references, and reinitializes the copied instance with `dml2_initialize_instance()`. Create-copy combines allocation and copy.

## State and persistence behavior
The persistent state is heap-allocated kernel memory for the DML context and its nested DML instance/programming output. No on-disk persistence exists. The destroy path frees nested allocations but does not free the outer `struct dml2_context`, implying ownership remains with the caller or a higher wrapper.

## Dependencies and integration points
It depends on `vzalloc()`, `vfree()`, optional `DC_RUN_WITH_PREEMPTION_ENABLED`, DML top-level initialization, DML2 internal types, wrapper FPU functions, and DC FPU infrastructure. It is called during DC state/context lifecycle management.

## Risks and edge cases
Allocation failure after earlier successful allocations leaks memory because `dml21_allocate_memory()` returns false without cleanup. `dml21_destroy()` does not null-check or free the outer context. Copy relies on deep-copying only two nested allocations; new internal pointers added to `struct dml2_context` would need explicit restoration. Reinitialization after copy is required for internal references and is a key regression point.

## Test signals
Fault-injection tests for each allocation, create/destroy leak checks, create-copy equivalence tests, copied-context validation tests, and FPU/preemption wrapper build coverage are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/dml21_wrapper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/dml21_wrapper.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/dml21_wrapper.h

## Purpose
`dml21_wrapper.h` exposes the DML2.1 context lifecycle API and declares shared wrapper-side structures for external SoC/IP parameters and DC mcache programming inputs.

## Important APIs, types, and functions
It declares `dml21_create()`, `dml21_destroy()`, `dml21_copy()`, and `dml21_create_copy()`. `struct socbb_ip_params_external` carries externally supplied `dml2_ip_capabilities` and `dml2_soc_bb` for debugging/tool flows. `struct dc_mcache_params` describes per-plane mcache allocation validity, dedicated requirements, plane0/plane1 cache counts, last-slice sharing flags, and x-offset boundaries.

## Control flow
The header has no implementation logic. Its comments define lifecycle expectations: creation is part of DC state creation and initializes DML2.1 IP/SOC/states immediately.

## State and persistence behavior
The declared structures are in-memory configuration/programming carriers. `dc_mcache_params` is populated from DML mode-programming output and consumed by DC resource callbacks.

## Dependencies and integration points
It includes OS and DML top SoC/display type headers. It is included by wrapper, translation, FPU validation, and callers that need external bounding-box injection or mcache allocation data.

## Risks and edge cases
The mcache offset arrays are fixed at `DML2_MAX_MCACHES + 1`; allocation producers and hardware programmers must agree on boundary semantics. External SoC/IP injection can bypass native translator safeguards, so invalid tables can poison all downstream validation.

## Test signals
Compile coverage, external SoC/IP debug initialization, mcache allocation cases with plane0/plane1 sharing, and lifecycle create/copy/destroy tests are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/dml21_wrapper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/dml21_wrapper_fpu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/dml21_wrapper_fpu.c

## Purpose
`dml21_wrapper_fpu.c` implements the FPU-protected DML2.1 initialization, validation, mode-programming, DC hardware-state mapping, clock/watermark/register copy-out, FAMS2 generation, and mcache programming preparation.

## Important APIs, types, and functions
Public APIs are `dml21_init()`, `dml21_reinit()`, `dml21_validate()`, and `dml21_prepare_mcache_programming()`. Internal helpers include `dml21_populate_configuration_options()`, `dml21_check_mode_support()`, `dml21_mode_check_and_programming()`, `dml21_calculate_rq_and_dlg_params()`, and `dml21_prepare_mcache_params()`.

## Control flow
Initialization copies configuration, applies debug-forced p-state options, populates DML init parameters, and initializes the DML2 instance. Non-programming validation scrubs prior phantom streams/planes, maps DC state into DML display config, and calls `dml2_check_mode_supported()`. Programming validation clears state, handles empty stream lists with minimum clocks and FAMS2 reset, removes phantoms, maps display config, calls `dml2_build_mode_programming()`, maps DC pipes, creates SubVP phantoms, optionally allocates mcache, copies per-pipe DCHUB/HUBP registers, clocks, watermarks, and FAMS2 payloads. Mcache preparation builds per-plane/per-pipe descriptors, calls `dml2_build_mcache_programming()`, then copies generated mcache registers into main and phantom pipes.

## State and persistence behavior
The file mutates `dml2_context->v21` scratch, display config, mode support, mode programming, and `dc_state->bw_ctx` plus pipe fields. Phantom streams/planes are transient runtime DC state. No persistent storage is used.

## Dependencies and integration points
It depends on DML top-level APIs, DML2 DC resource management, translation helpers, utility helpers, resource-pool callbacks, SVP/FAMS callbacks, and DC bandwidth context structures. It is the main integration point called by DC validation paths.

## Risks and edge cases
The programming path is sensitive to stale phantom state, so callback ordering matters. `dml21_calculate_rq_and_dlg_params()` appears to index max supported dispclk/dppclk with `num_clk_values`, which is one past the last valid element if the count is a conventional length. Empty-stream handling skips full DML mode programming but still seeds clocks and FAMS2 state. Mcache phantom indexing must stay aligned with DML's main-plane count. Skipping hardware-state mapping suppresses pipe/register copy-out.

## Test signals
Critical signals include validate-only and validate-and-programming modes, empty state, allocation of SubVP phantoms, mcache allocation/programming with and without phantom planes, skip-hw-state-mapping behavior, clock/watermark copy correctness, max clock table bounds, FAMS2 required and legacy-pstate paths, and repeated validation after phantom cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/dml21_wrapper_fpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/dml21_wrapper_fpu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/dml21_wrapper_fpu.h

## Purpose
`dml21_wrapper_fpu.h` declares the FPU-requiring DML2.1 wrapper entry points for initialization, reinitialization, validation, and mcache register preparation.

## Important APIs, types, and functions
It declares `dml21_init()`, `dml21_reinit()`, `dml21_validate()`, and `dml21_prepare_mcache_programming()`. The comments document validate modes: mode-only and state-index validation avoid populating `context.res_ctx`, while programming validation generates hardware programming for the new state.

## Control flow
The header defines the public sequence expected by callers: initialize or reinitialize the context, validate a `dc_state` according to requested mode, and later prepare mcache programming after allocation data exists.

## State and persistence behavior
No state is declared. Implementations mutate caller-owned DML and DC state. The comments explicitly warn that concurrent validation requires separate `dc_state` objects.

## Dependencies and integration points
It includes OS and DML top-level type headers and forward declares DC/DML types. It is included by lifecycle code in `dml21_wrapper.c` and by DC validation callers operating inside FPU protection.

## Risks and edge cases
Concurrency is the primary documented risk: two threads must not invoke validation concurrently on shared state. Callers must also honor FPU protection requirements; the type system does not enforce that.

## Test signals
Build coverage, FPU-protected call-path tests, validate-mode behavior, concurrent separate-state validation, and mcache preparation after successful programming are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/dml21_wrapper_fpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/inc/bounding_boxes/dcn42_soc_bb.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/inc/bounding_boxes/dcn42_soc_bb.h

## Purpose
`dcn42_soc_bb.h` defines static DML2.1 SoC and IP bounding boxes for DCN42. These constants provide default clock tables, memory topology, QoS derates, latency parameters, power-management blackout times, vmin limits, cache sizes, and IP resource limits.

## Important APIs, types, and functions
Key objects are `dml_dcn42_variant_a_soc_qos_params`, `dml2_socbb_dcn42`, `dcn42_ddr5_power_management_parameters`, and `dml2_dcn42_max_ip_caps`. The SoC box includes one-entry clocks for uclk/fclk/dcfclk/dispclk/dppclk/dtbclk/phyclk/socclk/dscclk, LPDDR5/LPCAMM2 DRAM config, DCN3-style QoS, MALL/mcache sizing, HostVM/GPUVM page sizes and levels, and `max_fclk_for_uclk_dpm_khz`. IP caps describe four pipes/OTGs/DSC units, return/compressed/meta buffers, cursor buffer, flip limits, SubVP timings, and FAMS2 delays/timeouts.

## Control flow
The header has no runtime flow. Translators include or copy these constants into `dml2_initialize_instance_in_out` when native SoC/IP construction selects DCN42 defaults.

## State and persistence behavior
All data is static compile-time constant except `dcn42_ddr5_power_management_parameters`, which is a global parameter block for DDR5 tuning. There is no runtime persistence.

## Dependencies and integration points
It depends on `dml_top_soc_parameter_types.h` and integrates with the SoC/IP translator and DML2.1 initialization path. The wrapper copies selected values into clock and validation outputs.

## Risks and edge cases
These constants directly affect validation margins; stale derates or blackout latencies can cause false support or false rejection. DCN42 uses `qos_type = dml2_qos_param_type_dcn3` despite being a DCN4-family target, so translator expectations must match. Single-entry clock tables reduce indexing flexibility and should be covered alongside multi-entry DCN401 tables.

## Test signals
Known-mode validation on DCN42, LPDDR5/LPCAMM2 and DDR5 power-management variants, SubVP/FAMS2 timing cases, HostVM/GPUVM page-level checks, mcache allocation, and clock-table bounds tests are important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/inc/bounding_boxes/dcn42_soc_bb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/inc/bounding_boxes/dcn4_soc_bb.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/inc/bounding_boxes/dcn4_soc_bb.h

## Purpose
`dcn4_soc_bb.h` defines static DML2.1 SoC and IP bounding boxes for DCN401/DCN4. It supplies clock tables, memory and fabric topology, DCN4x QoS parameters, power-management latencies, MALL/mcache settings, and IP resource caps.

## Important APIs, types, and functions
Key constants are `dml_dcn4_variant_a_soc_qos_params`, `dml2_socbb_dcn401`, and `dml2_dcn401_max_ip_caps`. The SoC table includes multi-entry fclk/dcfclk/dispclk/dppclk/dtbclk/socclk values, uclk and per-uclk DPM QoS latency arrays, GDDR-like DRAM topology, 64 MB MALL allocation, 512 outstanding requests, 64-byte return paths, GPUVM minimum page size, and DCN4x QoS margins. IP caps define four pipes/OTGs/DSC units, larger ROB/config return buffer values than DCN42, flip limits, SubVP margins, and FAMS2 timing constants.

## Control flow
The file has no executable control flow. Its constants are consumed during native SoC/IP construction for DCN4.01 and then guide mode support and programming calculations.

## State and persistence behavior
All state is static constant data in the compiled image. It is copied into DML initialization structures and not persisted elsewhere.

## Dependencies and integration points
It depends on `dml_top_soc_parameter_types.h`. It integrates with DML2.1 initialization selected by `dml21_dcn_revision_to_dml2_project_id()` for `DCN_VERSION_4_01` and with downstream clock/watermark/register calculations.

## Risks and edge cases
The multi-entry clock tables make off-by-one max-clock indexing particularly important. QoS arrays contain several per-uclk DPM entries with `minimum_uclk_khz = 0`, so selection logic must rely on surrounding translator/core semantics. Power-management latencies are much higher than DCN42 for DRAM clock change and stutter, so cross-project reuse would be risky.

## Test signals
DCN401 validation vectors, multi-clock-table bounds checks, UCLK/FCLK p-state support, SubVP/FAMS2 scheduling, MALL/mcache allocation, high-bandwidth four-pipe cases, and comparisons against hardware characterization are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/inc/bounding_boxes/dcn4_soc_bb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/inc/dml2_external_lib_deps.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/inc/dml2_external_lib_deps.h

## Purpose
`dml2_external_lib_deps.h` is a minimal dependency bridge for DML2.1 external-library builds. It currently just includes `os_types.h` behind an include guard.

## Important APIs, types, and functions
The file declares no APIs or types of its own. Its effective export is the OS type definitions made available through `os_types.h`.

## Control flow
There is no control flow.

## State and persistence behavior
No runtime or persistent state is defined.

## Dependencies and integration points
It integrates DML2.1 headers with the surrounding AMD DC OS abstraction layer. Include order can use this header where external DML code needs basic bool/integer/platform types without pulling larger driver headers.

## Risks and edge cases
The risk is low, but if external-library builds require additional platform shims, this thin header is where missing type dependencies may surface. Over-expanding it would increase coupling.

## Test signals
Standalone DML2.1 build coverage and kernel build coverage with this include path are sufficient signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/inc/dml2_external_lib_deps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/inc/dml_top.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/inc/dml_top.h

## Purpose
`dml_top.h` is the top-level public interface for the DML2 core used by DML2.1 wrappers. It declares instance sizing, initialization, support checking, full mode programming, and mcache programming APIs.

## Important APIs, types, and functions
The API surface is `dml2_get_instance_size_bytes()`, `dml2_initialize_instance()`, `dml2_check_mode_supported()`, `dml2_build_mode_programming()`, and `dml2_build_mcache_programming()`. Parameter and output structures come from `dml_top_types.h`.

## Control flow
Callers allocate or provide an instance, initialize it with SoC/IP/options, call support checks for boolean feasibility, call build-mode-programming for optimized clocks and register values, and call build-mcache-programming after mcache allocation and pipe geometry are known.

## State and persistence behavior
The DML instance is caller-owned memory. The API fills in-out structures and programming outputs in memory only; there is no persistence.

## Dependencies and integration points
It depends on `dml_top_types.h`. `dml21_wrapper.c` and `dml21_wrapper_fpu.c` call these functions to initialize and validate DML2.1 contexts and to produce DC hardware programming.

## Risks and edge cases
Correct sequencing matters: mcache programming requires successful mode programming first, and build-mode-programming is the only path that returns full optimized hardware values. Callers must manage instance allocation size and lifetime consistently with the implementation.

## Test signals
Instance-size/allocation tests, initialization with DCN401/DCN42 bounding boxes, support-only checks, full programming checks, mcache programming after allocation, and invalid sequencing tests are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/inc/dml_top.h -->

# subset-b-001425 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/inc/dml_top_dchub_registers.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/inc/dml_top_dchub_registers.h

## Purpose
`dml_top_dchub_registers.h` defines the DML21 output structures that carry calculated DC hub, HUBP, DLG, TTU, request queue, MCache, arbitration, and watermark register values from the DML core to the display driver. The file is data-only: it has no functions and exists as a stable typed contract between the calculation code in `src/dml2_core/dml2_core_dcn4_calcs.c`, the programming aggregate in `dml_top_types.h`, and wrapper/translation code that copies the results into DC pipe and watermark structures.

## Important APIs, Types, And Data Shapes
The main per-pipe register payload is `struct dml2_dchub_per_pipe_register_set`, which groups `dml2_display_rq_regs`, `dml2_display_ttu_regs`, `dml2_display_dlg_regs`, and a segment-count style `det_size`. `dml2_display_dlg_regs` holds timing and prefetch register values such as `refcyc_h_blank_end`, `dst_y_prefetch`, VM/PTE row request timings, line delivery timings, cursor offset timing, dynamic metadata timing, and MRQ metadata timing fields. `dml2_display_ttu_regs` carries QoS watermarks, request delivery timing, fixed QoS levels, and ramp-disable flags for luma, chroma, and cursor.

Request queue programming is split into `dml2_display_plane_rq_regs` for plane-local chunk, PTE, swath, and metadata chunk sizing, and `dml2_display_rq_regs` for luma/chroma plane RQ registers plus expansion modes, plane base selection, unbounded requesting, PTE buffer mode, one-row-for-frame, and MRQ expansion. MCache output is represented by `dml2_display_mcache_regs` and `dml2_hubp_pipe_mcache_regs`, with separate main and MALL entries for plane0 and plane1.

Global outputs use `dml2_display_arb_regs` for arbitration and compression-buffer policy, `dml2_dchub_watermark_regs` for watermark and QoS timing, `enum dml2_dchub_watermark_reg_set_index` for sets A through D, and `dml2_dchub_global_register_set` for one arbitration set plus up to four watermark sets.

## Control Flow And Integration
This header does not execute control flow. It is populated by calculation helpers such as `dml2_core_calcs_get_pipe_regs()`, `dml2_core_calcs_get_watermarks()`, and `dml2_core_calcs_get_arb_params()` in `dml2_core_dcn4_calcs.c`. `dml2_core_dcn4.c` stores per-pipe values in `dml2_display_cfg_programming.pipe_regs` and points each `dml2_per_plane_programming.pipe_regs[]` entry at the correct slot. Wrapper code later copies these structures into hardware-facing DC structures: for example, `dml21_program_dc_pipe()` copies a selected `dml2_dchub_per_pipe_register_set` into `pipe_ctx->hubp_regs`, and `dml21_extract_watermark_sets()` copies `dml2_dchub_watermark_regs` into DCN4 watermark sets.

## State And Persistence Behavior
The structures are transient programming state for a mode validation/programming pass. They are not persisted to disk and do not own memory. Pointer ownership is managed outside this header, primarily by `dml2_display_cfg_programming`, which contains backing arrays and per-plane pointers into them. Register values are `uint32_t` because the file models actual calculated hardware register fields; only a few booleans appear for software decisions such as `pte_buffer_mode` and `force_one_row_for_frame`.

## Dependencies
The file includes `dml2_external_lib_deps.h` for integer and boolean types. It is included by `dml_top_types.h`, which embeds these register sets in public programming outputs. Its field names must stay aligned with generated/ported DML calculations and DC wrapper expectations.

## Risks And Edge Cases
Most fields are unvalidated plain integers, so calculation-side unit conversion and fixed-point scaling errors can silently become bad register programming. `det_size` is stored as a segment count in DML programming but later multiplied by 64 KB by the wrapper; mismatched segment sizing would corrupt DET allocation. Watermark indexing relies on `DML2_DCHUB_WATERMARK_SET_NUM` remaining four and matching DCN4 set layout. MRQ fields are present beside legacy fields, so code paths must keep DCN4/DCN42 feature checks correct before consuming metadata request registers.

## Test Signals
Useful signals are mode-programming tests that inspect DLG/RQ/TTU fields for known display configurations, DC pipe programming tests that verify `pipe_ctx->hubp_regs` and `det_buffer_size_kb`, and watermark extraction tests that verify sets A through D are copied only up to `num_watermark_sets`. Boundary cases should include cursor-enabled planes, chroma planes, DCC/MRQ-enabled formats, SubVP phantom pipes, immediate flip, and unbounded request overrides.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/inc/dml_top_dchub_registers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/inc/dml_top_display_cfg_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/inc/dml_top_display_cfg_types.h

## Purpose
`dml_top_display_cfg_types.h` defines the public DML21 display configuration input model. It describes planes, streams, surface layout, timing, link output, writeback, overrides, and MCache configuration descriptors used by the DML top layer, PMO, DPMM, and core calculation code. It is the primary caller-facing structure for "what display mode should DML validate and program?"

## Important APIs, Types, And Data Shapes
The header establishes fixed maxima with `DML2_MAX_PLANES`, `DML2_MAX_DCN_PIPES`, `DML2_MAX_MCACHES`, and `DML2_MAX_WRITEBACK`. Enumerations classify input tiling (`dml2_swizzle_mode`), pixel/source format (`dml2_source_format_class`), chroma siting (`dml2_sample_positioning`), rotation, output format, encoder type, DP link rate, p-state type, UCLK strategy, SubVP and MALL overrides, ODM/MSO modes, scaling transform, DSC policy, TDLUT mode, and Twait budgeting policy.

`struct dml2_surface_cfg` describes plane0/plane1 dimensions, pitch, tiling, and optional DCC pitch/rate metadata. `struct dml2_composition_cfg` describes rotation, mirroring, output scaling intent, viewport rectangles for plane0/plane1, stationary behavior, and scaler/tap ratios including EASF, ISHARP, and UPSP controls. `struct dml2_timing_cfg` captures timing totals, active area, blanking, sync widths, pixel clock, bits per component, DSC overrides, interlace, DRR flags, and nominal vblank.

`struct dml2_plane_parameters` binds a plane to a stream and combines pixel format, surface, composition, metadata, cursor, TDLUT, immediate flip, and per-plane policy/HW overrides. `struct dml2_stream_parameters` holds timing, link output, writeback configuration, and stream-level ODM/SubVP/Twait overrides. `struct dml2_display_cfg` is the top-level input: VM mode flags, page-table levels, plane and stream descriptor arrays, counts, DET reallocation policy, and global overrides for HW forcing, power management, synchronization, SubVP implicit PMO, blanking, and DML debug knobs.

The MCache descriptors at the end, `dml2_pipe_configuration_descriptor` and `dml2_plane_mcache_configuration_descriptor`, are used by MCache programming to map calculated per-plane allocation onto actual pipe viewport slices.

## Control Flow And Integration
There are no functions here, but these types drive almost every DML21 pass. `dml21_translation_helper.c` builds `dml2_display_cfg` from DC state. `dml2_top_soc15.c` copies and mutates it during mode support and programming. `dml2_pmo_*` optimizers consume the same structure to choose p-state, SubVP, DRR, and ODM strategies. `dml2_core_dcn4.c` may copy the input, expand implicit SubVP into phantom streams and planes, and pass the expanded config to `dml2_core_calcs_mode_support_ex()` and `dml2_core_calcs_mode_programming_ex()`.

The config also feeds generated register extraction: `dml2_core_dcn4_calcs.c` reads surface, composition, timing, VM, cursor, DCC, DSC, writeback, and override fields to calculate support, bandwidth, register values, and informative diagnostics.

## State And Persistence Behavior
`dml2_display_cfg` is copied by value through many layers. It has no internal allocation and no ownership pointers, which makes `memcpy()` the dominant persistence pattern inside a single validation/programming pass. The top context stores a current display config, but the data is runtime state, not persistent storage. Counts such as `num_planes`, `num_streams`, `active_writebacks_per_stream`, and `num_cursors` are critical bounds for fixed-size arrays.

## Dependencies
The file includes `dml2_external_lib_deps.h` for standard types. It is included by `dml_top_types.h` and referenced by core, PMO, DPMM, wrapper, translation helper, and generated calculation files. Some fields are closely coupled to DC hardware concepts, such as DET, DCC, DSC, ODM, DRR, SubVP, MALL, TDLUT, VM page tables, and writeback.

## Risks And Edge Cases
Array bounds depend on callers honoring `DML2_MAX_PLANES`, `DML2_MAX_DCN_PIPES`, `DML2_MAX_MCACHES`, and `DML2_MAX_WRITEBACK`; invalid counts can cause later loops to overrun fixed arrays. Pixel format semantics determine whether plane1 is used, so incorrect format translation can distort chroma bandwidth, viewport, and MCache allocation. Overrides are powerful and bypass normal policy; debug forcing for unbounded requests, DET size, clocks, PTE buffer mode, and SubVP can create hardware-programming results that are valid for simulation but unsafe for production if leaked. Several fields combine units in kHz, MHz, us, ns, pixels, lines, bytes, and elements, so translation tests are important.

## Test Signals
Strong test signals include round-trip translation tests from DC state to `dml2_display_cfg`, mode-support coverage for RGB, planar YUV, mono, DCC, cursor, TDLUT, writeback, DSC, DRR, ODM, and SubVP inputs, and negative tests for viewport exceeding surface, pitch alignment, unsupported scaling/taps, and invalid link rates. Boundary tests should exercise maximum planes/streams, no-output or writeback-only streams, hostvm/gpuvm enablement, forced hardware overrides, and synchronized timing policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/inc/dml_top_display_cfg_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/inc/dml_top_policy_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/inc/dml_top_policy_types.h

## Purpose
`dml_top_policy_types.h` defines the small public policy-parameter surface used by DML21 top-level options. It currently provides tunables that influence display-mode policy decisions without changing the display configuration or SoC/IP bounding boxes.

## Important APIs, Types, And Data Shapes
The only exported type is `struct dml2_policy_parameters`. It contains `odm_combine_dispclk_threshold_khz`, a threshold for ODM combine policy decisions based on display clock, and `max_immediate_flip_latency`, a cap for immediate-flip latency policy. There are no functions, enums, or macros beyond the include guard.

## Control Flow And Integration
This header is included by `dml_top_types.h`, making policy parameters part of the broader top-level DML API surface. The exact structure is not heavily referenced in this subset, but policy concepts are reflected in `dml2_pmo_options`, mode support, and mode programming paths where ODM, immediate flip, p-state, DRR, and SubVP strategy are selected.

## State And Persistence Behavior
The policy structure is plain runtime configuration. It owns no memory and has no persistence behavior. Because it is a small scalar struct, callers can safely copy it by value, but absent defaults must be handled by initialization code outside this file.

## Dependencies
The file has no includes. It depends only on standard C integer types being available through includers or compiler defaults for `unsigned long` and `unsigned int`. Its main dependency is conceptual: consumers must interpret the units consistently as kHz and latency units expected by the policy code.

## Risks And Edge Cases
The structure has no validity flags, so zero can mean either "unset" or a real threshold depending on consumer interpretation. Unit ambiguity for `max_immediate_flip_latency` should be checked at call sites. As the policy surface grows, adding fields without explicit initialization in callers could change mode-selection behavior.

## Test Signals
Tests should verify default initialization, explicit ODM threshold behavior near the boundary value, and immediate-flip latency behavior when the cap is zero, below calculated latency, and above calculated latency. Compile-time integration through `dml_top_types.h` is also useful because this header intentionally stays minimal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/inc/dml_top_policy_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/inc/dml_top_soc_parameter_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/inc/dml_top_soc_parameter_types.h

## Purpose
`dml_top_soc_parameter_types.h` defines the public SoC and IP bounding-box model for DML21. These structures describe clocks, DRAM topology, QoS latency parameters, power-management blackout/exit latencies, VM/page-table limits, MALL and MCache sizing, and hardware capability counts. The data is consumed by minimum-clock generation, mode support, mode programming, watermark calculation, and project-specific DCN4/DCN42 initialization.

## Important APIs, Types, And Data Shapes
`DML_MAX_CLK_TABLE_SIZE` fixes clock and per-DPM arrays at 20 entries. `dml2_soc_derate_values` and `dml2_soc_derates` model bandwidth/clock derates for active urgent/average, DCN MALL prefetch, and idle states. `dml2_soc_qos_parameters` carries writeback latency and a union of DCN32x and DCN4x QoS parameters selected by `enum dml2_qos_param_type`. DCN4-specific QoS includes fabric response and transport timing plus `dml2_dcn4_uclk_dpm_dependent_qos_params` per UCLK DPM state.

`dml2_soc_power_management_parameters` contains blackout and stutter timing for DRAM/FCLK/PPT/temp-read/power states, including per-DPM G6 temp-read blackout and Type B delays. `dml2_clk_table`, `dml2_dram_params`, and `dml2_soc_state_table` describe clock tables and memory configuration. `dml2_soc_bb` is the main SoC bounding box, joining clock state, QoS, power management, vmin limits, bandwidth targets, reference clocks, MALL, outstanding request limits, return bus geometry, VM page settings, downspread, DCC/MCache attributes, and FCLK/UCLK coupling.

`dml2_ip_capabilities` describes display IP resources and feature limits: pipe/OTG/DSC/writeback counts, DP/HDMI output counts, return/compression buffer sizes, cursor buffer, flip limits, hostvm mode, MRQ presence, SubVP timing, PPT/temp/dummy p-state delay allowances, and FAMS2 timing fields.

## Control Flow And Integration
Initialization copies `dml2_soc_bb` and `dml2_ip_capabilities` into `dml2_core_internal_display_mode_lib` in `core_dcn4_initialize()` and `core_dcn42_initialize()`. MCG code builds minimum clock tables from `dml2_soc_bb`. DPMM maps mode requirements back to SoC DPM states using the clock tables. The core calculations read QoS, bandwidth, latency, VM, and capability fields to decide support and produce watermarks, pipe registers, and informative diagnostics. Static bounding-box headers such as `inc/bounding_boxes/dcn4_soc_bb.h` and `dcn42_soc_bb.h` instantiate these types.

## State And Persistence Behavior
These structures are runtime copies of platform bounding-box constants or caller-provided overrides. They contain only scalar values and fixed arrays, so they are copied by value with `memcpy()`. No data is persisted by this header. The `num_clk_values` fields in `dml2_clk_table` are the active lengths for clock arrays and are critical for loops such as UCLK DPM lookup.

## Dependencies
The file includes `dml2_external_lib_deps.h` for `bool` and integer types. It is used by public top-level types, internal shared types, MCG, DPMM, PMO, core DCN4/DCN42 initialization, and generated calculation helpers. It is tightly coupled to hardware-specific units and to DCN generation differences, especially the DCN3 versus DCN4 QoS union.

## Risks And Edge Cases
Clock table length or ordering errors can map a mode to the wrong DPM level. `lookup_uclk_dpm_index_by_freq()` in the DCN4 core returns 0 when no exact UCLK match is found, so missing or rounded clock values can silently select the first DPM entry. Many latency and bandwidth fields are doubles or unsigned integers with implicit units; inconsistent kHz/MHz/us/cycle conversions will affect mode support and watermark safety. The QoS union requires `qos_type` to match the populated member. Feature flags such as `dcn_mrq_present`, `hostvm_mode`, `no_dfs`, and MCache sizing must match the actual ASIC, or DML can accept unsupported programming.

## Test Signals
Tests should cover representative DCN40 and DCN42 bounding boxes, fine/coarse clock-table generation, exact and missing UCLK DPM lookup, QoS type selection, MRQ-enabled versus disabled paths, hostvm/gpuvm page-table limits, FAMS2 delay fields, MALL capacity limits, and watermark sensitivity to power-management blackout values. Static assertions or validation helpers for `num_clk_values <= DML_MAX_CLK_TABLE_SIZE` would catch high-impact configuration errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/inc/dml_top_soc_parameter_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/inc/dml_top_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/inc/dml_top_types.h

## Purpose
`dml_top_types.h` is the central public DML21 type contract. It includes display configuration, SoC/IP parameters, policy types, DCHUB register outputs, and DMUB FAMS2 command types, then defines top-level instance options, API in/out structs, mode-support diagnostics, and mode-programming output. It connects caller input (`dml2_display_cfg`, `dml2_soc_bb`, `dml2_ip_capabilities`) to calculated programming (`dml2_display_cfg_programming`).

## Important APIs, Types, And Data Shapes
Project and output enums include `dml2_project_id`, `dml2_pstate_change_support`, output type/rate classifications, and `dml2_pstate_method`. `dml2_pmo_options` and `dml2_options` hold top-level policy options for PMO strategies such as vblank, SubVP, DRR, FAMS2, dynamic ODM, and per-plane override strategy lists. Top-level in/out wrappers include `dml2_initialize_instance_in_out`, `dml2_reset_instance_in_out`, `dml2_check_mode_supported_in_out`, `dml2_build_mode_programming_in_out`, `dml2_build_mcache_programming_in_out`, and `dml2_unit_test_in_out`.

`dml2_mcache_surface_allocation` models calculated MCache slicing for plane0/plane1 and MALL: validity, dedicated-MALL requirement, cache counts, X offsets, shift granularity, global IDs, last-slice sharing, and metadata row-size diagnostics. `dml2_per_plane_programming` ties a plane descriptor to minimum clocks, MCache allocation, required DPP count, UCLK p-state support method, MALL size requirements, per-pipe register pointers, and optional phantom-plane programming. `dml2_per_stream_programming` carries stream descriptor pointers, clocks, global sync programming, ODM count, UCLK p-state method, optional phantom stream, and FAMS2 base/sub-state DMUB command data.

`dml2_mode_support_info` is a large diagnostic structure containing the overall support flag, immediate flip support, detailed per-reason booleans, selected ODM/MPC/DSC/FEC decisions, DPP counts, output type/rate, aligned pitches, p-state support, bandwidth support, QoS support, and clock support. `dml2_display_cfg_programming` is the main output aggregate: it embeds the display config, minimum clocks for DCN32x/DCN4x, p-state support, FAMS2 flags/config, stutter and Z8 support, global DCHUB registers, per-plane and per-stream programming arrays, pipe register backing storage, and a large `informative` diagnostics block with watermarks, plane info, DPP, MALL, QoS, CRB, DCC, power-management, misc DLG/prefetch metrics, mode support info, voltage level, non-optimized MCache allocation, and failure flags.

## Control Flow And Integration
This header has no functions, but its structs are the inputs and outputs used by top-level DML functions. `dml2_core_factory.c` selects DCN4/DCN42 function pointers based on `dml2_project_id`. `dml2_top_soc15.c` initializes instances, checks mode support, and builds mode programming using these structures. `dml2_core_dcn4.c` fills `dml2_display_cfg_programming` from the calculation library, including DCHUB register pointers into `pipe_regs`. `dml21_wrapper.c` allocates and copies `dml2_display_cfg_programming`, while `dml21_utils.c` and `dml21_translation_helper.c` map its values into DC state, pipe programming, watermarks, and bandwidth context.

## State And Persistence Behavior
The type design favors fixed arrays and by-value copies. `dml2_display_cfg_programming` contains both pointer fields and their backing storage: callers should not access `pipe_regs` directly without respecting the per-plane pointer mapping, and copied programming structures must preserve pointer validity. The wrapper performs deep-enough copy repair for its use case by copying the aggregate, but any generic memcpy of `dml2_display_cfg_programming` can leave pointer fields referring to the original object unless adjusted. No on-disk persistence exists.

## Dependencies
The header depends on `dml_top_display_cfg_types.h`, `dml_top_soc_parameter_types.h`, `dml_top_policy_types.h`, `dml_top_dchub_registers.h`, and `dmub_cmd.h`. It also forward-declares `struct dml2_instance`. The FAMS2 fields couple this public API to DMUB command layouts, and the register output fields couple it to DCHUB/HUBP programming.

## Risks And Edge Cases
The fixed arrays assume plane and stream counts never exceed `DML2_MAX_PLANES`; SubVP phantom expansion can temporarily increase counts and must stay within the same bound. Pointer members inside output programming are a copy hazard. Mode-support booleans are numerous and can become inconsistent if only some are initialized on failure paths. `dml2_mcache_surface_allocation` uses arrays sized `DML2_MAX_MCACHES + 1`, with a documented sentinel/wrap element; consumers must understand the final boundary semantics. FAMS2 union members support multiple command versions, so callers must know which sub-state layout is valid.

## Test Signals
Good tests validate initialization and zeroing of `dml2_display_cfg_programming`, pointer mapping from `plane_programming[].pipe_regs[]` into `pipe_regs[]`, copy behavior in wrapper duplication paths, SubVP phantom stream/plane programming, MCache allocation boundaries and last-slice sharing, mode-support reason reporting, FAMS2 required/config output, and extraction of informative diagnostics for unsupported modes. ABI-sensitive builds should also catch accidental changes to DMUB-facing fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/inc/dml_top_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_core/dml2_core_dcn4.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_core/dml2_core_dcn4.c

## Purpose
`dml2_core_dcn4.c` implements the DCN4/DCN42 DML core adapter. It owns project-specific base IP capability tables, initializes the internal mode library from SoC/IP bounding boxes, invokes the generated DCN4 calculation engine for mode support and mode programming, expands implicit SubVP configurations into phantom streams/planes when needed, packs calculated results back into public `dml2_display_cfg_programming`, and exposes MCache allocation and informative diagnostics helpers.

## Important APIs, Types, And Functions
The file defines two base `struct dml2_core_ip_params` instances: `core_dcn4_ip_caps_base` and `core_dcn42_ip_caps_base`. They encode generation defaults such as buffer sizes, DPP/OTG/DSC/writeback counts, scaling limits, cursor buffer sizes, output counts, SubVP timing, MRQ/DCN42 metadata fields, and hostvm settings. `patch_ip_caps_with_explicit_ip_params()` maps explicit internal IP parameters back into public `dml2_ip_capabilities`, while `patch_ip_params_with_ip_caps()` maps public capabilities into internal IP parameters.

The exported functions are `core_dcn4_initialize()`, `core_dcn42_initialize()`, `core_dcn4_mode_support()`, `core_dcn4_mode_programming()`, `core_dcn4_populate_informative()`, and `core_dcn4_calculate_mcache_allocation()`. Static helpers include `create_phantom_stream_from_main_stream()`, `create_phantom_plane_from_main_plane()`, `expand_implict_subvp()`, `pack_mode_programming_params_with_implicit_subvp()`, and `lookup_uclk_dpm_index_by_freq()`.

## Control Flow
Initialization checks that a minimum clock table is supplied, selects either an explicit IP bounding box or the DCN4/DCN42 base table, patches between internal and public capability representations, forces `imall_supported` false on the non-explicit path, and copies `dml2_soc_bb` plus `dml2_ip_capabilities` into the internal mode library.

Mode support starts by expanding implicit SubVP if `display_config.overrides.enable_subvp_implicit_pmo` is set. Expansion copies the original display config, optionally disables unbounded requesting until stage 3 is performed, creates phantom streams from stage3 metadata, creates phantom planes for planes attached to SubVP streams, adjusts phantom viewport heights from scaler ratios, disables immediate flip/dynamic metadata/cursor/TDLUT on phantoms, and marks the main plane as a main SubVP pipe. The expanded config is passed to `dml2_core_calcs_mode_support_ex()`. On success, the wrapper copies global clocks, p-state support, bandwidth requirements, per-plane DPP clocks, ODM/DPP/DSC decisions, and stream support data from the internal calculation structures into `mode_support_result`.

Mode programming repeats implicit SubVP expansion, prepares `dml2_core_calcs_mode_programming_ex()` parameters, and looks up the UCLK DPM index by matching the selected active UCLK in the SoC clock table. If calculation succeeds and implicit SubVP is enabled, `pack_mode_programming_params_with_implicit_subvp()` copies the unexpanded display config to output, fills global arb/watermark/FAMS2 config, packs main stream and plane programming, assigns per-pipe register storage, copies stage2 MCache allocation, populates main and phantom pipe registers, assigns phantom MCache IDs after main IDs, and fills phantom global sync. Without implicit SubVP, the function follows a simpler loop over planes and DPP offsets, fills global registers, decides a p-state method from legacy SubVP overrides or latency/TWait comparisons, copies MCache allocation, and populates stream programming once per stream.

`core_dcn4_populate_informative()` selects a voltage-level index from the mode-programming path when supported or the mode-support path when unsupported, then calls `dml2_core_calcs_get_informative()`. `core_dcn4_calculate_mcache_allocation()` zeroes the output, asks the calculation library for allocation, patches the last X offset to the plane width for each active plane, clears dedicated-MALL requirement, and returns true.

## State And Persistence Behavior
The file mutates the `dml2_core_instance` internal mode library and scratch buffers. It does not persist data beyond the DML instance lifetime. Scratch mappings in `core->scratch` track SubVP main-to-phantom stream and plane indexes and are rebuilt by `expand_implict_subvp()`. Programming output contains pointers into its own `pipe_regs` array; the code assigns those pointers during packing. The code uses stage2 MCache allocations and stage3 SubVP/FAMS2 metadata from `display_configuation_with_meta`, so mode-programming correctness depends on earlier PMO/MCache stages having populated those fields.

## Dependencies And Integration Points
The implementation includes `dml2_internal_shared_types.h`, `dml2_core_shared_types.h`, `dml2_core_dcn4.h`, `dml2_core_dcn4_calcs.h`, `dml2_debug.h`, and `lib_float_math.h`. It is wired into `dml2_core_factory.c`, which selects DCN4 functions for `dml2_project_dcn40`, `dml2_project_dcn4x_stage2`, and `dml2_project_dcn4x_stage2_auto_drr_svp`, and DCN42 initialization for `dml2_project_dcn42`. It delegates most numeric DML work to generated/ported calculation helpers and exposes public results consumed by top SOC, wrapper, translation helper, DC pipe programming, and watermarks.

## Risks And Edge Cases
Both initialization functions set `subvp_fw_processing_delay_us` from `core_dcn4_ip_caps_base.subvp_pstate_allow_width_us` on the explicit-IP path, which looks suspicious because the field name differs from the assigned source. `expand_implict_subvp` misspelling is harmless but duplicated with similarly named helpers elsewhere, increasing maintenance risk. Phantom expansion increments `num_streams` and `num_planes` without local bounds checks against `DML2_MAX_PLANES`. `stream_already_populated_mask` uses bit shifts and assumes stream indexes fit the mask width. `lookup_uclk_dpm_index_by_freq()` returns 0 on no exact match, which can hide clock-table mismatch. The code copies explicit IP bounding boxes using a caller-provided size without checking it against `sizeof(struct dml2_core_ip_params)`. Programming uses `total_pipe_regs_copied` without a local guard against the fixed backing array size.

## Test Signals
High-value tests include initialization with and without explicit IP bounding boxes for DCN4 and DCN42, mode support with multiple planes per stream, ODM combine/split/MSO modes, DSC and output type/rate reporting, and bandwidth reporting. SubVP tests should verify phantom stream/plane creation, viewport height clamping, disabled phantom features, main-to-phantom mappings, FAMS2 config generation, phantom MCache ID offsetting, and pipe register assignment. Negative tests should cover missing minimum clock table, UCLK not found in the DPM table, maximum plane/stream expansion, unsupported modes with informative voltage-level selection, and copy safety of programming pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_core/dml2_core_dcn4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_core/dml2_core_dcn4.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_core/dml2_core_dcn4.h

## Purpose
`dml2_core_dcn4.h` declares the DCN4/DCN42 core implementation entry points used by the DML core factory. It is the narrow interface between project selection and the implementation in `dml2_core_dcn4.c`.

## Important APIs, Types, And Functions
The header declares `core_dcn4_initialize()`, `core_dcn42_initialize()`, `core_dcn4_mode_support()`, `core_dcn4_mode_programming()`, `core_dcn4_populate_informative()`, and `core_dcn4_calculate_mcache_allocation()`. All signatures use internal in/out structs declared elsewhere, including `dml2_core_initialize_in_out`, `dml2_core_mode_support_in_out`, `dml2_core_mode_programming_in_out`, `dml2_core_populate_informative_in_out`, and `dml2_calculate_mcache_allocation_in_out`.

## Control Flow And Integration
The header has no control flow. `dml2_core_factory.c` includes it and assigns these functions into a `dml2_core_instance` based on `dml2_project_id`. DCN40 and DCN4 stage2 projects use `core_dcn4_initialize`; DCN42 uses `core_dcn42_initialize`; all supported DCN4-family projects share the mode support, programming, informative, and MCache allocation functions.

## State And Persistence Behavior
No state is declared here. State is passed through the in/out structures and stored in the `dml2_core_instance` by the implementation. The functions return `bool` success/failure and mutate caller-provided objects.

## Dependencies
The header intentionally does not include the definitions for its parameter structs, so includers must include internal shared type headers before using the prototypes in a context that requires complete types. This keeps the header small but makes include ordering important.

## Risks And Edge Cases
Because the prototypes use structs that are not forward-declared in this header, standalone inclusion can produce compile errors unless prior includes supply declarations. The shared function set for DCN4 and DCN42 means implementation changes must preserve both projects' behavior. Any signature change requires updates in the factory and internal shared type declarations.

## Test Signals
Compile coverage through `dml2_core_factory.c` is the primary signal. Runtime tests should verify each supported `dml2_project_id` installs the expected initializer and shared operation callbacks, and that unsupported/invalid project IDs do not expose these functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_core/dml2_core_dcn4.h -->

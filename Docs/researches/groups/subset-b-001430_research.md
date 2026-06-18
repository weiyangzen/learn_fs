# subset-b-001430 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_pmo/dml2_pmo_dcn4_fams2.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_pmo/dml2_pmo_dcn4_fams2.c

### Purpose
`dml2_pmo_dcn4_fams2.c` implements the DCN4 FAMS2 power-management optimizer. It selects and applies display-mode mutations for DCC mcache admissibility, vmin, UCLK p-state switching, implicit SubVP/FAMS2, DRR variants, vblank reservation, and stutter residency.

### Important APIs, Types, And Functions
The exported PMO entry points are `pmo_dcn4_fams2_initialize()`, `pmo_dcn4_fams2_optimize_dcc_mcache()`, the vmin `init/test/optimize` trio, the p-state `init/test/optimize` trio, the stutter `init/test/optimize` trio, `pmo_dcn4_fams2_expand_base_pstate_strategies()`, `dcn4_get_vactive_pstate_margin()`, and `dcn4_get_minimum_reserved_time_us_for_planes()`. The main data contract is `struct dml2_pmo_instance`, especially its `init_data.pmo_dcn4` persistent expanded strategy lists and `scratch.pmo_dcn4` candidate, timing, and scheduling state. Key helpers expand p-state strategies, compute per-stream p-state metadata, build synchronized timing groups, validate cofunctionality, schedule timing groups, and write per-plane overrides for vactive, vblank, SVP, DRR, and mixed FAMS2 strategies.

### Control Flow
Initialization stores SoC/IP/options pointers, sets combine limits and FAMS2 refresh-rate policy, and expands base strategy lists for one to four streams. DCC mcache optimization copies the input display config when needed, counts used/free pipes, then increases MPC combine for non-ODM cases or ODM combine for supported single-stream cases. Vmin optimization first marks streams unoptimizable when dynamic ODM is disabled, MPC combine is already needed, SVP conflicts with policy, horizontal timing is not divisible, or the encoder is not DP-like; optimization then increases ODM on the highest ODM-load stream until a legal 2:1, 3:1, or 4:1 mode is found. P-state support builds stream plane masks, vactive capability, per-stream FAMS2 metadata, implicit SVP metadata, synchronized timing groups, and a candidate list; each candidate must satisfy forced plane overrides, DRR policy, vactive/vblank/DRR/SVP capability, and global schedulability. Optimization walks candidates and, when allowed, increments the latency clock-state index before moving to the next strategy. Stutter initialization derives candidate reserved-vblank times from z8 and normal stutter latencies, while stutter optimization writes the chosen reservation to every plane.

### State, Persistence, And Dependencies
The persistent state across optimization attempts is held in `pmo->init_data` and `pmo->scratch`; display changes are written into `struct display_configuation_with_meta` copies and the nested `dml2_display_cfg` plane/stream overrides. There is no file or firmware persistence here. Dependencies include `dml2_internal_shared_types.h` for PMO/top state, `dml2_debug.h` for assertions/logging, `lib_float_math.h` for deterministic arithmetic helpers, and DML2 display, timing, SoC, IP, mcache, and p-state enums from the core headers.

### Integration Points
`dml2_pmo_factory.c` installs these functions for DCN4 stage1, DCN42, and auto-DRR-SVP projects. `dml2_top_soc15.c` calls them during optimization phases after core mode-support validation and before DPMM/programming generation. Output fields such as `stage3.pstate_switch_modes`, `stage3.stream_svp_meta`, `stage3.stream_pstate_meta`, `stage3.fams2_required`, `stage4.unoptimizable_streams`, and plane/stream override fields are consumed by core programming and display-resource code.

### Risks
Several arrays are indexed by stream or plane count and assume the caller has already bounded those counts to `DML2_MAX_PLANES` and `PMO_DCN4_MAX_DISPLAYS`; `get_num_expanded_strategies()` uses `stream_count - 1`, so zero or oversized stream counts are unsafe. `all_timings_support_vblank()` compares a stream mask with `synchronized_timing_group_masks[i]`, where `i` is the first stream index, not necessarily the timing-group index, making synchronized-group indexing a subtle review point. `pmo_dcn4_fams2_optimize_dcc_mcache()` indexes `stream_descriptors[i]` while iterating planes in the ODM branch, which is only safe when plane and stream indexes coincide. Candidate list capacity is finite, so strategy expansion can silently stop once `DML2_PMO_PSTATE_CANDIDATE_LIST_SIZE` is reached. Stutter candidate advancement is fragile because `cur_stutter_candidate` is initialized but not incremented in this file.

### Test Signals
High-value tests include one to four stream strategy expansion, forced per-plane p-state overrides, DRR active fixed and variable policies, vblank-synchronized and unsynchronized timings, SubVP rejection cases, DP versus HDMI dynamic ODM gating, horizontal timing divisibility for ODM 3:1/4:1, DCC mcache failures with and without free pipes, and optimization loops where the last candidate fails mode support and should increase latency index.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_pmo/dml2_pmo_dcn4_fams2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_pmo/dml2_pmo_dcn4_fams2.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_pmo/dml2_pmo_dcn4_fams2.h

### Purpose
This header declares the DCN4 FAMS2 PMO interface implemented by `dml2_pmo_dcn4_fams2.c`.

### Important APIs, Types, And Functions
It forward-declares `struct display_configuation_with_meta` and exposes helper queries for vactive p-state margin and reserved vblank time. It declares initialization, DCC mcache optimization, vmin optimization, p-state optimization, stutter optimization, and base-strategy expansion functions using the `dml2_pmo_*_in_out` structs from `dml2_internal_shared_types.h`.

### Control Flow
The header itself has no runtime flow. Its declarations define the callable lifecycle used by the PMO factory and top-level optimization pipeline: create an instance, initialize it, then call `init`, `test`, and `optimize` functions for each optimization family.

### State, Persistence, And Dependencies
There is no local state. The file depends on `dml2_internal_shared_types.h` for PMO parameter structs and strategy types. All persistent optimizer data lives in `struct dml2_pmo_instance`.

### Integration Points
`dml2_pmo_factory.c` includes this header to assign function pointers. `dml2_top_soc15.c` reaches the functions indirectly through `struct dml2_pmo_instance`.

### Risks
The header exposes the misspelled type name `display_configuation_with_meta`, so downstream code is coupled to that spelling. Function declarations do not encode stream/plane count bounds, leaving those invariants to callers and implementation assertions.

### Test Signals
Build coverage should ensure the factory can include this header for all supported DCN4 project IDs and that every declared symbol is defined when the DCN4 FAMS2 object is linked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_pmo/dml2_pmo_dcn4_fams2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_pmo/dml2_pmo_factory.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_pmo/dml2_pmo_factory.c

### Purpose
`dml2_pmo_factory.c` constructs a `dml2_pmo_instance` by selecting PMO implementation callbacks for a DML2 project ID.

### Important APIs, Types, And Functions
The exported API is `dml2_pmo_create()`. It installs DCN3 callbacks, DCN4 FAMS2 callbacks, or dummy stutter callbacks depending on `enum dml2_project_id`. The dummy stutter functions are local placeholders used for DCN3-backed projects.

### Control Flow
The factory rejects a null output pointer, zeroes the instance, then switches on `project_id`. `dml2_project_dcn4x_stage1` gets DCN4 initialize and DCC mcache optimization only. `dml2_project_dcn40` and `dml2_project_dcn4x_stage2` get DCN3 PMO callbacks plus dummy stutter hooks. `dml2_project_dcn42` and `dml2_project_dcn4x_stage2_auto_drr_svp` get the full DCN4 FAMS2 callback set. Invalid or unknown projects return false.

### State, Persistence, And Dependencies
The only state change is the zeroed and populated `struct dml2_pmo_instance` provided by the caller. Dependencies include the DCN3 PMO implementation, DCN4 FAMS2 PMO implementation, `dml2_external_lib_deps.h` for memory helpers, and shared PMO types.

### Integration Points
`dml2_top_soc15_initialize_instance()` calls this after MCG, DPMM, and core creation. The top optimization phases later invoke callbacks through the populated `dml2_pmo_instance`.

### Risks
The stage1 DCN4 case leaves vmin, p-state, and stutter callbacks unset, so top code must only call features valid for that project or guard null pointers. Dummy stutter behavior returns `init=false`, `test=true`, and `optimize=false`, which makes stutter a no-op but can hide accidental use unless tests assert project-specific behavior.

### Test Signals
Tests should instantiate every project ID and verify the expected callback table, null-output rejection, invalid-project rejection, and that unsupported optimization phases are either not called or gracefully skipped by top-layer orchestration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_pmo/dml2_pmo_factory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_pmo/dml2_pmo_factory.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_pmo/dml2_pmo_factory.h

### Purpose
This header declares the PMO factory entry point.

### Important APIs, Types, And Functions
It includes shared PMO types and top project enums, then declares `bool dml2_pmo_create(enum dml2_project_id project_id, struct dml2_pmo_instance *out)`.

### Control Flow
There is no runtime flow in the header. It establishes the creation contract used by top-level DML2 initialization.

### State, Persistence, And Dependencies
There is no local state. The output instance supplied to `dml2_pmo_create()` receives function pointers and persistent PMO state storage.

### Integration Points
Included by PMO implementations and by the SOC15 top initializer. It is the narrow boundary between project selection and concrete optimizer implementations.

### Risks
Because the factory only returns a boolean, callers must inspect or trust callback population per project. The header does not document which callbacks are mandatory for each project.

### Test Signals
Compile and initialization tests should validate all supported project IDs and confirm the top initializer rejects projects for which the factory returns false.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_pmo/dml2_pmo_factory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_standalone_libraries/lib_float_math.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_standalone_libraries/lib_float_math.c

### Purpose
`lib_float_math.c` provides small deterministic math helpers used by DML2 standalone and kernel-integrated display calculations.

### Important APIs, Types, And Functions
It implements `math_mod`, `math_min2`, `math_max2`, `math_floor2`, `math_floor`, `math_ceil`, `math_ceil2`, `math_max3`, `math_max4`, `math_max5`, `math_pow`, `math_fabs`, `math_log`, `math_log2`, `math_log2_approx`, and `math_round`. A local `isNaN` macro gives NaN-tolerant min/max/mod behavior.

### Control Flow
Most helpers are direct arithmetic wrappers. Min/max return the non-NaN operand when exactly one input is NaN. Floor/ceil use integer casts and a `0.99999` bias rather than libc. `math_pow` iteratively multiplies for positive integer-like exponents, reciprocates for negative exponents, and returns `1.0` for exponent zero. `math_log` uses repeated division to approximate logarithms for the narrow DML use case, and `math_log2_approx` counts right shifts.

### State, Persistence, And Dependencies
The file has no mutable state and no external persistence. It intentionally avoids full libc math dependencies and includes only `lib_float_math.h`.

### Integration Points
PMO and top SOC15 code call these helpers for timing, bandwidth, scheduling, and mcache computations where DML code wants reproducible simple arithmetic across build environments.

### Risks
These are not general-purpose IEEE math replacements. Negative non-integer floors, fractional exponents, logarithm precision, divide-by-zero handling, and overflow behavior should be treated as constrained by DML inputs. The empty `ASSERT` macro means `math_floor2()` does not enforce nonzero significance in production.

### Test Signals
Tests should cover NaN min/max/mod behavior, positive and negative exponent cases that DML uses, ceil/floor boundary values, log2 approximation powers of two and off-by-one values, and divide/significance inputs expected from display timing formulas.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_standalone_libraries/lib_float_math.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_standalone_libraries/lib_float_math.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_standalone_libraries/lib_float_math.h

### Purpose
This header exposes the standalone float/double math helper API used by DML2 calculations.

### Important APIs, Types, And Functions
It declares modulo, min/max, floor/ceil, max-of-N, power, absolute value, logarithm, approximate log2, and round helpers.

### Control Flow
The header has no runtime flow. Its declarations allow DML2 code to use the local helper implementation instead of depending directly on platform math libraries.

### State, Persistence, And Dependencies
There is no state and no includes beyond the include guard. Implementations are in `lib_float_math.c`.

### Integration Points
Included by DCN4 FAMS2 PMO and SOC15 top mcache/scheduling code.

### Risks
The names resemble standard math functions but semantics differ from libc in precision and edge cases, so new callers should confirm inputs match the restricted behavior.

### Test Signals
Build tests should verify all declared functions are linked, and unit tests should pin edge-case semantics before using these helpers in new formulas.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_standalone_libraries/lib_float_math.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_top/dml2_top_interfaces.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_top/dml2_top_interfaces.c

### Purpose
`dml2_top_interfaces.c` is the public top-level dispatch layer for DML2. It exposes instance sizing, initialization, mode support, mode programming, and mcache programming entry points.

### Important APIs, Types, And Functions
The file defines `dml2_get_instance_size_bytes()`, `dml2_initialize_instance()`, `dml2_check_mode_supported()`, `dml2_build_mode_programming()`, and `dml2_build_mcache_programming()`.

### Control Flow
Initialization switches on `options.project_id` and routes supported DCN4/DCN40/DCN42 projects to `dml2_top_soc15_initialize_instance()`. The other top-level APIs validate that the corresponding function pointer is installed in `in_out->dml2_instance->funcs` and then dispatch to the SOC15 implementation.

### State, Persistence, And Dependencies
This file holds no state. State belongs to the caller-provided `struct dml2_instance`, whose size is returned by `dml2_get_instance_size_bytes()` and whose `funcs` table is filled by the initializer. Dependencies are `dml_top.h`, `dml2_internal_shared_types.h`, and the SOC15 top header.

### Integration Points
This is the ABI-style entry used by wrappers and callers that do not know the project-specific implementation. It bridges external top interfaces to `dml2_top_soc15.c`.

### Risks
The dispatch functions assume non-null `in_out` and `in_out->dml2_instance`; only missing function pointers are guarded. Unsupported project IDs return false at initialization, so callers must check initialization before using the instance.

### Test Signals
Tests should validate instance-size allocation, initialization for each supported project ID, invalid project rejection, and null callback rejection for manually corrupted instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_top/dml2_top_interfaces.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_top/dml2_top_legacy.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_top/dml2_top_legacy.c

### Purpose
`dml2_top_legacy.c` is currently a stub translation unit for the legacy top implementation.

### Important APIs, Types, And Functions
It includes `dml2_top_legacy.h`, the core and PMO factories, and legacy display mode core structs, but defines no functions.

### Control Flow
There is no runtime flow in this file.

### State, Persistence, And Dependencies
There is no state. The includes indicate intended dependencies on legacy core and PMO creation and legacy display-mode structures.

### Integration Points
The companion header declares `dml2_top_legacy_initialize_instance()`, but this source file does not define it. Current top dispatch in this subset routes supported projects to SOC15 instead.

### Risks
If a build target expects `dml2_top_legacy_initialize_instance()`, this source file will not satisfy the symbol. The file may be a placeholder for removed or future legacy support, so stale includes should be watched for build churn.

### Test Signals
Build/link tests should confirm no active configuration requires the legacy initializer from this file, or else add/restore the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_top/dml2_top_legacy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_top/dml2_top_legacy.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_top/dml2_top_legacy.h

### Purpose
This header declares the legacy top initializer.

### Important APIs, Types, And Functions
It includes `dml2_internal_shared_types.h` and declares `bool dml2_top_legacy_initialize_instance(struct dml2_initialize_instance_in_out *in_out)`.

### Control Flow
There is no runtime flow in the header.

### State, Persistence, And Dependencies
There is no local state. Any implementation would populate `struct dml2_instance` through the shared initialization parameter.

### Integration Points
It is included by the legacy source stub. The current public top interface in this subset does not dispatch to this initializer.

### Risks
The declaration can become a dangling API if no object defines it. If reintroduced, it must match the SOC15 initializer contract for function-table population and component creation.

### Test Signals
Compile/link coverage should determine whether any configuration references the legacy initializer and should fail loudly if the declaration is used without an implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_top/dml2_top_legacy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_top/dml2_top_soc15.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_top/dml2_top_soc15.c

### Purpose
`dml2_top_soc15.c` is the SOC15 top-level DML2 implementation. It creates component instances, runs mode support and optimization phases, validates and programs DCC mcache, maps DPM/watermarks, and delegates final programming to the core.

### Important APIs, Types, And Functions
Exported functions are `dml2_top_soc15_initialize_instance()`, `dml2_top_mcache_calc_mcache_count_and_offsets()`, `dml2_top_mcache_assign_global_mcache_ids()`, `dml2_top_mcache_validate_admissability()`, and `dml2_top_soc15_build_mcache_programming()`. Static top callbacks implement check-mode and build-mode programming. Optimization is driven by `dml2_top_optimization_perform_optimization_phase()` and the binary-search-like phase 1 helper for minimum latency clocks. Mcache helpers include splitting, shift search, span counting, scaling-transform viewport splitting, allocation reset, and register generation.

### Control Flow
Initialization zeroes the instance, copies IP and SoC bounding boxes, creates MCG, DPMM, core, and PMO components, builds the minimum clock table, initializes the core and PMO, and installs `soc15_funcs`. `check_mode_supported()` runs unoptimized core mode support, attempts mcache optimization/validation, maps DPM requirements, and reports support through `in_out->is_supported`. `build_mode_programming()` first tries a speculative lowest-clock mode, falls back to unoptimized mode support and phase 1 latency-clock search, then runs mcache, UCLK p-state, vmin, and stutter phases in order. It finally maps DPM, asks core for mode programming, maps watermarks, and populates informative output. Mcache validation computes per-plane cache requirements, assigns global IDs, checks whether each pipe viewport spans at most two slices, searches for valid cache-boundary shifts when needed, and records per-plane status.

### State, Persistence, And Dependencies
All working state lives inside `dml->scratch` locals or the caller-provided `dml2_display_cfg_programming`. The instance persists component function tables, SoC/IP data, minimum clock table, PMO options, and component scratch. Dependencies include the MCG, DPMM, core, and PMO factories, `lib_float_math.h`, `dml2_debug.h`, and shared DML2 top/core/PMO/mcache types.

### Integration Points
This file is reached from `dml2_top_interfaces.c` for supported projects. It calls PMO callbacks installed by `dml2_pmo_factory.c`, core callbacks installed by `dml2_core_factory.c`, DPMM callbacks, and MCG callbacks. Mcache programming output is consumed by DC hubp programming paths through `dml2_build_mcache_programming_in_out`.

### Risks
The stutter init wrapper fills `l->uclk_pstate.init_params` but then calls `init_for_stutter(&l->stutter.stutter_params)` without assigning that stutter parameter's instance/base fields, which looks like a real initialization bug. `calculate_h_split_for_scaling_transform()` never sets `success = true` for supported scaling transforms, so callers ignore the return value today but future users could misread it. `dml2_top_soc15_build_mcache_programming()` zeroes a pointer table using `DML2_MAX_PLANES * DML2_MAX_DCN_PIPES * sizeof(struct dml2_hubp_pipe_mcache_regs *)`; this is correct only if the destination has exactly that flattened shape. Mcache ID assignment assumes enough global mcache ID slots and uses pseudo-last wraparound entries, so allocation bounds are important.

### Test Signals
Tests should cover initialization failure at each factory/build step, speculative mode success and fallback path, mcache validation pass/fail with DCC on both planes, shift-granularity search, SubVP and DRR p-state programming propagation, vmin partial-success copying, stutter optimization parameter wiring, DPMM failure flags, and generated mcache register IDs/split locations for one- and two-slice viewports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_top/dml2_top_soc15.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_top/dml2_top_soc15.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_top/dml2_top_soc15.h

### Purpose
This header declares the SOC15 top implementation and mcache helper APIs.

### Important APIs, Types, And Functions
It exposes `dml2_top_soc15_initialize_instance()`, mcache count/offset calculation, global mcache ID assignment, admissibility validation, and mcache programming construction.

### Control Flow
There is no runtime flow in the header. The declarations correspond to initialization, mode optimization support, and final hubp mcache programming stages.

### State, Persistence, And Dependencies
There is no local state. The functions operate on `struct dml2_instance` and parameter structs defined in `dml2_internal_shared_types.h`.

### Integration Points
Included by top interface dispatch and potentially by wrapper/resource code that needs direct mcache helper access.

### Risks
The API exposes low-level mcache helpers that mutate allocation arrays in place, so callers need clear ownership of the parameter storage. The misspelled `admissability` spelling is part of the symbol name.

### Test Signals
Build tests should verify all declarations are defined and callable in SOC15 builds; integration tests should exercise the direct mcache helper path used by mode support and programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_top/dml2_top_soc15.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/inc/dml2_debug.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/inc/dml2_debug.h

### Purpose
`dml2_debug.h` defines logging and assertion macros for DML2.

### Important APIs, Types, And Functions
It maps `DML_ASSERT` to `ASSERT`, sets a default warning log level, maps logging to `dm_output_to_console`, defines fatal/error/warn/info/debug/verbose log macros, and provides scalar and array logging helpers for booleans, integers, unsigned integers, doubles, and 1D/2D/3D arrays.

### Control Flow
Preprocessor log-level checks compile logging macros either to console output blocks or to `((void)0)`. Error-level builds enable `DML_ASSERT_MSG()` to log function and line context before asserting. Debug-level builds add XML-like function/component/top-interface entry and exit markers and field dump helpers.

### State, Persistence, And Dependencies
There is no runtime state. Output goes to the console/log sink selected by `dm_output_to_console`. The file depends on `os_types.h` for `ASSERT` and console output support.

### Integration Points
Included by PMO and top files to report verbose mcache and optimization diagnostics and to enforce DML invariants.

### Risks
Macros evaluate fields multiple times in some array/log contexts and should not be passed expressions with side effects. Disabled log levels remove assertions from `DML_ASSERT_MSG()` entirely below error level. The format helper macros require type-compatible fields.

### Test Signals
Compile tests with several `DML_LOG_LEVEL` values should confirm macros compile away or emit as expected. Runtime smoke tests can verify error logging and debug array formatting without changing calculation results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/inc/dml2_debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/inc/dml2_internal_shared_types.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/inc/dml2_internal_shared_types.h

### Purpose
`dml2_internal_shared_types.h` is the central internal contract for DML2. It defines shared data structures and function-pointer interfaces for clock generation, DPM mapping, core mode support/programming, PMO optimization, mcache handling, top-level optimization phases, and the `dml2_instance`.

### Important APIs, Types, And Functions
Major type groups are MCG clock tables and `dml2_mcg_instance`; DPMM map-mode/map-watermark parameter structs and `dml2_dpmm_instance`; core initialization, mode support, mode programming, informative population, mcache allocation, core scratch, and `dml2_core_instance`; optimization-stage state in `display_configuation_with_meta`; PMO parameter structs, strategy masks, PMO scratch/init data, and `dml2_pmo_instance`; top mcache parameter structs; optimization-phase locals and function parameter structs; top callback table `dml2_top_funcs`; and the aggregate `dml2_instance`.

### Control Flow
The header has no executable flow, but its types encode the pipeline: MCG builds a minimum clock table, core checks mode support and produces support info, top optimization phases mutate `display_configuation_with_meta` stage state, PMO callbacks test and optimize targeted power features, DPMM maps mode requirements to SoC DPM states and watermarks, core emits programming, and top callbacks expose the final operations.

### State, Persistence, And Dependencies
All DML2 instance persistence is described here. Long-lived state includes component instances, SoC/IP bounding boxes, minimum clock tables, PMO options, component function tables, and scratch spaces. Per-mode state persists through `display_configuation_with_meta` stages 1 through 5 while optimization proceeds. Dependencies include external library deps, top public types, and core shared types.

### Integration Points
Almost every file in this subset includes this header directly or indirectly. It is the type bridge among factories, SOC15 top, DCN4 FAMS2 PMO, DPMM, MCG, core, and mcache programming code.

### Risks
This header is large and tightly coupled; changing a field can affect many phases. Fixed-size arrays rely on `DML2_MAX_PLANES`, `DML2_MAX_DCN_PIPES`, and PMO constants, so bounds validation belongs at API edges. The misspelled `display_configuation_with_meta` type is pervasive. Some unions reuse scratch memory among phases, so functions must not retain pointers into phase-local union members beyond the call.

### Test Signals
ABI/build tests should cover all component factories against these structs. Behavioral tests should validate stage transitions, scratch reuse, PMO callback tables, mcache parameter mutation, and top function dispatch for each supported project ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/inc/dml2_internal_shared_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_dc_resource_mgmt.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_dc_resource_mgmt.c

### Purpose
`dml2_dc_resource_mgmt.c` maps DML2 display-configuration pipe requirements onto DC `pipe_ctx` topology. It creates or updates ODM and MPC combine trees, preserves preferred existing pipe choices when possible, supports DML2.0 and DML2.1 result formats, and rebuilds scaling/test-pattern state after mapping.

### Important APIs, Types, And Functions
The exported API is `dml2_map_dc_pipes()`. Internal structures are `dc_plane_pipe_pool` and `dc_pipe_mapping_scratch`. Important helpers compute plane IDs, find display-config indexes by stream or plane ID, locate master stream/plane pipes, gather assigned pipes, find preferred and last-resort candidates, allocate free pipes, sort pipe groups, calculate ODM slices, build ODM and blend trees, free unused pipes, derive source/target ODM/MPC factors, and choose either callback-driven or legacy direct mapping.

### Control Flow
If `ctx->config.map_dc_pipes_with_callbacks` is set, the file populates source and target ODM/MPC factors, first unmaps streams or planes that need fewer slices, then maps those that need more slices through DC callbacks. Otherwise it uses the legacy mapper. The legacy path converts DML2.1 programming outputs or DML2.0 `disp_cfg->hw` arrays into ODM and DPP-per-surface arrays, then iterates streams. For each stream it computes the target ODM factor and slice boundaries; blank streams still get ODM pipe mapping. For each plane it computes plane ID, target MPC factor, assigns/reuses enough pipes, sorts them, links bottom/top blend trees and prev/next ODM chains, calls `acquire_secondary_pipe_for_mpc_odm()`, frees unused plane pipes, then rebuilds scaling and test pattern parameters.

### State, Persistence, And Dependencies
The function mutates the caller's `dc_state->res_ctx.pipe_ctx` graph in memory. It uses `ctx->v20.scratch.dml_to_dc_pipe_mapping` or the supplied mapping to translate between DML and DC identifiers, and `ctx->pipe_combine_scratch` for callback mapping. Dependencies include DC resource/core types, DML wrapper/internal types, `dml2_utils.h`, `dml2_mall_phantom.h`, and many callback hooks in `ctx->config.callbacks` and `ctx->config.svp_pstate.callbacks`.

### Integration Points
This is the bridge from DML-calculated ODM/DPP requirements to actual DC hardware resource topology. It consumes DML2.0 `dml_display_cfg_st` or DML2.1 `mode_programming.programming`, handles SubVP phantom-to-main stream mapping, and calls DC resource callbacks for pipe acquisition, slice-count updates, scaling params, and test pattern params.

### Risks
The direct mapper relies heavily on preexisting master pipes and asserts rather than returning failures in many bad states. `remove_pipes_from_blend_trees()` assigns `pipe->bottom_pipe = pipe->top_pipe` when updating the lower neighbor, which is suspicious because it does not write through `pipe->bottom_pipe->top_pipe`. The mcache/pipe arrays are fixed-size and assume pipe counts never exceed `MAX_PIPES`. Plane duplicate handling depends on `dml_pipe_idx_to_plane_index` being valid. `validate_pipe_assignment()` is effectively stubbed, so final topology correctness depends on external callbacks and later hardware programming paths.

### Test Signals
Tests should cover DML2.0 and DML2.1 mappings, callback and legacy paths, ODM increase/decrease, MPC increase/decrease, stereo forced two-way split, SubVP phantom stream mapping, blank stream ODM setup, preserving preferred existing pipes, avoiding last-resort OTG/OPP-change pipes until needed, duplicate plane IDs, and topology validation of top/bottom and prev/next ODM links after mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_dc_resource_mgmt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_dc_resource_mgmt.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_dc_resource_mgmt.h

### Purpose
This header declares the DML2-to-DC pipe mapping API.

### Important APIs, Types, And Functions
It forward-declares `dml2_context`, `dml2_dml_to_dc_pipe_mapping`, and `dml_display_cfg_st`, includes DC wrapper types, and declares `dml2_map_dc_pipes()`.

### Control Flow
There is no runtime flow in the header. The comment documents that the implementation creates pipe linkage in `dc_state` from DML-calculated ODM and DPP-per-surface outputs.

### State, Persistence, And Dependencies
The header itself has no state. The declared function mutates `dc_state` and uses mapping/context state.

### Integration Points
Included by resource-management callers that need to convert DML outputs into DC pipe topology. It is shared by DML2.0 and DML2.1 wrapper flows.

### Risks
The API returns only a boolean even though much of the implementation asserts on invalid topology. Callers must pass a valid mapping covering all active stream and plane IDs.

### Test Signals
Compile tests should verify callers can include this header with DC types. Integration tests should assert `dc_state` topology after a successful `dml2_map_dc_pipes()` call.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_dc_resource_mgmt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_dc_types.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_dc_types.h

### Purpose
`dml2_dc_types.h` is a wrapper header for DC-owned types used by DML2.

### Important APIs, Types, And Functions
It does not define functions. It includes `resource.h`, `core_types.h`, `dsc.h`, `clk_mgr.h`, and `dc_state_priv.h`, which provide `dc_state`, `pipe_ctx`, stream/plane state, resource, DSC, and clock-manager types.

### Control Flow
There is no runtime flow.

### State, Persistence, And Dependencies
There is no state in the wrapper. It centralizes external DC type dependencies so DML2 code can include one header.

### Integration Points
`dml2_internal_types.h` and `dml2_dc_resource_mgmt.h` include this file before using DC resource types. The comment notes that standalone builds may provide these types differently.

### Risks
This wrapper ties DML2 compilation to private DC headers such as `dc_state_priv.h`. Changes in DC type definitions can ripple through DML2 even when DML2 source does not change.

### Test Signals
Build tests in both DC-integrated and standalone/unit-test configurations should verify this wrapper resolves the same required type names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_dc_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_internal_types.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_internal_types.h

### Purpose
`dml2_internal_types.h` defines wrapper-side DML2 context, scratch, mapping, and architecture types used by DC integration code.

### Important APIs, Types, And Functions
Key structs include `dml2_wrapper_optimize_configuration_params`, scratch structs for lowest-state and RQ/DLG calculations, `dml2_dml_to_dc_pipe_mapping`, `dml2_wrapper_scratch`, `dml2_helper_det_policy_scratch`, `dml21_wrapper_scratch`, `dml2_pipe_combine_factor`, `dml2_pipe_combine_scratch`, and the aggregate `dml2_context`. It also defines `__DML2_WRAPPER_MAX_STREAMS_PLANES__` and `enum dml2_architecture`.

### Control Flow
There is no executable flow. The structures describe how wrapper code carries current/new display configs, policies, mode-support data, flexible pipe mapping state, plane duplicate tracking, HPO encoder mapping, DML2.0 state, and DML2.1 top-interface state.

### State, Persistence, And Dependencies
`struct dml2_context` persists architecture selection, configuration callbacks/options, DET helper scratch, pipe-combine scratch, and a union of DML2.0 and DML2.1 state. Dependencies include DC types, legacy display mode core, wrapper and policy headers, DML2.1 top interfaces, and public DML top types.

### Integration Points
`dml2_dc_resource_mgmt.c` uses these types to choose DML2.0 versus DML2.1 mapping behavior, to access mapping arrays, to detect plane duplicates, and to store source/target pipe combine factors.

### Risks
The mapping arrays are limited to six stream/plane entries, so larger configurations need validation before use. The union means DML2.0 and DML2.1 state cannot be live simultaneously in one context. Mapping validity booleans must be maintained consistently; lookup helpers assert and return sentinel indexes when entries are missing.

### Test Signals
Tests should cover mapping-table population for streams, planes, DML pipe indexes, duplicate planes, DML2.0 and DML2.1 architecture selection, and pipe-combine scratch reset between mapping operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_internal_types.h -->

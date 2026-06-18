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

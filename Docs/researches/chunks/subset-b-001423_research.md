# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/display_mode_core.c lines 9970-10362

## Scope And Purpose

This chunk is the public-facing tail of the DML2.0 display-mode core implementation. It sits after the large internal mode-support and mode-programming formula paths and exposes their results to the rest of the AMD display driver. The code covered here has three main purposes:

- Finish `dml_core_get_row_heights()`, a minimal helper for computing DPTE and META row heights from source format, tiling, scan direction, pitch, GPUVM page size, and the DML IP buffer limits.
- Prepare and invoke the core mode-support and mode-programming passes through `dml_mode_support()`, `dml_mode_programming()`, and `dml_mode_support_ex()`.
- Define many small getter functions that export calculated watermarks, clock requirements, DLG timing values, VM/PTE/meta request timing, DET sizing, MALL sizing, DCC block information, and related per-surface values from `mode_lib->ms` and `mode_lib->mp`.

The chunk is therefore a boundary layer: the heavy math is performed by earlier functions such as `dml_core_mode_support()`, `dml_core_mode_support_partial()`, `dml_core_mode_programming()`, `CalculateBytePerPixelAndBlockSizes()`, and `CalculateVMAndRowBytes()`, while this code initializes the persistent calculation state and provides typed accessors for downstream DC programming code.

## Important APIs, Types, And Functions

`dml_core_get_row_heights()` is declared in `display_mode_core.h` and implemented just before and within this chunk. The covered portion selects luma or chroma parameters based on `is_plane1`, chooses the matching `dpte_buffer_size_in_pte_reqs_luma` or `dpte_buffer_size_in_pte_reqs_chroma` from `mode_lib->ip`, and calls `CalculateVMAndRowBytes()` with a reduced synthetic configuration. It asks that lower helper to compute only the DPTE and META row heights, sending all other outputs to a local `dummy_integer[16]` array.

`dml_get_soc_state_bounding_box()` is a static state-table accessor. It validates `state_idx` against `states->num_states`, asserts on out-of-range input, and returns `states->state_array[state_idx]` by value. This guards the setup path for every public support/programming call in this chunk.

`cache_ip_soc_cfg()` copies caller-visible DML inputs into `mode_lib->ms`, the mode-support working/persistent struct. It records the selected state index, maximum state index, SOC bounding box, IP parameters, policy, selected state bounding box, and maximum state bounding box.

`cache_display_cfg()` copies the whole `struct dml_display_cfg_st` into `mode_lib->ms.cache_display_cfg`. This cached copy is what the core calculations and getters use after the public entry point returns.

`fetch_socbb_params()` initializes the active clocks in `mode_lib->ms` from the selected SOC state: `SOCCLK`, `DRAMSpeed`, `FabricClock`, and `DCFCLK`. Later mode-support logic can replace some of these, especially when a minimum required DCFCLK policy is used.

`dml_mode_support()` is the single-state support entry point. It refreshes the cached IP/SOC/policy/display configuration, fetches state clocks, calls `dml_core_mode_support(mode_lib)`, and returns the boolean support result. The detailed evaluation data remains in `mode_lib->ms.support`.

`dml_mode_programming()` is the programming-value entry point. It builds a local `struct dml_clk_cfg_st` with `dml_use_required_freq` for DCFCLK, DISPCLK, and every DPPCLK entry, refreshes the same cached state/configuration, optionally runs `dml_core_mode_support_partial()` for standalone use, then calls `dml_core_mode_programming(mode_lib, &clk_cfg)`. It returns `mode_lib->mp.PrefetchAndImmediateFlipSupported`, so callers treat failure as inability to produce a valid programming set for the selected configuration.

`mode_support_pwr_states()` is a private search helper used by `dml_mode_support_ex()`. It scans a closed state-index range from `start_state_idx` to `end_state_idx`, calling `dml_mode_support()` for each state until one succeeds, and writes the first passing index to `*lowest_state_idx`.

`dml_mode_support_ex()` packages the multi-state search for wrapper code. It reads a `struct dml_mode_support_ex_params_st`, searches from `in_start_state_idx` through the highest available state, and on success copies `mode_lib->ms.support` to `*out_evaluation_info`.

`dml_get_is_phantom_pipe()` maps a pipe index to a plane index through `mode_lib->mp.pipe_plane[pipe_idx]` and checks whether that plane's cached `UseMALLForPStateChange` mode is `dml_use_mall_pstate_change_phantom_pipe`.

The two local getter macros define most of the exported API surface:

- `dml_get_var_func(name, type, expr)` creates whole-mode getters such as `dml_get_wm_urgent()`, `dml_get_return_bw()`, and `dml_get_total_immediate_flip_bytes()`.
- `dml_get_per_surface_var_func(name, type, array)` creates per-surface getters. Despite the parameter name `surface_idx`, the implementation treats the incoming index as a DML pipe index, maps it through `mode_lib->mp.pipe_plane[surface_idx]`, and returns the corresponding plane-array value.

The generated getters in this chunk fall into several groups:

- Watermark and latency getters: urgent, stutter, Z8 stutter, DRAM clock change, FCLK change, USR retraining, writeback urgent, writeback DRAM clock change, urgent latency, urgent extra latency, and max active FCLK/DRAM clock-change latency.
- Clock and bandwidth getters: DCFCLK deep sleep, calculated DISPCLK, calculated DPPCLK/DSCCLK, total data read bandwidth, return bandwidth, return DRAM bandwidth, and `TCalc`.
- Buffer and chunk getters: compressed buffer size, pixel/alpha/meta chunk sizes, minimum pixel/meta chunk bytes, DET buffer sizes, DPTE group size, VM group size, total immediate-flip bytes, PTE buffer mode, and BIGK fragment size.
- Prefetch/DLG timing getters: VStartup, VUpdate/VReady offsets, prefetch ratios, destination lines for VM/row requests in vblank and immediate flip, line/request delivery times, cursor request delivery times, metadata chunk times, and PTE-group times.
- Surface-geometry and compression getters: swath heights, DPTE/META row heights, DST after scaler, MALL static-screen use, MALL surface size, and DCC max/independent block values for luma and chroma.

## Control Flow

The first covered block is inside `dml_core_get_row_heights()`. The function has already declared luma/chroma byte, block, and macro-tile locals before line 9970. In this chunk it:

1. Calls `CalculateBytePerPixelAndBlockSizes()` using `SourcePixelFormat` and `SurfaceTiling`.
2. Selects the luma or chroma byte/block/macro-tile values based on `is_plane1`.
3. Selects the luma or chroma DPTE buffer request limit from `mode_lib->ip`.
4. Calls `CalculateVMAndRowBytes()` with enough fixed inputs to force the VM/PTE/META row-height calculations: viewport is treated as non-stationary, DCC is enabled, one DPP is used, GPUVM is enabled, max page-table levels is hardcoded as four, swath width and viewport dimensions are zero, and `pitch`/`GPUVMMinPageSizeKBytes` are caller-provided.
5. Captures only `*dpte_row_height` and `*meta_row_height`; every other output is intentionally discarded into `dummy_integer`.

The support/programming entry points follow a repeated setup pattern. `dml_mode_support()` and `dml_mode_programming()` both call `cache_ip_soc_cfg()`, `cache_display_cfg()`, and `fetch_socbb_params()` before invoking core calculation. This means every public pass resets `mode_lib->ms` to match the selected state, current top-level bounding boxes, policy, and display configuration before formula code runs.

`dml_mode_programming()` has an extra standalone branch. When `call_standalone` is true, it pre-seeds `mode_lib->ms.support.ImmediateFlipSupport` to true and runs `dml_core_mode_support_partial()`. This provides the subset of support fields required by programming when the caller did not first run a complete support check. After that, all programming outputs are computed by `dml_core_mode_programming()` into `mode_lib->mp`.

`mode_support_pwr_states()` validates the requested search range with assertions, initializes the output lowest state to `end_state_idx`, then scans upward. The first state for which `dml_mode_support()` returns true becomes the selected lowest supported state. If none pass, the function returns false and leaves `*lowest_state_idx` at the end-state default.

`dml_mode_support_ex()` uses that helper to implement the usual "find the lowest supporting voltage/SOC state" flow. On success, it copies the populated `mode_lib->ms.support` summary into the caller-provided `out_evaluation_info`. On failure, it does not refresh `out_evaluation_info`, which keeps failed evaluations from being mistaken for valid support data.

The getter section has no branching beyond pipe-to-plane mapping. Whole-mode getters return scalar fields directly. Per-surface getters translate the input DML pipe index through `mode_lib->mp.pipe_plane[]` and then index the stored plane arrays. This mapping is critical for ODM, MPC combine, phantom pipes, and other cases where DML pipe indices and logical plane indices are not identical.

## State And Persistence Behavior

All persistent state is held inside the caller-owned `struct display_mode_lib_st`; this chunk does not allocate memory, acquire locks, or program hardware.

`cache_ip_soc_cfg()` refreshes the mode-support state from top-level fields on every public call. It copies `mode_lib->soc`, `mode_lib->ip`, and `mode_lib->policy` into `mode_lib->ms`, then snapshots both the selected state and maximum state. Because these are value copies, subsequent changes to top-level bounding boxes do not affect the current calculation pass unless the public entry point is called again.

`cache_display_cfg()` copies the full display configuration into `mode_lib->ms.cache_display_cfg`. The rest of the mode-support/programming flow reads that cached version, not the caller's pointer. This is important for persistence: getters such as `dml_get_is_phantom_pipe()` inspect cached plane policy after calculations complete, and downstream code can use those values without retaining the original `display_cfg` object.

`fetch_socbb_params()` seeds the active clocks in `mode_lib->ms`. Those fields are calculation state, not hardware state. Later support logic can update DCFCLK, return bandwidth, and related fields while testing policies and state combinations.

`dml_mode_support()` persists evaluation results under `mode_lib->ms`, especially `mode_lib->ms.support`, return bandwidth fields, swath/DET values, and pipe-plane mapping inputs used later by programming and getters. `dml_mode_support_ex()` persists the same state for the lowest passing state and additionally copies `ms.support` to the caller's output structure.

`dml_mode_programming()` persists programming outputs under `mode_lib->mp`. These include watermarks, DLG timing values, calculated clocks, prefetch parameters, DPTE/META row heights, DCC block sizes, MALL sizing, immediate-flip byte counts, and `pipe_plane[]`. Most getters in this chunk are thin reads of that persisted `mp` state.

`dml_core_get_row_heights()` is an exception: it only writes the two caller-provided output pointers. It uses `mode_lib->ip` for constants, but it does not mutate `mode_lib`.

## Dependencies And Integration Points

The chunk depends on the DML2.0 core types defined in `display_mode_core_structs.h`:

- `struct display_mode_lib_st` owns top-level `soc`, `ip`, `policy`, `states`, mode-support state `ms`, mode-programming state `mp`, and scratch storage.
- `struct dml_display_cfg_st` is the display-mode input copied into `ms.cache_display_cfg`.
- `struct soc_states_st` and `struct soc_state_bounding_box_st` define voltage/SOC state arrays and clock limits.
- `struct mode_support_st` holds cached inputs, selected state data, support summary, swath/DET state, return bandwidth, and other support outputs.
- `struct mode_program_st` holds programming outputs consumed by DCHUB/RQ/DLG programming and DC bandwidth state.
- `struct dml_mode_support_ex_params_st` packages the extended mode-support search input and output pointers.

The chunk also depends on local calculation helpers defined earlier in `display_mode_core.c`: `CalculateBytePerPixelAndBlockSizes()`, `CalculateVMAndRowBytes()`, `dml_core_mode_support()`, `dml_core_mode_support_partial()`, and `dml_core_mode_programming()`. The getter declarations mirror `display_mode_core.h`, so adding, renaming, or changing a getter here requires the header to stay synchronized.

Driver integration is visible in nearby DML2 files:

- `dml2_wrapper_fpu.c` maps a DC state into `struct dml_display_cfg_st`, calls the extended support path, maps resources, and then calls `dml_mode_programming()` with the selected lowest state. It also clears `mode_lib->ms` and `mode_lib->mp` around validations, so the persistence described above is per validation/programming pass.
- `dml2_utils.c` uses these getters to copy DML results into DC structures. For example, `dml2_extract_watermark_set()` converts microsecond watermarks from `dml_get_wm_*()` to nanoseconds, `dml2_extract_writeback_wm()` reads writeback watermarks, and `dml2_calculate_rq_and_dlg_params()` uses per-pipe getters for VStartup/VUpdate/VReady, DET buffer size, DPP clock, and MALL surface size.
- `dml_display_rq_dlg_calc.c` consumes the same `mode_lib` state to derive RQ/DLG/TTU register fields, so the row-height and timing getters need to agree with those lower-level register extraction helpers.
- MALL/SubVP code such as `dml2_mall_phantom.c` relies on phantom-pipe and VStartup-related outputs to program phantom pipes and MALL-backed p-state-change behavior.

The functions here are pure model/translation APIs within the AMD display driver. They do not call DRM core APIs, memory-management APIs, or hardware register writes directly; those effects occur after DC wrapper code consumes the DML outputs.

## Risks And Edge Cases

State index validation is assert-only. `dml_get_soc_state_bounding_box()` asserts when `state_idx >= num_states`, and `mode_support_pwr_states()` asserts for reversed or out-of-range search ranges. In production builds where assertions may be less fatal or compiled differently, invalid state inputs could still produce undefined behavior if not caught by callers.

`cache_ip_soc_cfg()` assumes `mode_lib->states.num_states > 0` because it sets `max_state_idx` to `num_states - 1` and fetches the max-state bounding box. An empty state table would underflow the index and trip the later assertion. Correct SoC initialization is therefore a hard prerequisite.

`dml_core_get_row_heights()` intentionally calls `CalculateVMAndRowBytes()` with synthetic values: DCC enabled, GPUVM enabled, one DPP, four GPUVM page-table levels, zero viewport/swath dimensions, and zero DCC meta pitch. This is suitable for row-height discovery but not a general row-byte calculation. A caller expecting exact row bytes, DPTE storage, or frame metadata from this helper would get discarded/dummy data.

The row-height helper selects chroma values when `is_plane1` is true. Formats without chroma still rely on `CalculateBytePerPixelAndBlockSizes()` to produce sane chroma outputs. If callers pass `is_plane1` for a format that does not have a valid plane 1, the returned row heights may not correspond to a real plane.

The getter macros perform no bounds checks. Whole-mode getters assume the relevant support or programming pass has already populated `mode_lib->ms` or `mode_lib->mp`. Per-surface getters assume `surface_idx` is a valid DML pipe index and that `mode_lib->mp.pipe_plane[surface_idx]` contains a valid plane index. A stale or uninitialized `pipe_plane[]` mapping can redirect every per-surface getter to the wrong plane or beyond valid arrays.

`dml_get_is_phantom_pipe()` has the same mapping risk and also depends on `ms.cache_display_cfg` matching the programming state. If programming is run with one display config and getters are read after another support pass, cached policy and `mp.pipe_plane[]` could describe different configurations.

`dml_mode_programming()` returns only `PrefetchAndImmediateFlipSupported`. That is a practical success signal for programming, but it means callers must not infer that every support-policy field is valid unless they either ran full support first or used `call_standalone` to trigger the partial support setup. The standalone path also assumes immediate flip support before the partial pass, which is a deliberate optimistic seed for calculating programming fields.

`mode_support_pwr_states()` initializes `*lowest_state_idx` to `end_state_idx` even when no state passes. Callers must check the returned boolean before using the index. `dml_mode_support_ex()` follows this rule by copying `out_evaluation_info` only on success.

Several getters return values with unit conventions that differ from downstream DC structures. Watermark getters return DML units that `dml2_utils.c` multiplies by 1000 to store nanoseconds. Clock getters often return MHz and are converted to kHz elsewhere. Unit mistakes at call sites can lead to large over/under-programming errors.

## Test Signals

Useful validation signals for this chunk are mostly integration-level because the functions are glue around large DML calculations:

- Mode validation should select the lowest passing SOC state through `dml_mode_support_ex()`. Tests should cover start indices other than zero, unsupported configurations, and configurations that first pass at a higher state.
- A full support-then-programming flow and a standalone programming flow should produce coherent programming outputs for the same valid configuration, especially prefetch/immediate-flip status, watermarks, DCFCLK deep sleep, VStartup/VUpdate/VReady values, and DET sizes.
- DML debug builds with `__DML_RQ_DLG_CALC_DEBUG__` should show row-height helper inputs and outputs that track source format, tiling, rotation, pitch, page size, and luma/chroma DPTE buffer request limits.
- Per-pipe DC programming should receive the expected plane values when ODM, MPC combine, SubVP phantom pipes, or multiple pipes per surface are active. This specifically exercises the `mp.pipe_plane[]` mapping used by the getter macros.
- Watermark extraction in `dml2_extract_watermark_set()` should show expected unit conversion from DML microsecond-style outputs to DC nanoseconds, including urgent, stutter, DRAM/FCLK p-state, USR retraining, and Z8 watermarks.
- Writeback watermark extraction should remain stable for configurations with and without DWB enabled, using `dml_get_wm_writeback_urgent()` and `dml_get_wm_writeback_dram_clock_change()`.
- Phantom-pipe tests should confirm `dml_get_is_phantom_pipe()` and MALL-related getters agree with `UseMALLForPStateChange` policy and that phantom pipes get zero DET/unbounded-request treatment in downstream code.
- Negative or boundary tests should exercise invalid state ranges under assertion-enabled builds, zero or one SOC state, maximum pipe/surface indices, and unsupported modes where `dml_mode_support_ex()` returns false without refreshing `out_evaluation_info`.

## Cross-Chunk Notes

The preceding chunks of this same file contain the formula-heavy support and programming engines that populate the state exposed here: swath/DET setup, VM/PTE/META row-byte calculation, prefetch scheduling, urgent burst factors, watermarks, DRAM/FCLK clock-change support, stutter efficiency, and DLG/RQ values. The following chunks continue the getter surface beyond line 10362. The final per-file report should treat this chunk as the API/export boundary for DML2.0 core calculations rather than as a standalone calculation engine.

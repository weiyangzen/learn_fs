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

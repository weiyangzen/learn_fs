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

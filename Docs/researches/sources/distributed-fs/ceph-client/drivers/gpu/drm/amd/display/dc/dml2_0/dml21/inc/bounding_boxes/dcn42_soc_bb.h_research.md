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

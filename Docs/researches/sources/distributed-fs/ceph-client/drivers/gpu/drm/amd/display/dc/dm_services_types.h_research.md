# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dm_services_types.h

## Purpose
Defines shared Display Manager service data types for power/clock levels, watermark ranges, display configuration, ACPI backlight and display types, DMUB wait behavior, and PHY transition parameters.

## Important APIs, Types, And Functions
Key types include `dm_pp_clock_range`, `dm_pp_clocks_state`, `dm_pp_gpu_clock_range`, `dm_pp_clock_type`, `dm_pp_clock_levels`, latency/voltage clock level structs, `dm_pp_single_disp_config`, watermark set/range structs, `dm_pp_display_configuration`, ACPI backlight capability structures, `dm_pp_power_level_change_request`, `dm_pp_clock_for_voltage_req`, `dm_pp_static_clock_info`, `dtn_min_clk_info`, `dm_dmub_wait_type`, ACPI transition link types, and PHY transition input/init payloads. `DC_DECODE_PP_CLOCK_TYPE()` converts clock type enum values to strings.

## Control Flow
The file contains type definitions only. Runtime flow is driven by consumers in `dm_services.h`, PP/SMU integration, clock managers, ACPI transition code, and display configuration builders.

## State And Persistence
Instances of these structures persist in higher-level objects such as `core_types` display configuration, clock manager state, and temporary service requests. The header itself has no storage.

## Dependencies And Integration Points
Includes `os_types.h` and `dc_types.h`, and forward-declares `pp_smu_funcs`. The types are used by Display Core, AMDGPU DM PP/SMU implementations, ACPI integration, DMUB command code, and link/clock policy logic.

## Risks
Several fixed-size arrays impose limits, including clock levels, watermark sets, display configs, and backlight data points. Unit consistency matters: many clocks are KHz, while SMU-specific files may use MHz. The backlight structure has a size constraint comment that must remain compatible with ACPI ATIF expectations. Adding enum values without updating string decoding or provider mappings can reduce diagnostics or break policy conversion.

## Test Signals
Compile consumers after type changes, validate clock-level conversion and display configuration population, test watermark set limits, ACPI backlight parsing size/layout, DMUB wait behavior, and PHY transition payloads for HDMI TMDS/FRL and DP 8b/10b or 128b/132b links.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dm_pp_smu.h

## Purpose
Defines Display Core's interface to PowerPlay/SMU services for display clocks, voltage, watermarks, DPM tables, p-state handshake, and SMU timeout notification across multiple ASIC families.

## Important APIs, Types, And Functions
Core types are `enum pp_smu_ver`, `struct pp_smu`, `enum pp_smu_status`, watermark range/set structs, `enum wm_type`, `enum pp_smu_nv_clock_id`, `struct pp_smu_nv_clock_table`, DPM clock tables, and family-specific callback structs `pp_smu_funcs_rv`, `pp_smu_funcs_nv`, `pp_smu_funcs_rn`, and `pp_smu_funcs_vgh`. The top-level `struct pp_smu_funcs` stores a common context plus a union of family-specific interfaces.

## Control Flow
The header provides callback contracts only. Clock managers obtain or fill a `pp_smu_funcs` object and invoke the family-appropriate callbacks to set display count, hard minimum clocks, deep-sleep DCFCLK, voltage-by-frequency, watermark ranges, maximum sustainable clocks, UCLK DPM states, p-state handshake support, DPM clock tables, PME workaround, or timeout notification.

## State And Persistence
Persistent state is held by the SMU/PP provider via `pp_smu.pp` and `pp_smu.dm` opaque handles. Watermark and clock table structures are transient inputs/outputs, though many callers allocate GPU-visible tables for SMU transfer.

## Dependencies And Integration Points
This header is included by core types and AMDGPU DM PP/SMU implementation. DC clock managers for DCE/DCN families use these contracts to communicate display requirements and memory/DCF/SOC/FCLK/UCLK constraints to power management firmware.

## Risks
Family-specific unions require callers to use the correct interface version. Unit mismatches are easy: some fields use MHz, others KHz. Watermark table structures copy firmware ABI layouts, so layout drift can break SMU transfers. Unsupported callbacks must be handled gracefully. Incorrect p-state or hard-min clock programming can cause underflow, excessive power, or failed mode validation.

## Test Signals
Validate clock manager flows on RV/NV/RN/VGH-class paths, watermark programming, hard-min clock requests, DPM table queries, max sustainable clock reads, p-state handshake toggles, display count changes, SMU timeout notifications, and unit conversions between DC KHz and SMU MHz.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn401/dcn401_clk_mgr_smu_msg.h

## Purpose
This header declares the DCN 4.01 SMU message wrapper interface consumed by `dcn401_clk_mgr.c`.

## Important APIs, Types, And Functions
It forward-declares `struct clk_mgr_internal` and declares bool-returning version checks, void setters for p-state/CAB/table/PME/display-count policy, hardmin setters and queries, and DPM information queries. Important functions include `dcn401_smu_get_smu_version`, `dcn401_smu_check_driver_if_version`, `dcn401_smu_check_msg_header_version`, `dcn401_smu_set_hard_min_by_freq`, `dcn401_smu_set_idle_uclk_fclk_hardmin`, `dcn401_smu_set_active_uclk_fclk_hardmin`, `dcn401_smu_set_subvp_uclk_fclk_hardmin`, `dcn401_smu_get_dpm_freq_by_index`, and `dcn401_smu_get_dc_mode_max_dpm_freq`.

## Control Flow And Integration
The clock manager includes this header and never touches DAL mailbox registers directly. Initialization uses the version and DPM query functions. Runtime clock updates use hardmin, p-state, CAB, display count, DMCUB wait, and DRR declarations. Watermark notification uses DRAM address setters and the table transfer function.

## State And Persistence
The header itself has no state. Its API methods operate on `clk_mgr_internal`, using cached SMU presence/version state and mutating firmware-side clock/power policy.

## Dependencies
The declarations depend on `os_types.h` and `core_types.h` for integer, bool, and Display Core type definitions. Implementations depend on `dalsmc.h` and `dcn401_smu14_driver_if.h`.

## Risks
Some functions return void even though the underlying transport can fail. Callers therefore cannot always distinguish accepted from dropped firmware policy changes. In contrast, hardmin and query functions return values but use zero as failure in several paths, which can collide with valid disabled/lowest states.

## Test Signals
Compile-time coverage catches signature drift between clock manager and wrapper. Runtime tests should verify that void setters still generate trace events and that failure injection does not leave clock-manager cached state inconsistent with firmware.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn35/dcn35_clk_mgr.h

## Purpose
This header declares the DCN 3.5 display clock manager interface and the DCN 3.5 specific `clk_mgr_internal` wrapper used by AMD Display Core. It is the public contract between generic clock-manager selection code, DCN 3.5 clock-manager implementation files, and the DCN 3.5 SMU mailbox layer.

## Important APIs, Types, And Functions
`struct clk_mgr_dcn35` embeds `struct clk_mgr_internal` and adds `smu_wm_set`, so all generic clock-manager function table consumers can treat the object as a base clock manager while DCN 3.5 code can keep SMU watermark table state. `struct dcn35_smu_watermark_set` couples a CPU-visible `struct dcn35_watermarks *` with a GPU memory controller address for SMU table transfer. `struct dcn35_ss_info_table` stores spread-spectrum divider and per-clock-source percentages.

Declared entry points include `dcn35_init_clocks`, `dcn35_update_clocks`, `dcn35_clk_mgr_construct`, `dcn351_clk_mgr_construct`, `dcn35_clk_mgr_destroy`, `dcn35_are_clock_states_equal`, and `dcn35_disable_otg_wa`. The separate DCN 3.5 and DCN 3.5.1 constructors indicate shared structure with variant-specific setup.

## Control Flow And Integration
Generic clock-manager creation in `clk_mgr.c` selects this family and calls a constructor. Runtime display validation later calls the function table installed by the implementation, which uses these declarations for clock initialization, clock updates, and teardown. The header intentionally forward-declares `struct dcn35_watermarks`; the concrete SMU watermark layout is owned by `dcn35_smu.h`.

## State And Persistence
State is held in the live `clk_mgr_dcn35` allocation and in GPU memory referenced by `smu_wm_set`. There is no durable storage; persistence is limited to driver lifetime and SMU-visible memory until freed by destroy paths.

## Dependencies
The header depends on `clk_mgr_internal.h` for base clock-manager types and on common Display Core types such as `dc_context`, `dc_state`, `dc_clocks`, `dccg`, and `pp_smu_funcs` through included or transitive declarations.

## Risks
The most important risk is lifetime correctness for `smu_wm_set`: the SMU receives a physical address, so stale or freed memory would corrupt firmware interactions. The header also exposes variant constructors with identical object type, so implementation selection must match ASIC revision.

## Test Signals
Useful signals are successful display bring-up on DCN 3.5/3.5.1, SMU watermark transfer logs, no leaks across clock-manager destroy, and trace/assert coverage around `dcn35_update_clocks` and OTG disable workaround paths.

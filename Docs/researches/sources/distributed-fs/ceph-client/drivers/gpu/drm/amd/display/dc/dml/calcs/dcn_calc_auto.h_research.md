# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/calcs/dcn_calc_auto.h

## Purpose
Declares the generated DCN bandwidth calculation entry points implemented in `dcn_calc_auto.c`. It exposes the calculation phases to the surrounding DCN calculation driver.

## Important APIs, Types, And Functions
The header declares `scaler_settings_calculation()`, `mode_support_and_system_configuration()`, `display_pipe_configuration()`, and `dispclkdppclkdcfclk_deep_sleep_prefetch_parameters_watermarks_and_performance_calculation()`, each accepting `struct dcn_bw_internal_vars *v`.

## Control Flow
The header has no implementation, but the declarations imply the phase order used by `dcn_calcs.c`: derive scaler ratios/taps, evaluate mode support/system configuration, choose display pipe configuration, then calculate clocks, prefetch, watermarks, and performance outputs.

## State And Persistence
No state is stored here. All functions mutate caller-provided `struct dcn_bw_internal_vars` in place.

## Dependencies And Integration Points
Includes `dc.h` and `dcn_calcs.h` for core display types and the bandwidth internal variable structure. `dcn_calcs.c` includes this header to orchestrate generated equations.

## Risks
Prototype drift between this header and the generated implementation breaks the DML build. Because all APIs mutate a large shared struct, adding or reordering phases without updating callers can yield stale intermediate values.

## Test Signals
Compile DML calculators and run bandwidth validation paths that call every declared phase. Golden DML tests should detect behavior changes in phase sequencing or struct field interpretation.

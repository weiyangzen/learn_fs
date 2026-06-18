# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn32/dcn32_dpp.c

## Purpose
`dcn32_dpp.c` adapts the DCN3 DPP implementation for DCN 3.2. It keeps most DCN30 callbacks, removes DPP-local BLNDGAM/shaper/3D LUT programming because those blocks moved out of the DPP, and replaces line-buffer partition calculations with DCN32-specific memory sizing.

## Important APIs, types, and functions
- `dpp32_construct()` initializes a `struct dcn3_dpp` with DCN32 function and cap tables.
- `dscl32_calc_lb_num_partitions()` computes luma/chroma line-buffer partition counts for `struct scaler_data`.
- `dscl32_spl_calc_lb_num_partitions()` performs the same calculation for SPL scaler data.
- `dcn32_dpp_funcs` inherits DCN30 GAMCOR, post-CSC/CNVC setup, pre-degamma, cursor, gamut remap, CM bias/dealpha, tap selection, readback, and DPP clock callbacks, but sets blend LUT, shaper LUT, and 3D LUT callbacks to NULL.
- `dcn32_dpp_cap` advertises floating DSCL processing, max 31 line-buffer partitions, and the DCN32 partition calculator.

## Control flow
Construction stores base context/instance, installs `dcn32_dpp_funcs`, installs `dcn32_dpp_cap`, and records DCN3 register tables. The partition calculators choose the lesser of viewport and recout width for luma/chroma, guard zero widths as one, compute memory line sizes by dividing by six with ceiling, choose memory capacities based on `enum lb_memory_config`, account for full-active non-scaling cases with larger effective memory, include alpha memory as a luma limiter when enabled, and cap output counts at 32.

## State and persistence behavior
This file does not create new persistent state. It populates existing `struct dcn3_dpp` fields and provides stateless calculations. Runtime state remains in the DPP object, DC debug/cap flags, and hardware registers programmed by inherited callbacks.

## Dependencies and integration points
The file includes DC core types, register helpers, `dcn32_dpp.h`, DCN30 color helpers, and conversion helpers. It integrates with DC resource construction through `dpp32_construct()`, and with scaler/tap logic because `dpp3_get_optimal_number_of_taps()` calls the cap-supplied line-buffer partition function.

## Risks and edge cases
The partition constants are hardware-specific magic values; incorrect values or caps can produce unsupported tap choices. The 32 cap coexists with `max_lb_partitions = 31`, so callers must preserve the intended off-by-one hardware interpretation. Removing BLNDGAM/shaper/3D LUT callbacks means higher-level code must route those operations to MPCC or tolerate NULL callbacks. Zero-dimension guards avoid division by zero but can hide invalid scaler input.

## Test signals
Build and boot on DCN32 ASICs, scaler validation for RGB and 4:2:0 formats, alpha-enabled line-buffer cases, SPL and non-SPL partition parity, callback NULL handling for moved color blocks, and visual tests for inherited GAMCOR/CSC/cursor paths are the important signals.

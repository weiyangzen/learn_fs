# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn32/dcn32_dpp.h

## Purpose
`dcn32_dpp.h` is the small public/private header for DCN32 DPP construction and SPL line-buffer partition calculation. It reuses the DCN20 and DCN30 DPP type/register model rather than defining a new DPP structure.

## Important APIs, types, and functions
- `dpp32_construct()` constructs a DCN32 DPP instance using `struct dcn3_dpp` and DCN3 register tables.
- `dscl32_spl_calc_lb_num_partitions()` exposes the SPL scaler-data variant of the line-buffer partition calculator.

## Control flow
There is no executable flow in the header. It provides prototypes used by resource construction and scaler code.

## State and persistence behavior
No state is stored here. DCN32 instances use `struct dcn3_dpp` from `dcn30_dpp.h`; partition calculations are stateless.

## Dependencies and integration points
The header depends on `dcn20/dcn20_dpp.h` and `dcn30/dcn30_dpp.h`. It is included by DCN32 implementation and later code, including DCN401, that reuses the SPL partition helper pattern.

## Risks and edge cases
Because DCN32 intentionally reuses DCN3 structures, prototype changes ripple to later generations. The header does not define a `TO_DCN32_DPP()` cast, so callers must know that `struct dcn3_dpp` remains the concrete type.

## Test signals
Compile coverage for DCN32 resource construction and callers of `dscl32_spl_calc_lb_num_partitions()` is the main signal, supplemented by runtime scaler tests from the implementation file.

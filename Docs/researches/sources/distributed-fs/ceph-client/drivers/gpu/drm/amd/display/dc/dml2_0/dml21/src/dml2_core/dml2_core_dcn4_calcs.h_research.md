# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_core/dml2_core_dcn4_calcs.h

## Purpose
Declares the DCN4 core calculation API used by DML21 mode support and mode programming. The header is the public face of the core calculator implementation: callers pass display configuration, mode-lib state, and output register/programming structures, and the implementation emits support decisions, watermarks, arbiter registers, pipe registers, stream programming, MALL/MCACHE data, FAMS2 data, and debug string conversions.

## Important APIs, types, and functions
- `dml2_core_calcs_mode_support_ex()` evaluates a `dml2_display_cfg` against a min-clock table and project id, updating `dml2_core_internal_display_mode_lib` and returning a support result status.
- `dml2_core_calcs_mode_programming_ex()` consumes the selected support state and emits `dml2_display_cfg_programming`.
- `dml2_core_calcs_get_watermarks()`, `dml2_core_calcs_get_arb_params()`, `dml2_core_calcs_get_pipe_regs()`, and `dml2_core_calcs_get_stream_programming()` map the internal mode-programming state into DC hub/display programming structures.
- `dml2_core_calcs_get_global_sync_programming()`, `dml2_core_calcs_get_stream_fams2_programming()`, and `dml2_core_calcs_get_global_fams2_programming()` expose synchronization and FAMS2 programming derived by core calculations.
- `dml2_core_calcs_get_mcache_allocation()`, `dml2_core_calcs_get_mall_allocation()`, `dml2_core_calcs_get_plane_support_info()`, `dml2_core_calcs_get_stream_support_info()`, and `dml2_core_calcs_get_informative()` expose support and informational state to the top layer.
- `dml2_core_calcs_get_dpte_row_height()` and `dml2_core_calcs_cursor_dlg_reg()` are narrower helpers for DPTE row and cursor DLG programming.

## Control flow and integration
The expected flow is mode support first, mode programming second, then register/programming getters. It includes only prototypes and forward declarations, so state ownership is external: `dml2_core_internal_display_mode_lib` is allocated and initialized by the core instance selected through the core factory, while output structures are supplied by top-level DML code or DPMM.

## State and persistence behavior
This header stores no data. It defines access points into the persistent per-core `mode_lib`, whose `ms`, `mp`, and `scratch` fields are defined in `dml2_core_shared_types.h`. Callers must preserve the mode-lib instance across support/programming/getter calls for coherent outputs.

## Dependencies
Includes `dml2_core_shared_types.h` and relies on DCN/DML top-level structures such as `dml2_display_cfg`, `dml2_display_cfg_programming`, DCHUB register sets, DMUB FAMS2 commands, and p-state enums. It forward-declares several register/support structures to reduce include coupling.

## Risks and edge cases
The API relies on strict call ordering and valid array indices for `pipe_index` and `plane_index`; the header does not encode bounds. Several getters expose data produced by prior calculations, so using them before successful mode programming may return stale or uninitialized values. FAMS2 functions depend on `display_configuation_with_meta`, making implicit SubVP/FAMS metadata part of the contract.

## Test signals
Useful tests instantiate supported project ids, run mode support/programming for representative single-stream, multi-stream, DSC, ODM, SubVP/FAMS2, and cursor cases, then compare emitted watermarks/registers/support info against known-good values. Negative tests should call unsupported formats or invalid indices only in harnesses that can catch assertions.

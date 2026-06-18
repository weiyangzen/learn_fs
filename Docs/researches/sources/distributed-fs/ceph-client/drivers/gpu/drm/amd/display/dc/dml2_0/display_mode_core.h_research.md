# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/display_mode_core.h

## Purpose
`display_mode_core.h` is the public C interface for the legacy DML 2.0 display mode core. It exposes mode-support evaluation, mode-programming generation, bandwidth helpers, row-height calculation, and many accessor functions for computed watermarks, clocks, pipe timing, request queue, DCC, MALL, and DET values.

## Important APIs, types, and functions
The main entry points are `dml_core_mode_support()`, `dml_core_mode_support_partial()`, `dml_core_mode_programming()`, `dml_mode_support()`, `dml_mode_programming()`, and `dml_mode_support_ex()`. `dml_core_get_row_heights()` computes DPTE/meta row heights for a plane and tiling mode. `dml_get_return_bw_mbps()` and `dml_get_return_bw_mbps_vm_only()` expose return bandwidth formulas. The `dml_get_var_decl` and `dml_get_per_surface_var_decl` macros declare a broad getter surface for values stored in `struct display_mode_lib_st`.

## Control flow
This header has no implementation logic, but it defines the expected flow for callers: fill `display_mode_lib_st` with SoC/IP/policy/display state, call support evaluation for a state or display config, optionally call programming with a clock policy, then consume register/programming outputs through getters. The `dml_mode_support_ex_params_st` path wraps support evaluation with input and output pointers.

## State and persistence behavior
All state is caller-owned in `struct display_mode_lib_st`. The API mutates only in-memory mode support/programming fields; it has no durable persistence and no independent allocation contract in this header.

## Dependencies and integration points
It depends on `display_mode_core_structs.h` for the full DML data model and integrates with DML calculation implementations elsewhere in `dml2_0`. Consumers include wrapper layers that translate driver `dc_state` into DML inputs and consume DCHUB/HUBP timing outputs.

## Risks and edge cases
The getter set is macro-declared and easy to desynchronize from implementation fields. Many getters are per-surface and assume valid plane indices under `__DML_NUM_PLANES__`. Clock and bandwidth helpers operate on model units, so kHz/MHz/Mbps conversion mistakes at wrapper boundaries can produce invalid programming.

## Test signals
Useful signals are build coverage for every getter implementation, mode-support/programming tests over single and multi-plane configs, bandwidth unit checks, row-height checks for linear/tiled/rotated/420 cases, and comparison of generated RQ/DLG/TTU values against known DML vectors.

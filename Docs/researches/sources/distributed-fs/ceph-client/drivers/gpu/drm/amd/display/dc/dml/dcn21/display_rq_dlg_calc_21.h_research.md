# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn21/display_rq_dlg_calc_21.h

## Purpose

This header exposes the DCN 2.1 request queue and DLG/TTU calculation interface to the rest of Display Mode Library. It is a narrow declaration file: it includes service/helper declarations, forward-declares `struct display_mode_lib`, and publishes the two functions implemented in `display_rq_dlg_calc_21.c`.

The file documents that these functions are the main entry points for tests and callers that need DML-calculated register values. It does not define data structures itself; it relies on shared DML typedefs such as `display_rq_regs_st`, `display_pipe_params_st`, `display_dlg_regs_st`, `display_ttu_regs_st`, and `display_e2e_pipe_params_st`.

## Important APIs, Types, and Functions

`dml21_rq_dlg_get_rq_reg()` calculates request queue register fields for one pipe source configuration. It takes a `display_mode_lib *`, an output `display_rq_regs_st *`, and a `const display_pipe_params_st *`. The comment describes it as the test-facing path that calls the internal RQ parameter and register extraction routines.

`dml21_rq_dlg_get_dlg_reg()` calculates DLG and TTU register structs for a selected pipe in a compacted pipe array. It takes output `display_dlg_regs_st *` and `display_ttu_regs_st *`, the end-to-end pipe array, pipe count, target pipe index, cstate/pstate enable flags, VM enable, viewport-position ignore flag, and immediate flip support flag. In this DCN 2.1 implementation the latter three flags are accepted for interface compatibility but are explicitly unused by the C file.

The header includes `dm_services.h` and `../display_rq_dlg_helpers.h`, which provide common AMD display service types, assertions, and DML register/helper declarations required for prototypes and callers.

## Control Flow

There is no executable control flow in this header. Its role is compile-time integration: include guards prevent duplicate declarations, and callers include it to bind to the DCN 2.1 implementation. The DML function table in `display_mode_lib.c` references the declarations when assigning the DCN 2.1 RQ/DLG callbacks.

## State and Persistence Behavior

The header has no state, storage, or persistence. It establishes an ABI-like source contract between DML core code and the DCN 2.1 implementation. The only state implications are in the pointer parameters: callers are responsible for providing valid mode-lib input and writable output register structs.

## Dependencies and Integration Points

This file is coupled to shared DML display mode structs and helper declarations. It is included by `display_rq_dlg_calc_21.c` and is also indirectly important to `display_mode_lib.c`, where DCN 2.1 function pointers are initialized. Its sibling headers for DCN20, DCN30, DCN31, and later generations follow a similar contract, which allows project-specific DML implementations to be swapped behind common function pointers.

## Risks and Edge Cases

The main header-level risk is signature drift. The C implementation currently ignores `vm_en`, `ignore_viewport_pos`, and `immediate_flip_support`; if callers assume those flags change behavior for DCN 2.1, they will get misleading results. Another risk is include-order fragility because the prototypes use DML typedefs that must be available through the included helper headers or prior includes.

## Test Signals

Compile coverage should verify that all users can include the header without missing typedefs. Functional tests should call both exported functions through the `display_mode_lib` callback table and directly in any DML unit harness, confirming that output structs are fully initialized and match golden register values for DCN 2.1 mode cases.

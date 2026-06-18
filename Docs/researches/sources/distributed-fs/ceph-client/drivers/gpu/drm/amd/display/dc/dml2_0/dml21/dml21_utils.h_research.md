# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/dml21_utils.h

## Purpose
`dml21_utils.h` declares the DML2.1 utility functions used to map DML programming results onto DC pipe state and firmware payload state.

## Important APIs, types, and functions
It declares mapping lookup helpers, pipe-register index helpers, `dml21_find_dc_pipes_for_plane()`, `dml21_program_dc_pipe()`, phantom stream/plane handling, FAMS2 programming, DP2.0 detection, MALL allocation accounting, and plane1 enablement.

## Control flow
The header has no logic. It organizes the utility sequence used after DML mode programming: resolve mappings, find pipes, program pipe-level state, add phantoms when needed, and build firmware programming.

## State and persistence behavior
No state is declared here. Callers pass `dml2_context`, `dc_state`, `pipe_ctx`, and DML programming objects to implementation functions.

## Dependencies and integration points
It forward declares DC and DML types and is included by DML2.1 translation, wrapper, and resource-management code. Its prototypes rely on `__DML2_WRAPPER_MAX_STREAMS_PLANES__` and DML enum definitions being visible before inclusion in some compile units.

## Risks and edge cases
Because several APIs accept raw arrays sized by a macro, callers must allocate the expected number of entries. Invalid mapping return values use signed `int` for some functions and unsigned for others elsewhere, so comparisons need care.

## Test signals
Compile coverage plus DML2.1 programming tests with normal, ODM/MPC split, blank, and SubVP states exercise the declared surface.

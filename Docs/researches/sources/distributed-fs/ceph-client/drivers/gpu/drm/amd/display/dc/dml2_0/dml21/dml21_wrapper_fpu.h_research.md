# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/dml21_wrapper_fpu.h

## Purpose
`dml21_wrapper_fpu.h` declares the FPU-requiring DML2.1 wrapper entry points for initialization, reinitialization, validation, and mcache register preparation.

## Important APIs, types, and functions
It declares `dml21_init()`, `dml21_reinit()`, `dml21_validate()`, and `dml21_prepare_mcache_programming()`. The comments document validate modes: mode-only and state-index validation avoid populating `context.res_ctx`, while programming validation generates hardware programming for the new state.

## Control flow
The header defines the public sequence expected by callers: initialize or reinitialize the context, validate a `dc_state` according to requested mode, and later prepare mcache programming after allocation data exists.

## State and persistence behavior
No state is declared. Implementations mutate caller-owned DML and DC state. The comments explicitly warn that concurrent validation requires separate `dc_state` objects.

## Dependencies and integration points
It includes OS and DML top-level type headers and forward declares DC/DML types. It is included by lifecycle code in `dml21_wrapper.c` and by DC validation callers operating inside FPU protection.

## Risks and edge cases
Concurrency is the primary documented risk: two threads must not invoke validation concurrently on shared state. Callers must also honor FPU protection requirements; the type system does not enforce that.

## Test signals
Build coverage, FPU-protected call-path tests, validate-mode behavior, concurrent separate-state validation, and mcache preparation after successful programming are useful signals.

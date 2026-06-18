# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/inc/dml_top.h

## Purpose
`dml_top.h` is the top-level public interface for the DML2 core used by DML2.1 wrappers. It declares instance sizing, initialization, support checking, full mode programming, and mcache programming APIs.

## Important APIs, types, and functions
The API surface is `dml2_get_instance_size_bytes()`, `dml2_initialize_instance()`, `dml2_check_mode_supported()`, `dml2_build_mode_programming()`, and `dml2_build_mcache_programming()`. Parameter and output structures come from `dml_top_types.h`.

## Control flow
Callers allocate or provide an instance, initialize it with SoC/IP/options, call support checks for boolean feasibility, call build-mode-programming for optimized clocks and register values, and call build-mcache-programming after mcache allocation and pipe geometry are known.

## State and persistence behavior
The DML instance is caller-owned memory. The API fills in-out structures and programming outputs in memory only; there is no persistence.

## Dependencies and integration points
It depends on `dml_top_types.h`. `dml21_wrapper.c` and `dml21_wrapper_fpu.c` call these functions to initialize and validate DML2.1 contexts and to produce DC hardware programming.

## Risks and edge cases
Correct sequencing matters: mcache programming requires successful mode programming first, and build-mode-programming is the only path that returns full optimized hardware values. Callers must manage instance allocation size and lifetime consistently with the implementation.

## Test signals
Instance-size/allocation tests, initialization with DCN401/DCN42 bounding boxes, support-only checks, full programming checks, mcache programming after allocation, and invalid sequencing tests are useful signals.

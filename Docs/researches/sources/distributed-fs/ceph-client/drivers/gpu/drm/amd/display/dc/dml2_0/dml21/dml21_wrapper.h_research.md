# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/dml21_wrapper.h

## Purpose
`dml21_wrapper.h` exposes the DML2.1 context lifecycle API and declares shared wrapper-side structures for external SoC/IP parameters and DC mcache programming inputs.

## Important APIs, types, and functions
It declares `dml21_create()`, `dml21_destroy()`, `dml21_copy()`, and `dml21_create_copy()`. `struct socbb_ip_params_external` carries externally supplied `dml2_ip_capabilities` and `dml2_soc_bb` for debugging/tool flows. `struct dc_mcache_params` describes per-plane mcache allocation validity, dedicated requirements, plane0/plane1 cache counts, last-slice sharing flags, and x-offset boundaries.

## Control flow
The header has no implementation logic. Its comments define lifecycle expectations: creation is part of DC state creation and initializes DML2.1 IP/SOC/states immediately.

## State and persistence behavior
The declared structures are in-memory configuration/programming carriers. `dc_mcache_params` is populated from DML mode-programming output and consumed by DC resource callbacks.

## Dependencies and integration points
It includes OS and DML top SoC/display type headers. It is included by wrapper, translation, FPU validation, and callers that need external bounding-box injection or mcache allocation data.

## Risks and edge cases
The mcache offset arrays are fixed at `DML2_MAX_MCACHES + 1`; allocation producers and hardware programmers must agree on boundary semantics. External SoC/IP injection can bypass native translator safeguards, so invalid tables can poison all downstream validation.

## Test signals
Compile coverage, external SoC/IP debug initialization, mcache allocation cases with plane0/plane1 sharing, and lifecycle create/copy/destroy tests are the main signals.

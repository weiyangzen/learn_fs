# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_core/dml2_core_factory.h

## Purpose
Declares the core factory entry point for constructing a `dml2_core_instance` from a `dml2_project_id`.

## Important APIs, types, and functions
- `dml2_core_create()` is the single exported API.
- It depends on `struct dml2_core_instance` from internal shared types and `enum dml2_project_id` from top-level DML types.

## Control flow and integration
The header is included by top-level DML initialization code that needs to bind core callbacks and by the implementation file. It hides project-specific callback selection behind one factory call.

## State and persistence behavior
No state is stored in the header. The function it declares mutates caller-provided `out` storage.

## Dependencies
Includes `dml2_internal_shared_types.h` and `dml_top_types.h`.

## Risks and edge cases
The API returns only bool and leaves error reason implicit, so callers need project-id validation or logging around failed creation. Because the header exposes no capability query, code must track supported project ids in sync with the implementation switch.

## Test signals
Compile-time test coverage is mostly include/link coverage. Runtime factory tests should verify the implementation fills valid callbacks for supported ids and returns false for null/invalid inputs.

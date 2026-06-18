# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_core/dml2_core_dcn4.h

## Purpose
`dml2_core_dcn4.h` declares the DCN4/DCN42 core implementation entry points used by the DML core factory. It is the narrow interface between project selection and the implementation in `dml2_core_dcn4.c`.

## Important APIs, Types, And Functions
The header declares `core_dcn4_initialize()`, `core_dcn42_initialize()`, `core_dcn4_mode_support()`, `core_dcn4_mode_programming()`, `core_dcn4_populate_informative()`, and `core_dcn4_calculate_mcache_allocation()`. All signatures use internal in/out structs declared elsewhere, including `dml2_core_initialize_in_out`, `dml2_core_mode_support_in_out`, `dml2_core_mode_programming_in_out`, `dml2_core_populate_informative_in_out`, and `dml2_calculate_mcache_allocation_in_out`.

## Control Flow And Integration
The header has no control flow. `dml2_core_factory.c` includes it and assigns these functions into a `dml2_core_instance` based on `dml2_project_id`. DCN40 and DCN4 stage2 projects use `core_dcn4_initialize`; DCN42 uses `core_dcn42_initialize`; all supported DCN4-family projects share the mode support, programming, informative, and MCache allocation functions.

## State And Persistence Behavior
No state is declared here. State is passed through the in/out structures and stored in the `dml2_core_instance` by the implementation. The functions return `bool` success/failure and mutate caller-provided objects.

## Dependencies
The header intentionally does not include the definitions for its parameter structs, so includers must include internal shared type headers before using the prototypes in a context that requires complete types. This keeps the header small but makes include ordering important.

## Risks And Edge Cases
Because the prototypes use structs that are not forward-declared in this header, standalone inclusion can produce compile errors unless prior includes supply declarations. The shared function set for DCN4 and DCN42 means implementation changes must preserve both projects' behavior. Any signature change requires updates in the factory and internal shared type declarations.

## Test Signals
Compile coverage through `dml2_core_factory.c` is the primary signal. Runtime tests should verify each supported `dml2_project_id` installs the expected initializer and shared operation callbacks, and that unsupported/invalid project IDs do not expose these functions.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce100/dce100_resource.h

## Purpose
Declares the DCE100 resource-pool factory and validation/resource helper APIs. It is the external contract for `dce100_resource.c`.

## Important APIs and Types
Forward declarations cover `struct dc`, `struct resource_pool`, and `struct dc_validation_set`. Prototypes expose `dce100_create_resource_pool()`, `dce100_validate_plane()`, `dce100_validate_global()`, `dce100_validate_bandwidth()`, `dce100_add_stream_to_ctx()`, and `dce100_find_first_free_match_stream_enc_for_link()`.

## Control Flow and State
The header has no executable flow. It allows the ASIC selection layer and shared resource code to create a DCE100 pool and call generation-specific validation and mapping helpers. Persistent state is owned by the returned `struct resource_pool`.

## Dependencies and Integration Points
Relies on common Display Core type definitions being visible to includers. The implementation uses these declarations in the resource function table and external ASIC initialization paths.

## Risks and Test Signals
Risks are signature drift from common resource interfaces or missing declarations when helper functions are referenced by other DCE generations. Build coverage is the primary signal; runtime signals come from successful DCE100 resource creation and validation callback use.

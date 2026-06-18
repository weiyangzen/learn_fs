# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/atombios_dp.h

## Purpose
This header declares the legacy ATOMBIOS DisplayPort helper interface.

## Important APIs, types, and functions
It declares AUX initialization, sink-type query, DPCD read, panel-mode query, link configuration selection, mode validation, link-train-needed check, sink power state update, and link training.

## Control flow
The header has no runtime flow. Display connector and modeset code call these functions during DP detection, validation, setup, and training.

## State and persistence behavior
No state is stored in the header. Implementations update connector private DP state, sink DPCD state, and source encoder state.

## Dependencies
The prototypes require AMDGPU connector types, DRM connector/encoder/display mode types, and fixed-width boolean/integer types in the include environment.

## Integration points
Legacy DP connector, encoder, and modeset paths include this header to bind ATOMBIOS DP behavior.

## Risks and edge cases
As a thin prototype header, include-order and signature drift are the main concerns. The API returns mixed boolean, int, and void results, so callers must know which operations can fail visibly.

## Test signals
Compile coverage plus DP detection/modeset/link-training execution validates the declarations.

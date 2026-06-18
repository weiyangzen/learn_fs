# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_colorop.h

## Purpose
`amdgpu_dm_colorop.h` is the small private header for AMD plane color-pipeline support. It shares supported colorop transfer-function masks and the pipeline initialization entry point with the rest of Display Manager.

## Important APIs, Types, And Functions
It declares the exported `u64` masks `amdgpu_dm_supported_degam_tfs`, `amdgpu_dm_supported_shaper_tfs`, and `amdgpu_dm_supported_blnd_tfs`, plus `amdgpu_dm_initialize_default_pipeline(struct drm_plane *plane, struct drm_prop_enum_list *list)`. The masks are consumed by both colorop construction and colorop atomic-state parsing.

## Control Flow
The header defines no executable control flow. The intended sequence is plane initialization calls `amdgpu_dm_initialize_default_pipeline`, then later atomic plane update code walks the generated pipeline and validates curve types using the shared masks.

## State And Persistence
It owns no state. The declarations expose immutable mask constants and a constructor that creates DRM object lifetime state elsewhere.

## Dependencies And Integration Points
It depends on DRM plane and property enum declarations being visible to consumers. Its main integration points are plane initialization code and `amdgpu_dm_color.c` colorop parsing.

## Risks
Because the masks are global constants rather than per-hardware fields, unsupported curve exposure must be handled by pipeline composition and later DC conversion. Header users must keep the function declaration in sync with DRM helper API changes and avoid including it without the relevant DRM type declarations.

## Test Signals
Compile coverage across colorop-enabled builds, successful link of the mask exports, plane pipeline enumeration, and atomic commits using every advertised mask bit are the main signals.

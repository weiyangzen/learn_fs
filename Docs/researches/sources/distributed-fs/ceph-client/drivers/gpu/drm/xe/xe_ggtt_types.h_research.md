<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ggtt_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ggtt_types.h

## Purpose
`xe_ggtt_types.h` provides forward declarations and callback typedefs for GGTT users without exposing the private `struct xe_ggtt` layout.

## Important APIs, types, and functions
It forward-declares `struct xe_ggtt` and `struct xe_ggtt_node`. `xe_ggtt_set_pte_fn` is the function signature for writing one GGTT PTE. `xe_ggtt_transform_cb` is a display/custom mapping callback receiving the GGTT, node, PTE flags, PTE writer, and caller argument.

## Control flow and integration points
There is no control flow. Transform callbacks are passed to `xe_ggtt_insert_node_transform()` to populate non-linear mappings such as display rotations or layout-specific views.

## State and persistence behavior
No state is owned here. Callback users mutate PTEs inside an allocated GGTT node owned by the implementation.

## Dependencies, risks, and test signals
Dependencies are Linux integer types and DRM MM type visibility. Risks include transform callbacks writing outside node bounds or using wrong PTE flags. Test signals include display transform mapping tests, GGTT PTE readback, and compile coverage of callback users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ggtt_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_drm_ras_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_drm_ras_types.h

## Purpose
`xe_drm_ras_types.h` defines Xe RAS state structures and a small hardware-error category enum.

## Important APIs, types, and functions
`enum hardware_error` distinguishes correctable, nonfatal, fatal, and max categories. `struct xe_drm_ras_counter` pairs a component name with an atomic counter. `struct xe_drm_ras` stores the allocated DRM RAS node array and per-severity arrays of `xe_drm_ras_counter`.

## Control flow and integration points
The header has no control flow. `xe_device_types.h` embeds `struct xe_drm_ras ras` in `struct xe_device`, while `xe_drm_ras.c` allocates nodes and counter arrays and registers them with DRM RAS.

## State and persistence behavior
Counter arrays persist for the device lifetime after RAS initialization. Counter increments are atomic so hardware error paths can update them concurrently with RAS queries.

## Dependencies, risks, and test signals
Dependencies include Linux atomics and `drm/xe_drm.h` severity/component constants. Risks include unused or mismatched `enum hardware_error`, counter-array sizing tied to UAPI values, and missing synchronization for future non-atomic fields. Test signals include counter query correctness, concurrent increment/read tests, and build checks when UAPI RAS enums change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_drm_ras_types.h -->

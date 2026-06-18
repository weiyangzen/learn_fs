# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_debugfs.h

## Purpose
`amdgpu_dm_debugfs.h` declares the Display Manager debugfs initialization hooks implemented by `amdgpu_dm_debugfs.c`.

## Important APIs, types, and functions
It exposes `connector_debugfs_init(struct amdgpu_dm_connector *connector)`, `dtn_debugfs_init(struct amdgpu_device *adev)`, and `crtc_debugfs_init(struct drm_crtc *crtc)`.

## Control flow
There is no executable control flow. DM setup calls these functions when connector, device, and CRTC debugfs roots are available.

## State and persistence behavior
The header defines no state. Runtime state is managed by the implementation and by the AMDGPU/DRM objects passed into the functions.

## Dependencies and integration points
It includes `amdgpu.h` and `amdgpu_dm.h`, providing the compile-time boundary between the wider DM driver and debugfs-specific code.

## Risks and edge cases
The main risk is signature drift with call sites. The header is unconditional while individual debugfs files are config- and hardware-dependent, so callers must not assume every debugfs entry exists.

## Test signals
Build coverage and probe-time connector/CRTC/device debugfs initialization validate this header.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/mock_drm.h

Purpose: provides tiny DRM file helpers for i915 selftests using mock DRM/GEM devices.

Important APIs/functions: `mock_file(struct drm_i915_private *i915)` obtains a `struct file *` via `mock_drm_getfile(i915->drm.primary, O_RDWR)`. `to_drm_file(struct file *f)` returns `f->private_data` as a `struct drm_file *`.

Control flow and state: no local state; the helpers bridge Linux file objects to DRM file-private data for selftests that need per-file handles.

Dependencies and integration: includes `drm_file.h` and i915 driver definitions. Integrates with DRM mock file allocation and the `drm_file` handle namespace used by GEM tests.

Risks: callers must close/drop the returned file correctly. The cast in `to_drm_file()` assumes the file came from DRM mock infrastructure.

Test signals: selftests should be able to allocate mock file contexts and use DRM handle/object APIs without a real userspace open.

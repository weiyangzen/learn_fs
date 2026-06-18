## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_sched.h

Purpose: declares scheduler priority conversion and the AMDGPU scheduler ioctl entry point.

Important APIs and types: forward-declares `enum drm_sched_priority`, `struct drm_device`, and `struct drm_file`; declares `amdgpu_to_sched_priority()` and `amdgpu_sched_ioctl()`.

Control flow: no implementation here; it establishes the interface between context priority code, DRM scheduler priority mapping, and the ioctl dispatcher.

State and persistence: none.

Dependencies and integration points: included by scheduler ioctl implementation and code needing AMDGPU-to-DRM scheduler priority conversion.

Risks: the header exposes `amdgpu_to_sched_priority()` although that function is implemented elsewhere, so signature drift would break compilation. The final `#endif` uses a C++-style comment but is harmless.

Test signals: compile coverage and ioctl/context priority tests.

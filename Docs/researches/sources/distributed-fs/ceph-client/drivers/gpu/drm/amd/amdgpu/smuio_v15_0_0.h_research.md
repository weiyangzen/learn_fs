# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v15_0_0.h

Purpose: declaration header for SMUIO v15.0.0 operations.

Important APIs, types, and functions: declares `extern const struct amdgpu_smuio_funcs smuio_v15_0_0_funcs`.

Control flow: no runtime flow.

State and persistence: no header state.

Dependencies and integration points: exposes the v15.0.0 clock-counter callback table.

Risks and test signals: build linkage and monotonic counter callback dispatch validate the header.

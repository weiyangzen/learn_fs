# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v13_0_3.h

Purpose: declaration header for SMUIO v13.0.3 operations.

Important APIs, types, and functions: declares `extern const struct amdgpu_smuio_funcs smuio_v13_0_3_funcs`.

Control flow: no runtime flow.

State and persistence: no header state.

Dependencies and integration points: makes the v13.0.3 topology callback table available to SOC setup.

Risks and test signals: build linkage plus correct die/socket/package callback dispatch validate it.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v11_0_6.h

Purpose: declaration header for SMUIO v11.0.6 operations.

Important APIs, types, and functions: declares `extern const struct amdgpu_smuio_funcs smuio_v11_0_6_funcs`.

Control flow: no runtime flow; version selection code uses the descriptor.

State and persistence: no header state.

Dependencies and integration points: integrates the v11.0.6 SMUIO table with SOC15 common code.

Risks and test signals: build linkage and correct version-table selection are the main checks.

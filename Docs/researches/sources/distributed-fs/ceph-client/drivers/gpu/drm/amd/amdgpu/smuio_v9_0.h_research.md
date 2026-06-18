# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v9_0.h

Purpose: declaration header for SMUIO v9 operations.

Important APIs, types, and functions: declares `extern const struct amdgpu_smuio_funcs smuio_v9_0_funcs`.

Control flow: no runtime flow.

State and persistence: no header state.

Dependencies and integration points: exposes v9 ROM/clock-gating callbacks to SOC15 common code.

Risks and test signals: build linkage and successful version-specific ROM/CG callback dispatch validate it.

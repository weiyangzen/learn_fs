# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v14_0_2.h

Purpose: declaration header for SMUIO v14.0.2 operations.

Important APIs, types, and functions: declares `extern const struct amdgpu_smuio_funcs smuio_v14_0_2_funcs`.

Control flow: no runtime flow.

State and persistence: no header state.

Dependencies and integration points: exposes v14.0.2 ROM and clock-counter callbacks.

Risks and test signals: build linkage and correct clock-counter dispatch validate it.

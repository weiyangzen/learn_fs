# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v15_0_8.h

Purpose: declaration header for SMUIO v15.0.8 operations.

Important APIs, types, and functions: declares `extern const struct amdgpu_smuio_funcs smuio_v15_0_8_funcs`.

Control flow: no runtime flow.

State and persistence: no header state.

Dependencies and integration points: exposes v15.0.8 SMUIO callbacks to SOC setup.

Risks and test signals: build linkage and correct dispatch of ROM, clock, and topology callbacks validate it.

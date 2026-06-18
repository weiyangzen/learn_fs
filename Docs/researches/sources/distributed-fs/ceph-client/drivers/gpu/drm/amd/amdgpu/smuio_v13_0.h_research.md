# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v13_0.h

Purpose: declaration header for SMUIO v13.0 operations.

Important APIs, types, and functions: declares `extern const struct amdgpu_smuio_funcs smuio_v13_0_funcs`.

Control flow: no runtime flow; selected by versioned SOC setup.

State and persistence: no header state.

Dependencies and integration points: exposes v13.0 SMUIO callbacks to amdgpu SOC15 code.

Risks and test signals: correct version selection and successful topology/ROM callback use validate this header link.

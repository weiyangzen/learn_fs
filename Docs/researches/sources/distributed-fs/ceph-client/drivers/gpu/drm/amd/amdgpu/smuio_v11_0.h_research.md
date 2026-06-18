# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v11_0.h

Purpose: SMUIO v11 function-table declaration header.

Important APIs, types, and functions: includes `soc15_common.h` and declares `extern const struct amdgpu_smuio_funcs smuio_v11_0_funcs`.

Control flow: no runtime flow. The descriptor is selected by SOC/IP discovery code to install version-specific SMUIO operations.

State and persistence: no state in the header; implementation reads/writes SMUIO registers.

Dependencies and integration points: exposes SMUIO v11 operations to amdgpu common SOC15 code.

Risks and test signals: build linkage catches mismatch. Runtime signal is correct ROM offset and ROM clock-gating behavior when the v11 table is selected.

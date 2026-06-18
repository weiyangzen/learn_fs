# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sienna_cichlid.h

Purpose: Sienna Cichlid reset-control public header.

Important APIs, types, and functions: includes `amdgpu.h` and declares `sienna_cichlid_reset_init()` and `sienna_cichlid_reset_fini()`.

Control flow: no runtime flow. Callers use init/fini during ASIC setup and teardown to install or remove the mode2 reset controller.

State and persistence: no state in the header; implementation allocates `adev->reset_cntl`.

Dependencies and integration points: integrates the ASIC reset implementation with common amdgpu device setup code.

Risks and test signals: declaration drift would fail builds. Runtime signal is that reset control is installed for Sienna Cichlid and released without leaking or leaving stale `adev->reset_cntl`.

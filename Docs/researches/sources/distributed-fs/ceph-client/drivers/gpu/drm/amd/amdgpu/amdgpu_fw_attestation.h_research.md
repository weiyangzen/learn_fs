# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_fw_attestation.h

## Purpose
`amdgpu_fw_attestation.h` declares the debugfs initialization hook for firmware-attestation reporting.

## Important APIs, types, and functions
It includes `amdgpu.h` and declares `amdgpu_fw_attestation_debugfs_init(struct amdgpu_device *adev)`.

## Control flow
The header has no executable control flow. Device debugfs initialization calls the declared function, which performs support checks internally.

## State and persistence behavior
No state is defined here. The implementation reads PSP-populated VRAM records on demand.

## Dependencies and integration points
It connects AMDGPU device/debugfs setup code with the firmware-attestation implementation and PSP integration.

## Risks and edge cases
The single exported hook hides support gating in the C file, so callers should not assume the debugfs file exists after calling it.

## Test signals
Build coverage and debugfs file creation/absence on supported/unsupported devices validate the header contract.

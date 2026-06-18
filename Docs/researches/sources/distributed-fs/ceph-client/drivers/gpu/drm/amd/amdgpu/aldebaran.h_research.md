<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/aldebaran.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/aldebaran.h

## Purpose
`aldebaran.h` is the public local header for Aldebaran ASIC reset support. It exposes the reset-control lifecycle entry points implemented in `aldebaran.c` and imports `amdgpu.h` for the `struct amdgpu_device` declaration and related driver types.

## Important APIs, types, and functions
- `int aldebaran_reset_init(struct amdgpu_device *adev);` allocates and installs Aldebaran reset control state.
- `int aldebaran_reset_fini(struct amdgpu_device *adev);` tears down that reset control state.
- The include guard `__ALDEBARAN_H__` prevents duplicate inclusion.

## Control flow
There is no executable control flow in this header. Compile-time flow is limited to the include guard. Runtime control enters through callers that invoke `aldebaran_reset_init()` during device setup and `aldebaran_reset_fini()` during teardown.

## State and persistence behavior
The header itself stores no state. The declared functions mutate `adev->reset_cntl` and related reset-control runtime state in the implementation. No persistent state is defined here.

## Dependencies and integration points
The header depends on `amdgpu.h`, making it part of the main amdgpu internal API surface rather than a standalone forward-declaration header. It is included by `aldebaran.c` and by ASIC setup code that wires Aldebaran reset support into the broader driver.

## Risks and edge cases
The main risk is broad include coupling. Including `amdgpu.h` pulls in many subsystem headers, so this header should stay narrow and avoid adding unrelated declarations. Prototype mismatches with `aldebaran.c` would break reset setup at compile time.

## Test signals
Compile-time success and successful call sites for `aldebaran_reset_init()`/`aldebaran_reset_fini()` are the primary signals. Runtime validation is covered through Aldebaran reset tests described for `aldebaran.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/aldebaran.h -->

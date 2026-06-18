# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v4_4.h

## Purpose
Declares the SDMA v4.4 RAS descriptor so other SDMA implementation files can attach the correct RAS operations for v4.4 hardware.

## APIs, Types, And Functions
The sole exported symbol is `extern struct amdgpu_sdma_ras sdma_v4_4_ras;`. The header defines no functions or additional types.

## Control Flow
There is no local control flow. The declaration is consumed by `sdma_v4_0.c`, which assigns `adev->sdma.ras` to this descriptor for matching IP versions.

## State And Persistence
The header is stateless. Runtime RAS state and hardware counter interaction live in `sdma_v4_4.c` and the common AMDGPU RAS core.

## Dependencies And Integration
It assumes `struct amdgpu_sdma_ras` is already declared by included AMDGPU headers. Its integration point is deliberately narrow: expose only the RAS block descriptor, not the counter decoding helpers.

## Risks And Test Signals
Risk is declaration/definition mismatch or missing inclusion when v4.4 RAS is selected. Build/link success and SDMA RAS initialization on v4.4 hardware are the practical signals.

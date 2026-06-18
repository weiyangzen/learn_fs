# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_doorbell.h

## Purpose

`amdgpu_doorbell.h` defines AMDGPU doorbell state, doorbell index assignments, and the public helpers for reading, writing, initializing, allocating, and translating doorbell offsets. Doorbells are CPU-visible MMIO or doorbell-domain BO locations used to notify GPU engines that queue write pointers or other ring state changed.

## Important APIs, types, and functions

- `struct amdgpu_doorbell` stores doorbell BAR base/size, the number of kernel-reserved doorbells, the kernel doorbell BO, and the CPU address used by the driver.
- `struct amdgpu_doorbell_index` is the normalized per-device assignment table used by graphics, compute, SDMA, MES, IH, VCN/UVD/VCE/JPEG, VPE, and user queue code.
- Assignment enums encode generation/layout-specific ranges:
  - `AMDGPU_DOORBELL_ASSIGNMENT` for older 32-bit doorbell layouts.
  - `AMDGPU_VEGA20_DOORBELL_ASSIGNMENT` for Vega20-like 64-bit layouts with SDMA/IH/media ranges and XCC/AID extensions.
  - `AMDGPU_NAVI10_DOORBELL_ASSIGNMENT` for Navi layouts including MES and graphics user queues.
  - `AMDGPU_DOORBELL64_ASSIGNMENT` for a compact 64-bit assignment map.
  - `AMDGPU_DOORBELL_ASSIGNMENT_LAYOUT1` and `AMDGPU_SOC_V1_0_DOORBELL_ASSIGNMENT` for newer multi-XCC/SOC layouts.
- `amdgpu_mm_rdoorbell()`, `amdgpu_mm_wdoorbell()`, `amdgpu_mm_rdoorbell64()`, and `amdgpu_mm_wdoorbell64()` perform 32-bit and 64-bit doorbell aperture access.
- `amdgpu_doorbell_init()`, `amdgpu_doorbell_fini()`, and `amdgpu_doorbell_create_kernel_doorbells()` manage driver doorbell resources.
- `amdgpu_doorbell_index_on_bar()` translates an index inside a doorbell BO into an absolute BAR dword index.
- `RDOORBELL32`, `WDOORBELL32`, `RDOORBELL64`, and `WDOORBELL64` are convenience macros used by ring/IP code with an in-scope `adev`.

## Control flow

ASIC setup calls an ASIC-specific doorbell index initializer that fills `adev->doorbell_index` using one of the assignment layouts. `amdgpu_doorbell_init()` establishes aperture bounds from PCI BAR2 and computes the maximum kernel doorbell range. Later `amdgpu_doorbell_create_kernel_doorbells()` allocates a doorbell-domain BO for kernel doorbells and maps it to `cpu_addr`. Ring and IP code then reads or writes doorbells through the access helpers/macros when updating queue pointers.

## State and persistence behavior

Doorbell layout state persists in `adev->doorbell_index`. Aperture and allocation state persists in `adev->doorbell`. The kernel doorbell BO pins/backs the CPU-visible doorbell area until `amdgpu_doorbell_fini()` frees it. Doorbell writes are hardware notifications rather than ordinary persisted memory semantics.

## Dependencies and integration points

The header is consumed by graphics, SDMA, MES, VCN/JPEG, IH, user queue, VPE, NBIO, and ring code. It relies on `struct amdgpu_device`, `struct amdgpu_bo`, and generation-specific initialization code elsewhere to populate assignments correctly.

## Risks and edge cases

- Assignment constants are hardware contracts. Off-by-one ranges or using a 32-bit index where a 64-bit/QWORD index is expected can notify the wrong engine.
- Several media assignments intentionally overlap because engines are mutually exclusive on a given ASIC; consumers must select the right semantic layout.
- New multi-XCC layouts require correct per-XCC ranges for KIQ/KCQ and user queues.
- The 64-bit access helpers operate on `cpu_addr + index` cast to `atomic64_t *`; callers must pass an index aligned to the layout's 64-bit convention.
- The convenience macros require a local variable named `adev`, so they are unsuitable for contexts without that convention.

## Test signals

Signals include successful ring tests for graphics/compute/SDMA/MES/media, no "beyond doorbell aperture" logs, correct queue write-pointer advancement, SR-IOV and multi-XCC queue bring-up, user queue doorbell allocation tests, and suspend/resume/reset tests that prove doorbell BOs are recreated and mapped correctly.

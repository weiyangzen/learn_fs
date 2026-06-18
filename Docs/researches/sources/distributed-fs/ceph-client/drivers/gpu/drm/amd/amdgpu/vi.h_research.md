# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vi.h

## Purpose
`vi.h` is the public local header for the AMDGPU VI common implementation. It exposes the VI-specific setup and selection helpers used by other AMDGPU components while keeping the large implementation details in `vi.c`.

## Important APIs, Types, And Functions
The header defines `VI_FLUSH_GPU_TLB_NUM_WREG` as the number of write-register operations needed for a VI GPU TLB flush sequence. It declares `vi_srbm_select()`, `vi_set_virt_ops()`, `vi_set_ip_blocks()`, and `legacy_doorbell_index_init()`.

## Control Flow
Other VI-era blocks include this header when they need to select an SRBM register instance, install virtualization operations, populate the device IP block list, or initialize legacy doorbell indices. The implementation is called during device discovery and IP block setup.

## State And Persistence
This header itself owns no state. Its declared functions mutate `amdgpu_device` hardware and software state in `vi.c`, including SRBM selection registers, virtual operation tables, IP block lists, and doorbell index assignments.

## Dependencies And Integration Points
It depends on the including translation unit already knowing `struct amdgpu_device` and `u32`. It integrates VI common code with GFX, KIQ, VM/TLB, virtualization, and device initialization paths.

## Risks
The file has low direct risk, but it is an ABI-like internal contract: changing declarations, the TLB write-count constant, or doorbell helper name can break multiple VI-generation source files. The include guard name `__VI_H__` differs from `vid.h`'s `VI_H`, avoiding a direct collision.

## Test Signals
Compile coverage is the primary signal. Runtime signals come indirectly from VI probe, SRBM-indexed register access, KIQ/TLB flush paths using the constant, and queue doorbell operation after `legacy_doorbell_index_init()`.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc24.h

## Purpose

`soc24.h` exposes the minimal SOC24 common interface to the rest of AMDGPU. It declares the common IP block and the GRBM selector implemented in `soc24.c`.

## Important APIs, Types, And Functions

`soc24_common_ip_block` is inserted into the AMDGPU IP block list for supported SOC24 devices. `soc24_grbm_select(struct amdgpu_device *adev, u32 me, u32 pipe, u32 queue, u32 vmid)` programs the active graphics engine/pipe/queue/VMID selection for register accesses that depend on GRBM context.

## Control Flow And State

No code runs from this header. It creates compile-time linkage between common AMDGPU setup code and the SOC24 implementation. State changes occur when the declared GRBM selector writes hardware registers or when the common IP block lifecycle callbacks in `soc24.c` are invoked.

## Dependencies, Risks, And Test Signals

The header relies on AMDGPU core type declarations. The risk is selecting this helper for hardware that needs a different GRBM addressing model, such as per-XCC shadowed GRBM writes. Build coverage, graphics/compute queue selection, and ring tests on SOC24 devices validate the declarations.

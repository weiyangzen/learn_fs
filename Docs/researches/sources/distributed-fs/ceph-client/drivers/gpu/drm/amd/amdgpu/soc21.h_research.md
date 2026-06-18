# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc21.h

## Purpose

`soc21.h` is the narrow public header for the SOC21 common block. It declares the `soc21_common_ip_block` exported by `soc21.c` and the `soc21_grbm_select()` helper used by graphics code to select ME, pipe, queue, and VMID context through GRBM.

## Important APIs, Types, And Functions

`soc21_common_ip_block` plugs SOC21 common behavior into AMDGPU's IP block list. `soc21_grbm_select(struct amdgpu_device *adev, u32 me, u32 pipe, u32 queue, u32 vmid)` writes the GRBM graphics control register using SOC21 register naming and does not expose an XCC parameter, unlike some multi-XCC SOC15/SOC v1 helpers.

## Control Flow And State

The header has no runtime behavior. Its declarations are used during IP block assembly and by code that needs GRBM queue selection. The actual state changes occur in `soc21.c`, where GRBM writes affect hardware register state and the common IP block mutates `adev` lifecycle state.

## Dependencies, Risks, And Test Signals

Consumers must include AMDGPU core types before using the prototypes. The main risk is calling the SOC21 GRBM selector on hardware that requires per-XCC selection or RLC shadowing semantics not represented by this prototype. Compile coverage, graphics ring tests, and queue/VMID selection tests on SOC21 hardware are the relevant signals.

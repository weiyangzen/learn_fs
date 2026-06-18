# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vpe.h

## Purpose

This header defines the AMDGPU VPE state object, hardware callback interface, register cache, exported helper APIs, and IP block declaration for VPE v6.1 support.

## Important APIs, types, and functions

`AMDGPU_MAX_VPE_INSTANCES` caps supported instances. `struct vpe_funcs` declares hardware-specific callbacks for register offsets, register setup, IRQ init, firmware init/load, and ring lifecycle. `struct vpe_regs` caches register offsets used by common code. `struct amdgpu_vpe` contains the ring, trap IRQ source, function table, register table, firmware metadata, command buffer BO/GPU/CPU addresses, idle delayed work, context state, instance count, collaborate-mode flag, and supported reset mask. Public APIs include VPE firmware, ring, DPM, and sysfs helpers. Convenience macros call optional function pointers with zero defaults.

## Control flow, state, and persistence behavior

The header itself does not run code. It defines how common VPE code delegates ASIC-specific behavior through `vpe_funcs` while keeping shared ring, firmware, idle-work, and reset state in `struct amdgpu_vpe`. State exists for the life of the AMDGPU device and is initialized/freed by `amdgpu_vpe.c`.

## Dependencies and integration points

It depends on AMDGPU ring and IRQ types plus `vpe_6_1_fw_if.h`. The declared `vpe_v6_1_ip_block` is consumed by AMDGPU IP discovery/init code, and hardware-specific files fill `vpe_funcs`.

## Risks and test signals

Risks are mostly interface drift: common code assumes callbacks are present or safely optional, register offsets are initialized before use, and firmware metadata matches the included interface. Test signals are compile coverage across supported VPE IP versions, successful early init callback installation, and ring/sysfs paths working when optional callbacks are absent.

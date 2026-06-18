# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gfxhub.h

## Purpose
`amdgpu_gfxhub.h` defines the small function-table wrapper for graphics VM hub operations. The gfxhub is the GC-side VM/GART integration point used by generation-specific code to set up page-table registers, enable the GART, handle faults, query XGMI information, and preserve/restore mode2 state.

## Important APIs, types, and functions
The central type is `struct amdgpu_gfxhub_funcs`, with hooks for `get_fb_location`, `get_mc_fb_offset`, `setup_vm_pt_regs`, `gart_enable`, `gart_disable`, `set_fault_enable_default`, `init`, `get_xgmi_info`, `utcl2_harvest`, `mode2_save_regs`, `mode2_restore_regs`, and `halt`. `struct amdgpu_gfxhub` stores the installed function table.

## Control flow
The header has no executable logic. Common GMC/GART and ASIC initialization code call the function pointers after the specific gfxhub version has installed its implementation.

## State and persistence behavior
The only state represented here is a pointer to constant function tables. Hardware register state manipulated by the functions is runtime state and is restored by generation-specific mode2 save/restore helpers when supported.

## Dependencies and integration points
It depends on `struct amdgpu_device` and is consumed by GMC/GFX hub implementations. It integrates with VM page-table setup, GART lifecycle, XGMI discovery, UTCL2 harvest configuration, VM fault policy, and reset/halt flows.

## Risks and edge cases
Missing function pointers can break bring-up on an IP version if callers assume hooks are present. The table abstracts hardware-specific register layouts, so wrong implementations can misprogram VMID page-table bases or fault policy.

## Test signals
GART enable/disable, VM page-table register programming, VM fault enable defaults, XGMI information reporting, mode2 reset save/restore, and UTCL2 harvest tests validate this contract.

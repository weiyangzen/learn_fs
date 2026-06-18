# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_cmd.c

## Purpose

`amdgpu_ras_cmd.c` implements AMDGPU-specific RAS command handling on top of the generic `rascore` command dispatcher. It validates and prepares error injection, reports safe framebuffer ranges, translates framebuffer addresses, routes VF commands to the virtualization path, and waits for reset-safe command execution.

## Important APIs, Types, And Functions

Public functions are `amdgpu_ras_handle_cmd()` and `amdgpu_ras_submit_cmd()`. Static handlers are `amdgpu_ras_inject_error`, `amdgpu_ras_get_ras_safe_fb_addr_ranges`, and `amdgpu_ras_translate_fb_address`, mapped in `amdgpu_ras_cmd_maps`. Helper flow includes XGMI-specific power policy preparation/restoration, local-to-global XGMI address conversion, and bank/SOC physical address translation through rascore UMC helpers.

## Control Flow, State, And Persistence

Submission initializes `cmd_res` and `output_size`, sends VF commands to `amdgpu_virt_ras_handle_cmd`, rejects disabled rascore access, waits up to 60 seconds while the GPU is in reset, tries AMDGPU-local handlers, falls back to `rascore_handle_cmd`, records `cmd_res`, and validates output size. UMC injection rejects already retired addresses, out-of-VRAM or above-52-bit addresses, converts multi-node XGMI addresses, temporarily disables XGMI power-down for XGMI injections, and restores policy unless an interrupt was triggered.

## Dependencies And Integration Points

The file depends on AMDGPU RAS manager state, XGMI topology, DPM policy APIs, SR-IOV virtualization command handling, rascore command structs, and UMC translation routines. It is the manager-side command bridge used by ioctl or internal callers through `amdgpu_ras_mgr_handle_ras_cmd`.

## Risks And Test Signals

Risks include accepting malformed `input_size`, failing to restore XGMI/DF policies, racing reset state, copying output only on exact size match in callers, and address translation mistakes on multi-node systems. Test signals include injection command tests for UMC/GFX/XGMI, invalid address rejection, retired-address rejection, reset-wait timeout, VF command routing, safe range output for memory partitions, and SOC-to-bank translation round trips.

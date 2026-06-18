# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmmcp77.c

## Purpose
Defines MCP77 VMM behavior as a small NV50-derived variant with reduced page capability flags.

## Important APIs, Types, And Functions
Exports `mcp77_vmm_new`. The local function table uses `nv50_vmm_join`, `nv50_vmm_part`, `nv50_vmm_valid`, `nv50_vmm_flush`, and NV50 descriptor arrays.

## Control Flow
Construction delegates to `nv04_vmm_new_` with the MCP77 function table. Runtime mapping and flush behavior is inherited from NV50.

## State And Persistence
No local state exists. Persistent VM state is NV50 page-directory entries written into joined instance memory and NV50 page tables.

## Dependencies And Integration Points
Depends on NV50 VMM exports and the generic NV04 VMM constructor wrapper. It is selected for MCP77 chipset MMU setup.

## Risks And Test Signals
Risk lies in page flag differences from full NV50, especially lack of compression on the 16-bit page entry. Test host/VRAM mappings, 4 KiB and 64 KiB style pages, and inherited NV50 TLB flush paths on MCP77 hardware.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmnv50.c

## Purpose
Implements NV50/G8x VMM support with block-encoded PTE runs, page-directory entries mirrored into joined instance memory, kind/compression validation, and engine-specific TLB flushing.

## Important APIs, Types, And Functions
Exports descriptor arrays `nv50_vmm_desc_12`, `nv50_vmm_desc_16`, and functions `nv50_vmm_flush`, `nv50_vmm_valid`, `nv50_vmm_part`, `nv50_vmm_join`, `nv50_vmm_new`. Internal helpers cover PTE writes, DMA/SGL/mem map, PDE encoding, and PGD update.

## Control Flow
`nv50_vmm_pgt_pte` groups aligned PTE runs by power-of-two block size and stores the block log in bits 7+. `nv50_vmm_pgd_pde` updates every joined instance when a PDE changes. Validation unpacks `if500d` args, maps memory targets to aperture bits, checks kind table compatibility with bankswizzle, allocates compression tags when requested, and sets final PTE type bits. Flush iterates `vmm->engref[]`, uses GR-specific TLB flush when available, otherwise writes per-engine invalidate IDs to `0x100c80`.

## State And Persistence
State includes page tables, joined instance list nodes, compression tag allocations, and engine reference counters. `nv50_vmm_part` removes one joined instance from the list.

## Dependencies And Integration Points
Depends on FB RAM metadata, GR engine flush hooks, timer polling, NVIF `if500d`, and NVKM kind/compression tag APIs. MCP77 reuses these descriptors and operations.

## Risks And Test Signals
Risks include block-run alignment bugs, stale joined instance PDEs, compression tag math, unsupported bankswizzle kinds, and engine invalidate timeouts. Test page ranges with varied alignment, multi-channel joins, GR and non-GR engine flushes, compressed surfaces, stolen-memory aperture handling, and suspend/resume.

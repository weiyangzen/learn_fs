# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmnv41.c

## Purpose
Implements NV41-era host-page VMM support with 32-bit PTE encodings and an explicit MMU flush sequence.

## Important APIs, Types, And Functions
Exports `nv41_vmm_new`. Internal helpers are `nv41_vmm_pgt_{pte,sgl,dma,unmap}` and `nv41_vmm_flush`.

## Control Flow
PTEs encode `(addr >> 7) | VALID` and advance by `0x20` for 4 KiB pages. The fast DMA path writes shifted DMA addresses when PAGE_SHIFT is 12. Flush locks the MMU mutex, writes `0x100810`, polls for bit `0x20`, then clears the register.

## State And Persistence
State is page-table memory and hardware TLB state. No join or private state is defined locally; construction uses `nv04_vmm_new_`.

## Dependencies And Integration Points
Depends on `subdev/timer.h` and NV04 validation. It integrates with NV4x chipset MMU factory selection.

## Risks And Test Signals
Risks include address shift mistakes, missing flush completion handling, and PAGE_SHIFT-specific DMA behavior. Test SGL/DMA mappings, unmap, repeated flushes, and timeout logging on NV41-class devices.

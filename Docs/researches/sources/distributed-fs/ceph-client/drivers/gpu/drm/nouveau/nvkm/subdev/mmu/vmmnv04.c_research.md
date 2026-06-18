# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmnv04.c

## Purpose
Implements the earliest NV04 VMM page table backend and shared constructor wrapper for older nouveau VMM implementations.

## Important APIs, Types, And Functions
Exports `nv04_vmm_valid`, `nv04_vmm_new_`, and `nv04_vmm_new`. Internal helpers write 32-bit PTEs with present/RW bits and support SGL, DMA, and unmap callbacks through `nv04_vmm_desc_pgt`.

## Control Flow
Mapping emits 32-bit PTEs at an 8-byte page-directory header offset. The fast DMA path writes DMA addresses directly when PAGE_SHIFT is 12; otherwise iterator macros handle larger base-page systems. `nv04_vmm_new` calls `nv04_vmm_new_`, then writes the legacy page-directory header with PCI/RW/PT flags and limit.

## State And Persistence
Persistent state is the PGT memory and the two-word PD header. Argument validation only accepts the unversioned NVIF form and stores no local runtime state.

## Dependencies And Integration Points
Uses `nvif/if000d.h`, `nvif_unvers`, and generic NVKM VMM allocation. Many later files reuse `nv04_vmm_new_` as a constructor wrapper even when their descriptors differ.

## Risks And Test Signals
Risks include header-offset mistakes, 32-bit address truncation, PAGE_SHIFT conditional behavior, and legacy argument parsing. Test old NV04/NV10 mappings, DMA/SGL input, unmap, and VM limits written into the PD header.

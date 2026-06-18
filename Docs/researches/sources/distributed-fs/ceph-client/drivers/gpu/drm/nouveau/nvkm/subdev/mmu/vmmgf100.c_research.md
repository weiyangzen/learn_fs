# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmgf100.c

## Purpose
Implements the GF100/Fermi-generation NVKM virtual memory manager backend. It defines 4 KiB and large-page page-table descriptors, PTE/PDE writers, map validation, compression tag setup, MMU invalidate/flush, VM instance join/part handling, and constructor dispatch based on framebuffer big-page size.

## Important APIs, Types, And Functions
Key exported helpers include `gf100_vmm_pgt_{sgl,dma,mem,unmap}`, `gf100_vmm_pgd_pde`, `gf100_vmm_invalidate`, `gf100_vmm_flush`, `gf100_vmm_valid`, `gf100_vmm_aper`, `gf100_vmm_part`, `gf100_vmm_join_`, `gf100_vmm_join`, `gf100_vmm_new_`, and `gf100_vmm_new`. The file exports descriptor functions `gf100_vmm_pgt` and `gf100_vmm_pgd`; later generation files reuse them heavily. Descriptors cover either 16-bit or 17-bit large pages and 12-bit small pages.

## Control Flow
Mapping flows through NVKM iterator macros into `gf100_vmm_pgt_pte`, which encodes address, aperture, kind, access flags, volatility, and optional compression tags into 64-bit PTEs. `gf100_vmm_valid` unpacks versioned NVIF map arguments, validates kind indexes through the MMU kind table, allocates/clears compression tags when required, and prepares `map->type`, `map->next`, and `map->ctag`. Join writes the page-directory pointer and limit into the instance block. Flush serializes on the MMU mutex, optionally writes a PDB target, and commands register `0x100cbc`.

## State And Persistence
Persistent state is hardware page-table memory, instance memory at offsets `0x0200/0x0208`, compression tag allocations in `map->tags`, and hardware TLB/cache state. The MMU mutex protects invalidate sequencing. `map->type` is mutated during DMA and compression handling, so callers rely on NVKM map lifecycle discipline.

## Dependencies And Integration Points
Depends on `vmm.h`, framebuffer page-size selection, LTC compression tags, timer polling, `nvif/if900d.h`, `nvif_unpack`, and NVKM memory target APIs. Constructors are wired from chip-specific MMU factory tables. Later GK104/GM200/GP100/GV100/TU102/GH100 code reuses this file's descriptor and instance helpers.

## Risks And Test Signals
Risk is high around bit encodings: address shifts, VOL/RO/PRIV bits, aperture values, compression-kind remapping, and the `ALL_PDB`/`HUB_ONLY` invalidate flags. Test by mapping VRAM/HOST/NCOH memory with 4 KiB and large pages, compressed and uncompressed kinds, BAR mappings, repeated map/unmap, suspend/resume, and GPU fault/invalidate stress. Build coverage should catch exported-symbol drift in generation-specific users.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmgh100.c

## Purpose
Adds GH100/Hopper virtual-memory support using NVIDIA MMU version 3 register-field definitions. It provides VER3 PTE/PDE encoding, sparse/invalid entries, 128-bit dual-PDE handling, deep multi-level descriptors, and a GH100 constructor that uses the GP100 VMM creation path.

## Important APIs, Types, And Functions
Important functions include `gh100_vmm_pgt_pte`, `gh100_vmm_pgt_{sgl,dma,mem,sparse}`, `gh100_vmm_lpt_invalid`, `gh100_vmm_pd0_{pte,mem,pde,sparse,unmap}`, `gh100_vmm_pd1_pde`, `gh100_vmm_pde`, `gh100_vmm_valid`, and `gh100_vmm_new`. The `gh100_vmm` function table uses `gv100_vmm_join`, `gf100_vmm_part`, `gf100_vmm_aper`, `gp100_vmm_valid`, `gh100_vmm_valid` as `valid2`, and `tu102_vmm_flush`.

## Control Flow
Mapping emits raw physical addresses ORed with `map->type`; no GF100-style right shift is used. DMA fast path writes direct VER3 PTEs for PAGE_SHIFT mappings, while iterator paths handle SGL and memory-backed maps. PDE creation calls `gh100_vmm_pde` to translate NVKM memory targets into VER3 aperture and PCF fields, then writes either 64-bit single PDEs or 128-bit dual PDEs.

## State And Persistence
The file persists page tables in MMU-managed memory and instance state through reused GV100/GP100 helpers. Sparse entries persist with explicit VER3 PCF encodings. `map->type` stores validity, aperture, PCF, and kind; `map->next` is page-size bytes.

## Dependencies And Integration Points
Uses `nvhw/drf.h` and `nvhw/ref/gh100/dev_mmu.h` for field-safe encodings. Integrates with GP100 fault replay/cancel method parsing, TU102 flush registers, and GV100 instance layout. This file is a generation bridge from nouveau's generic VMM API to Hopper MMU format.

## Risks And Test Signals
Risks include incorrect VER3 PCF selection for RO/privileged/volatile memory, ATS permission mismatch, 128-bit PDE alignment, sparse encodings, and deep address-level descriptors for 56/47/38/29/21/16/12-bit pages. Test with system coherent and noncoherent memory, sparse mappings, large-page mappings, BAR flushes, replayable faults, and build checks against GH100 nvhw headers.

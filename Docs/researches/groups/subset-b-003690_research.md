# subset-b-003690 Research

This grouped report covers the requested nouveau NVKM MMU, MXM, PCI, and PMU files. Each file section is bounded by the exact reconciliation markers for later source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmgf100.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmgf100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmgh100.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmgh100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmgk104.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmgk104.c

## Purpose
Defines GK104/Kepler VMM descriptors by reusing GF100 PTE/PDE logic and adding an LPT invalidation encoding for large-page shadow PTEs.

## Important APIs, Types, And Functions
Exports `gk104_vmm_lpt_invalid`, descriptor arrays `gk104_vmm_desc_17_12`, `gk104_vmm_desc_17_17`, `gk104_vmm_desc_16_12`, `gk104_vmm_desc_16_16`, and constructor `gk104_vmm_new`. The local `gk104_vmm_lpt` descriptor supplies `.invalid`, `.unmap`, and `.mem`.

## Control Flow
The constructor delegates to `gf100_vmm_new_`, selecting 16-bit or 17-bit big-page tables according to framebuffer configuration. Mapping and flushing are entirely through GF100 helpers; only invalid LPT entries differ, using `VALID_FALSE + PRIV` to make the MMU ignore corresponding small-page entries.

## State And Persistence
State lives in GF100-style page tables and instance memory. The file defines no private runtime state; it selects page descriptors and supported page flags for GK104.

## Dependencies And Integration Points
Depends on `vmm.h` declarations and GF100 exported functions. GM20B and GK20A also reuse these descriptor arrays. It integrates into the MMU factory for Kepler-class GPUs.

## Risks And Test Signals
The main risk is descriptor mismatch between big-page size and LPT/SPT layout, causing invalid entries to be interpreted as real mappings. Test 16/17-bit big-page hardware, small-page fallback, sparse/invalid large-page holes, and compile-time consumers of exported descriptor arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmgk104.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmgk20a.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmgk20a.c

## Purpose
Provides the Tegra GK20A VMM function tables. It narrows the aperture model for integrated GPU memory and reuses GK104/GF100 descriptors and operations.

## Important APIs, Types, And Functions
Exports `gk20a_vmm_aper` and `gk20a_vmm_new`. It defines two `nvkm_vmm_func` tables for 16-bit and 17-bit big pages, using `gf100_vmm_join`, `gf100_vmm_part`, `gf100_vmm_valid`, `gf100_vmm_flush`, and `gf100_vmm_invalidate_pdb`.

## Control Flow
`gk20a_vmm_aper` accepts only `NVKM_MEM_TARGET_NCOH`, returning aperture 0, but the function tables currently reference `gf100_vmm_aper`, so the local aperture helper is available to related mobile variants rather than used by `gk20a_vmm_new` itself. Construction delegates to `gf100_vmm_new_`.

## State And Persistence
No local state is stored. Page tables and instance memory follow the GF100/GK104 layout, with supported page flags emphasizing host/noncoherent integrated-memory mappings.

## Dependencies And Integration Points
Depends on `core/memory.h`, GK104 descriptor arrays, and GF100 helper exports. It is selected by platform-specific MMU construction for GK20A-class chips.

## Risks And Test Signals
The notable risk is aperture-policy drift: if code expects `gk20a_vmm_aper` but the table uses `gf100_vmm_aper`, invalid memory targets may be accepted. Test integrated-memory mappings, NCOH-only paths, 4 KiB and large-page mappings, and build warnings for unused/local aperture behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmgk20a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmgm200.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmgm200.c

## Purpose
Implements GM200/Maxwell VMM descriptors with sparse mapping support, selectable 16/17-bit big pages from NVIF arguments, and instance join bits for 64 KiB page mode.

## Important APIs, Types, And Functions
Exports sparse helpers `gm200_vmm_pgt_sparse` and `gm200_vmm_pgd_sparse`, descriptor arrays `gm200_vmm_desc_*`, join helpers `gm200_vmm_join_` and `gm200_vmm_join`, constructors `gm200_vmm_new_`, `gm200_vmm_new`, and `gm200_vmm_new_fixed`.

## Control Flow
The descriptor functions wrap GF100 PTE/PDE writers and add `.sparse` callbacks for SPT/LPT/PGD. `gm200_vmm_new_` unpacks `gm200_vmm_v0.bigpage`; valid values 16 and 17 choose the matching function table, while unversioned arguments default to 17. `gm200_vmm_new_fixed` instead delegates to framebuffer page-size selection through `gf100_vmm_new_`.

## State And Persistence
State is GF100-style page tables plus sparse entries marked with `VOL` or `VOL_BIG`. Join writes instance state and sets bit 11 when the selected page table has 16-bit large pages. No heap state is allocated locally.

## Dependencies And Integration Points
Depends on GF100/GK104 functions, NVIF `ifb00d` argument formats, and nouveau sparse-page flags. GM20B reuses its descriptors and constructor helper.

## Risks And Test Signals
Risks include invalid `bigpage` argument rejection, inconsistent fixed versus requested big-page selection, sparse encoding mistakes, and missing bit 11 in VM instance state. Test both 16 and 17 modes, sparse buffers, compressed mappings, old clients with unversioned args, and large BAR mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmgm200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmgm20b.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmgm20b.c

## Purpose
Defines GM20B/Tegra Maxwell VMM function tables. It reuses GM200 sparse descriptors while applying the GK20A aperture policy and mobile page capability flags.

## Important APIs, Types, And Functions
Exports `gm20b_vmm_new` and `gm20b_vmm_new_fixed`. Local 16-bit and 17-bit function tables use `gm200_vmm_join`, `gk20a_vmm_aper`, `gf100_vmm_valid`, and `gf100_vmm_flush`.

## Control Flow
`gm20b_vmm_new` delegates to `gm200_vmm_new_`, allowing NVIF-selected big-page mode. `gm20b_vmm_new_fixed` delegates to `gf100_vmm_new_`, deriving the page mode from the framebuffer page configuration. Both tables support 27-bit sparse levels plus 16/17-bit and 12-bit pages.

## State And Persistence
The file stores no local state. Page-table state follows GM200 layouts; aperture state is constrained through `gk20a_vmm_aper`.

## Dependencies And Integration Points
Depends on GM200 descriptors and GK20A aperture behavior. It is used by mobile/Tegra MMU setup where system memory and noncoherent mappings differ from discrete GPUs.

## Risks And Test Signals
Risks include accepting unsupported VRAM/system-coherent targets, choosing the wrong constructor mode, and sparse entry handling on integrated GPUs. Test NCOH mappings, NVIF bigpage selection, sparse maps, and fixed constructor paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmgm20b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmgp100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmgp100.c

## Purpose
Implements GP100/Pascal VMM support, including MMU version 2 PTE/PDE encoding, sparse entries, PFN mapping with DMA map/unmap bookkeeping, compression tag line handling, replayable fault control methods, 64-bit PDB invalidation, and VMM construction with optional fault replay.

## Important APIs, Types, And Functions
Exports `gp100_vmm_desc_16`, `gp100_vmm_desc_12`, `gp100_vmm_valid`, `gp100_vmm_mthd`, `gp100_vmm_invalidate_pdb`, `gp100_vmm_flush`, `gp100_vmm_join`, `gp100_vmm_new_`, and `gp100_vmm_new`. Internal helpers cover PFN map/clear/unmap for 4 KiB and 2 MiB entries, sparse/invalid entries, 128-bit dual PDE writes, comptag calculations, and fault replay/cancel.

## Control Flow
Validation unpacks `gp100_vmm_map_v0` or unversioned args, optionally delegates to `valid2` for GH100, validates kind indexes, and configures compression behavior only when GSP-RM initialized the compbit store. Mapping uses `(addr >> 4)` encodings, and PFN mappings call DMA API for system pages. Fault cancel pauses GR context switching, compares the current instance, and sends a targeted invalidate; replay sends a global replay invalidate.

## State And Persistence
State includes page-table memory, DMA mappings created from PFN maps, `vmm->replay`, instance control bits for VER2/64KiB/fault replay, compression tag-line increments, and hardware fault/TLB state. `pfn_clear` invalidates valid DMA-backed entries before unmap.

## Dependencies And Integration Points
Depends on Linux DMA APIs, `engine/gr.h`, GF100 helpers, NVIF `ifc00d` method formats, and GSP-RM compression availability. GV100, TU102, GP10B, and GH100 reuse GP100 descriptors and constructors.

## Risks And Test Signals
Risks include DMA mapping leaks, PFN address shift mistakes, stale valid bits after `pfn_clear`, incorrect fault instance translation, compression exposure without GSP-RM, and 128-bit PDE partial writes. Test PFN VRAM/system mappings, sparse pages, GSP/non-GSP compression, fault replay/cancel, BAR-only flushes, context-switch pause/resume failure paths, and IOMMU-enabled systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmgp100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmgp10b.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmgp10b.c

## Purpose
Defines GP10B/Tegra Pascal VMM support by reusing GP100 descriptors and methods with GK20A aperture restrictions and host-oriented page flags.

## Important APIs, Types, And Functions
Exports `gp10b_vmm_new`. The local function table uses `gp100_vmm_join`, `gf100_vmm_part`, `gk20a_vmm_aper`, `gp100_vmm_valid`, `gp100_vmm_flush`, `gp100_vmm_mthd`, and `gp100_vmm_invalidate_pdb`.

## Control Flow
Construction delegates to `gp100_vmm_new_`, retaining GP100 argument parsing and optional fault replay state. Page descriptors expose high-level sparse address levels and 21/16/12-bit host page mappings.

## State And Persistence
No local state is allocated. Persistent state is GP100-format page tables and instance memory, with aperture behavior limited by the integrated GPU memory model.

## Dependencies And Integration Points
Depends on `vmm.h`, GK20A aperture helper, GP100 descriptors, and GP100 method handling. It integrates with platform-specific Pascal mobile MMU creation.

## Risks And Test Signals
Risks are incorrect aperture acceptance, fault replay behavior on mobile hardware, and descriptor mismatch for host-only pages. Test NCOH/system memory maps, sparse mappings, replay/cancel methods, and BAR flush paths on GP10B platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmgp10b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmgv100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmgv100.c

## Purpose
Provides GV100/Volta VMM support, primarily by extending GP100 instance join setup with additional per-entry page-directory base replication state.

## Important APIs, Types, And Functions
Exports `gv100_vmm_join` and `gv100_vmm_new`. The local `gv100_vmm` table uses GP100 descriptors, validation, flush, method handling, and PDB invalidation.

## Control Flow
`gv100_vmm_join` first performs `gp100_vmm_join`, then reads the instance PDB pointer from `0x200/0x204`, clears offset `0x21c`, populates 64 replicated entries at `0x2a0/0x2a4/0x2a8`, and writes a mask at `0x298/0x29c`. Only bit 0 is enabled in the current mask.

## State And Persistence
Persistent state is written to the GPU instance block after normal GP100 join state. No additional heap state is owned by the file.

## Dependencies And Integration Points
Depends on GP100 descriptors, GF100 part/aper helpers, and NVKM instance memory write helpers. TU102 and GH100 reuse `gv100_vmm_join`.

## Risks And Test Signals
Risks include wrong instance offsets, stale replicated PDB entries, mask mismatch, and failure to preserve GP100 join bits for replay/64 KiB mode. Test VM bind/unbind, multi-engine use, BAR mappings, replay faults, and suspend/resume across GV100-class hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmgv100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmmcp77.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmmcp77.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmnv04.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmnv04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmnv41.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmnv41.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmnv44.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmnv44.c

## Purpose
Implements NV44 packed-page-table VMM support. Four 27-bit page-frame entries are packed across four 32-bit words, with dummy-page fill for unmapped entries.

## Important APIs, Types, And Functions
Exports `nv44_vmm_new`. Internal helpers include `nv44_vmm_pgt_fill`, `nv44_vmm_pgt_{pte,sgl,dma,unmap}`, and `nv44_vmm_flush`.

## Control Flow
`nv44_vmm_pgt_fill` read-modify-writes a four-entry group so partial updates preserve neighboring PTEs. Full groups are written directly. Unmap fills entries with `vmm->null`, allocated as a 16 KiB coherent dummy page during construction if possible. Flush writes limit and command registers at `0x100814`/`0x100808`, polls, then clears the command.

## State And Persistence
Persistent state includes packed PGT words, a coherent dummy-page allocation (`vmm->nullp`/`vmm->null`), and hardware TLB state. Dummy allocation failure degrades to null address zero with a warning.

## Dependencies And Integration Points
Depends on NV04 validation, timer polling, DMA coherent allocation, and generic VMM destructor ownership of `vmm->nullp` if present. It is selected for NV44-style host-only page tables.

## Risks And Test Signals
Risks include partial group corruption, off-by-one loop behavior in unmap, dummy-page allocation failure, and packed bitfield errors. Test unaligned PTE ranges, ranges crossing four-entry groups, unmap holes, PAGE_SHIFT variants, and flush timeout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmnv44.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmnv50.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmnv50.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmtu102.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmtu102.c

## Purpose
Defines TU102/Turing VMM support by reusing GV100/GP100 page-table logic with a different MMU flush register sequence.

## Important APIs, Types, And Functions
Exports `tu102_vmm_flush` and `tu102_vmm_new`. The local function table uses `gv100_vmm_join`, `gf100_vmm_part`, `gf100_vmm_aper`, `gp100_vmm_valid`, `gp100_vmm_mthd`, and GP100 descriptor arrays.

## Control Flow
Flush constructs a PAGE_ALL invalidate type and, for BAR mappings, adds HUB_ONLY and ALL_PDB. It writes the PDB base to `0xb830a0`, clears high bits at `0xb830a4`, triggers `0xb830b0`, and polls until bit 31 clears. If RM provided `vmm->rm.bar2_pdb`, that PDB overrides the normal page directory.

## State And Persistence
Persistent state is GP100/GV100 page-table and instance memory plus Turing flush hardware state. No local heap state is introduced.

## Dependencies And Integration Points
Depends on `subdev/timer.h`, GP100 descriptors/methods, and GV100 join state. GH100 also uses this flush path.

## Risks And Test Signals
Risks include incorrect BAR2 PDB selection, flush timeout, overly broad ALL_PDB invalidation, and mismatch with GP100 descriptor assumptions. Test BAR mappings, RM-provided BAR2 PDB, replay fault paths, sparse/large pages, and repeated map/unmap under engine load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmtu102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mxm/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mxm/Kbuild

## Purpose
Adds the MXM subdevice objects to the NVKM build: `base.o`, `mxms.o`, and `nv50.o`.

## Important APIs, Types, And Functions
The build file is declarative. It ensures the core MXM constructor, MXM-SIS parser, and NV50 DCB sanitization logic are linked into the nouveau NVKM object set.

## Control Flow
There is no runtime control flow in this file. Build-time control is a straight `nvkm-y +=` object list.

## State And Persistence
No state is stored. Its persistence effect is build graph membership.

## Dependencies And Integration Points
Integrates with the kernel Kbuild system and the surrounding nouveau `nvkm-y` aggregation. Removing an object here would break MXM symbol availability.

## Risks And Test Signals
Risk is missing object linkage or stale source list after adding/removing MXM files. Test by building nouveau with MXM enabled paths and checking unresolved symbols for `nvkm_mxm_new_`, `mxms_*`, and `nv50_mxm_new`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mxm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mxm/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mxm/base.c

## Purpose
Constructs the NVKM MXM subdevice and locates a valid MXM System Information Structure from ROM/I2C, ACPI DSM, or ACPI WMI. It decides whether later DCB sanitization should run.

## Important APIs, Types, And Functions
Key functions are `mxm_shadow_rom_fetch`, `mxm_shadow_rom`, `mxm_shadow_dsm`, `wmi_wmmx_mxmi`, `mxm_shadow_wmi`, `mxm_shadow`, and exported `nvkm_mxm_new_`. The `_mxm_shadow` table orders ROM, DSM, and WMI providers according to build configuration.

## Control Flow
`nvkm_mxm_new_` reads the MXM VBIOS table and version. If no VBIOS MXM data exists it exits successfully with no work. Otherwise it calls `mxm_shadow`, which tries each provider, validates the resulting `mxm->mxms` with `mxms_valid`, and frees failed candidates. Successful discovery logs MXMS version, optionally dumps descriptors, and sets `MXM_SANITISE_DCB` unless `NvMXMDCB=false`.

## State And Persistence
Owns `struct nvkm_mxm`, `mxm->mxms` allocated from ROM/ACPI data, and `mxm->action`. The SIS blob persists for later MXM parsing and DCB sanitization.

## Dependencies And Integration Points
Depends on BIOS MXM helpers, I2C bus lookup, ACPI DSM/WMI APIs when enabled, and `core/option.h`. `nv50.c` consumes `mxm->action` and the parsed MXMS data.

## Risks And Test Signals
Risks include malformed ACPI buffers, bad length fields before allocation, checksum/signature failures, systems requiring exact DSM revision, and silent fallback when SIS is absent. Test MXM laptops with ROM, DSM, and WMI paths; invalid checksum tables; `NvMXMDCB=0`; and ACPI-disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mxm/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mxm/mxms.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mxm/mxms.c

## Purpose
Parses and validates MXM System Information Structure blobs, iterates descriptor records, and decodes output-device descriptors for DCB sanitization.

## Important APIs, Types, And Functions
Exports `mxms_version`, `mxms_headerlen`, `mxms_structlen`, `mxms_checksum`, `mxms_valid`, `mxms_foreach`, and `mxms_output_device`. Internal macros `ROM16` and `ROM32` perform little-endian unaligned reads.

## Control Flow
Validation checks the `_MXM` signature, supported versions `2.0`, `2.1`, or `3.0`, and additive checksum over header plus structure. `mxms_foreach` walks descriptors from header end to structure end, derives header/record sizes from descriptor type, optionally logs debug dumps, and invokes a callback for selected types. `mxms_output_device` extracts output type, DDC port, connector type, and digital connection fields.

## State And Persistence
The file stores no state; it reads `mxm->mxms` and fills caller-provided output structures. `mxms_foreach` callbacks may mutate the underlying blob, as `nv50.c` does to mark matched descriptors.

## Dependencies And Integration Points
Depends on `priv.h`, debug logging, unaligned little-endian helpers, and MXM descriptor format assumptions. `base.c` uses validation; `nv50.c` uses iteration and output-device decode.

## Risks And Test Signals
Risks include trusting structure length, descriptor walk overrun if malformed, unknown descriptor types aborting iteration, endian/alignment issues in direct casts, and callback mutation side effects. Test MXMS 2.0/2.1/3.0 blobs, every descriptor type 0-7, checksum failure, truncated structures, and unmatched output logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mxm/mxms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mxm/mxms.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mxm/mxms.h

## Purpose
Declares the MXMS parser interface and output-device descriptor structure used by MXM base and NV50 sanitization code.

## Important APIs, Types, And Functions
Defines `struct mxms_odev` with `outp_type`, `conn_type`, `ddc_port`, and `dig_conn`. Declares all exported parser helpers: `mxms_output_device`, `mxms_version`, `mxms_headerlen`, `mxms_structlen`, `mxms_checksum`, `mxms_valid`, and `mxms_foreach`.

## Control Flow
No executable control flow exists in this header.

## State And Persistence
No state is stored. The struct layout is the cross-file data contract for decoded MXMS ODS records.

## Dependencies And Integration Points
Includes `priv.h` for `struct nvkm_mxm`. Used by `base.c`, `mxms.c`, and `nv50.c`.

## Risks And Test Signals
Risk is interface drift between parser implementation and callers. Build tests catch signature mismatches; runtime DCB sanitization tests catch semantic mismatches in `mxms_odev` fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mxm/mxms.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mxm/nv50.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mxm/nv50.c

## Purpose
Sanitizes NV50-era DCB output tables using MXM-SIS output device descriptors. It disables DCB outputs not represented by MXM, fixes DDC/AUX and SOR link mapping, and adjusts connector types.

## Important APIs, Types, And Functions
Key functions are `mxm_match_tmds_partner`, `mxm_match_dcb`, `mxm_dcb_sanitise_entry`, `mxm_show_unmatched`, `mxm_dcb_sanitise`, and exported `nv50_mxm_new`. `struct context` carries the current DCB output words and decoded MXMS descriptor.

## Control Flow
After `nvkm_mxm_new_`, `nv50_mxm_new` runs sanitization if `MXM_SANITISE_DCB` is set. Sanitization requires DCB version 0x40 or 0x41, then iterates DCB outputs. Each output seeks a matching MXMS ODS record by output type and, for digital outputs, SOR/link mapping. Unmatched DCB entries are disabled; matched entries get DDC/AUX, link, power-script, and connector-type fixups.

## State And Persistence
This code mutates BIOS shadow data in-place: DCB output words, connector table entries for MXMS >= 3.0, and MXMS descriptor type fields used to mark matched records. Those mutations persist for later display initialization.

## Dependencies And Integration Points
Depends on BIOS DCB/connector/MXM helpers and `mxms_foreach`. It integrates between platform-provided MXM SIS data and nouveau display connector/encoder setup.

## Risks And Test Signals
Risks include disabling valid outputs when SIS is incomplete, DP/TMDS partner special-case errors, connector table pointer issues, and in-place mutation of shared BIOS data. Test MXM laptops with HDMI, DVI, LVDS, eDP, DP, missing SIS ODS entries, `NvMXMDCB=0`, and DCB 0x40/0x41 variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mxm/nv50.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mxm/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mxm/priv.h

## Purpose
Defines the private MXM subdevice structure and constructor declaration.

## Important APIs, Types, And Functions
Defines `nvkm_mxm(p)` container macro, `MXM_SANITISE_DCB`, `struct nvkm_mxm`, and `nvkm_mxm_new_`.

## Control Flow
No executable control flow exists.

## State And Persistence
`struct nvkm_mxm` persists the subdev base, action flags, and owned MXMS blob pointer.

## Dependencies And Integration Points
Includes public `<subdev/mxm.h>` and is included by all MXM implementation files. The action bit is consumed by `nv50.c`.

## Risks And Test Signals
Risk is memory ownership or flag mismatch across files. Build tests catch layout/name drift; runtime unload tests should catch MXMS blob lifetime leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mxm/priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/Kbuild

## Purpose
Lists PCI subdevice implementation objects included in the NVKM build.

## Important APIs, Types, And Functions
The file adds common AGP/base/PCIe objects and generation-specific PCI backends from NV04 through GH100.

## Control Flow
There is no runtime control flow. Kbuild appends each object to `nvkm-y`.

## State And Persistence
No runtime state is stored. Its effect is persistent build graph membership.

## Dependencies And Integration Points
Integrates with nouveau's aggregate Kbuild. The listed generation files provide `*_pci_new` constructors referenced by device tables.

## Risks And Test Signals
Risk is missing objects causing unresolved constructors or dead code after source changes. Test with allmodconfig-style nouveau builds and symbol resolution for each generation constructor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/agp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/agp.c

## Purpose
Implements optional AGP bridge setup, teardown, mode quirks, preinit reset, and write-combining aperture setup for AGP NVIDIA devices.

## Important APIs, Types, And Functions
Exports `nvkm_agp_ctor`, `nvkm_agp_dtor`, `nvkm_agp_preinit`, `nvkm_agp_init`, and `nvkm_agp_fini` when AGP is enabled. Defines quirk table `nvkm_device_agp_quirks`.

## Control Flow
Constructor temporarily acquires the AGP bridge, copies mode/base/size info, applies `NvAGP`, platform defaults, and hostbridge/chip quirks, disables fast writes on NV18, and registers write-combining. Preinit disables fast writes if needed, disables bus mastering/AGP, resets PGRAPH/PFIFO/PTIMER, and restores bus mastering. Init acquires and enables the backend; fini releases it.

## State And Persistence
Stores bridge pointer, AGP mode/base/size/CMA, MTRR handle, and acquired flag inside `pci->agp`. Hardware AGP mode and CPU WC mapping persist until fini/dtor.

## Dependencies And Integration Points
Depends on Linux AGP backend, PCI IDs, architecture WC APIs, and `NvAGP` options. Called from PCI base constructor/preinit/init/fini/dtor.

## Risks And Test Signals
Risks include bridge acquisition failure, bad quirks, fast-write lockups, PowerPC GATT issues, WC mapping leaks, and mode mismatches. Test AGP mode 0/1/2/4/8, quirked VIA/SiS platforms, NV18, module unload, and VBIOS init requiring stable AGP reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/agp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/agp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/agp.h

## Purpose
Declares AGP helper functions or provides no-op stubs when AGP support is unavailable.

## Important APIs, Types, And Functions
Declares/stubs `nvkm_agp_ctor`, `nvkm_agp_dtor`, `nvkm_agp_preinit`, `nvkm_agp_init`, and `nvkm_agp_fini`.

## Control Flow
Conditional compilation selects real declarations for `CONFIG_AGP` or AGP module builds, otherwise inline no-ops and `-ENOSYS` init.

## State And Persistence
No direct state is stored. It controls whether PCI base can call real AGP lifecycle functions.

## Dependencies And Integration Points
Includes `priv.h` and is consumed by `base.c` and `agp.c`.

## Risks And Test Signals
Risk is configuration mismatch between AGP objects and header stubs. Test AGP built-in, AGP module, and no-AGP configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/agp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/base.c

## Purpose
Provides the common NVKM PCI subdevice lifecycle, config-space helpers, AGP/PCIe initialization hooks, ROM shadow control, MSI enablement, and constructor.

## Important APIs, Types, And Functions
Exports `nvkm_pci_msi_rearm`, `nvkm_pci_rd32`, `nvkm_pci_wr08`, `nvkm_pci_wr32`, `nvkm_pci_mask`, `nvkm_pci_rom_shadow`, and `nvkm_pci_new_`. Internal lifecycle hooks are `nvkm_pci_preinit`, `nvkm_pci_oneinit`, `nvkm_pci_init`, `nvkm_pci_fini`, and `nvkm_pci_dtor`.

## Control Flow
Constructor allocates `struct nvkm_pci`, stores generation callbacks, initializes PCIe speed/width to -1, sets up AGP if needed, chooses MSI eligibility with chipset/bridge/big-endian exclusions and `NvMSI`, then enables MSI only if a rearm callback exists. Init initializes AGP or PCIe, runs generation init, and rearms pending MSI.

## State And Persistence
Persists `pci->func`, Linux `pci_dev`, AGP state, MSI state, and requested PCIe link state. Config writes modify device hardware registers.

## Dependencies And Integration Points
Depends on core PCI device access, AGP helpers, PCIe helpers, and generation-specific `nvkm_pci_func` tables. Device constructors call `nvkm_pci_new_`.

## Risks And Test Signals
Risks include MSI enabled on unsupported bridges, config aperture mismatch, AGP/PCIe init ordering, ROM shadow bit mistakes, and resource cleanup on constructor failures. Test MSI on/off, big-endian builds, AGP devices, PCIe link setup, module unload, and config read/write smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/g84.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/g84.c

## Purpose
Implements G84/G86 PCIe control and PCI initialization quirks, including version reporting, link speed changes, request tag limiting, and function table construction.

## Important APIs, Types, And Functions
Exports `g84_pcie_version`, `g84_pcie_set_version`, `g84_pcie_set_link_speed`, `g84_pcie_cur_speed`, `g84_pcie_max_speed`, `g84_pci_init`, `g84_pcie_init`, `g84_pcie_set_link`, and `g84_pci_new`.

## Control Flow
Version support is forced to 1 because G84/G86 report wrong capability data. Link speed writes config register `0x460` and triggers retrain. PCI init adjusts request limits depending on EXT_TAG availability. PCIe init mirrors current 5.0 GT/s state into the cap-speed bit.

## State And Persistence
Hardware state lives in PCI config registers and PUNITS register `0x00154c`. Requested link state is also tracked by common PCIe code in `pci->pcie`.

## Dependencies And Integration Points
Depends on `core/pci.h`, common PCI config helpers, and NV46 MSI rearm. G92/G94/GF100 variants reuse several G84 PCIe helpers.

## Risks And Test Signals
Risks include misdetecting link speed, retrain failures, EXT_TAG request-limit regression, and incorrect Gen2 enablement on chips with bad caps. Test Gen1/Gen2 link changes, EXT_TAG enabled/disabled, suspend/resume, MSI rearm, and fdo#86537-style request pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/g84.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/g92.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/g92.c

## Purpose
Defines the G92 PCI backend, mainly overriding PCIe version capability detection while reusing G84 behavior.

## Important APIs, Types, And Functions
Exports `g92_pcie_version_supported` and `g92_pci_new`. The function table uses G84 init/link/version helpers and NV46 MSI rearm.

## Control Flow
Capability detection reads config register `0x460` bit `0x200`; set means PCIe version 2, otherwise version 1. Construction delegates to `nvkm_pci_new_`.

## State And Persistence
No local state is stored. Hardware config state is managed by reused G84 helpers.

## Dependencies And Integration Points
Depends on G84 helper exports and common PCI base. G94/GF100/GF106 reuse `g92_pcie_version_supported`.

## Risks And Test Signals
Risk is capability-bit misinterpretation causing incorrect Gen2 enablement. Test G92 boards on Gen1/Gen2 slots and link-speed set requests through common PCIe code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/g92.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/g94.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/g94.c

## Purpose
Defines the G94 PCI backend as a G84/G92-derived function table with a different MSI rearm path.

## Important APIs, Types, And Functions
Exports `g94_pci_new`. The function table uses G84 PCI init and PCIe helpers, `g92_pcie_version_supported`, and `nv40_pci_msi_rearm`.

## Control Flow
No new logic beyond construction. All runtime behavior is delegated through the function table.

## State And Persistence
State is common `struct nvkm_pci` state plus hardware config touched by inherited helpers.

## Dependencies And Integration Points
Depends on G84/G92 helper symbols and NV40 MSI rearm. Selected by chipset PCI constructor tables.

## Risks And Test Signals
Risk is selecting the wrong MSI rearm method for the chipset. Test MSI interrupt delivery/rearm and inherited PCIe speed handling on G94 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/g94.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/gf100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/gf100.c

## Purpose
Implements GF100/Fermi PCIe control and MSI rearm logic, using newer PUNITS registers while reusing G84 config-space link retrain helpers.

## Important APIs, Types, And Functions
Exports `gf100_pcie_set_version`, `gf100_pcie_version`, `gf100_pcie_set_cap_speed`, `gf100_pcie_cap_speed`, `gf100_pcie_init`, `gf100_pcie_set_link`, and `gf100_pci_new`.

## Control Flow
MSI rearm writes byte `0xff` to config offset `0x0704`. PCIe version and cap-speed bits are controlled through device register `0x02241c`; link retrain still uses `g84_pcie_set_link_speed`. Function table also uses G84 PCI init and G92 version-supported detection.

## State And Persistence
Hardware state persists in PCI config aperture and PUNITS register `0x02241c`. Common PCI state tracks MSI and requested link.

## Dependencies And Integration Points
Depends on G84/G92 helpers and common PCI base. GF106 and GK104 reuse GF100 PCIe helper functions.

## Risks And Test Signals
Risks include wrong cap-speed bit, MSI rearm register mismatch, and inherited Gen2 detection behavior. Test Gen1/Gen2 transitions, MSI interrupt storms, load-time pending interrupts, and request-tag init behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/gf100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/gf106.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/gf106.c

## Purpose
Defines GF106 PCI backend as a GF100-derived function table with NV40 MSI rearm.

## Important APIs, Types, And Functions
Exports `gf106_pci_new`. The table uses G84 PCI init, GF100 PCIe init/set-link/version helpers, G84 speed readers, G92 supported-version detection, and `nv40_pci_msi_rearm`.

## Control Flow
All runtime behavior is delegated via the function table to shared helpers.

## State And Persistence
No local state is stored. Common PCI state and hardware config registers are modified by inherited callbacks.

## Dependencies And Integration Points
Depends on GF100/G84/G92 helper exports and common PCI constructor.

## Risks And Test Signals
Risk is function-table mismatch for MSI rearm or PCIe registers. Test GF106 MSI delivery, Gen2 link changes, and inherited G84 PCI init behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/gf106.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/gh100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/gh100.c

## Purpose
Defines GH100 PCI config-space access using generated XTL endpoint PRI bounds and a no-op MSI rearm hook.

## Important APIs, Types, And Functions
Exports `gh100_pci_new`. The local `gh100_pci` function table sets `.cfg.addr` and `.cfg.size` from `NV_EP_PCFGM` DRF bounds and provides `gh100_pci_msi_rearm`.

## Control Flow
No-op rearm documents that MSI acknowledgement is handled by top-level interrupt ACK. Construction delegates to `nvkm_pci_new_`.

## State And Persistence
Common PCI state stores MSI and config aperture metadata. No local runtime state is owned.

## Dependencies And Integration Points
Depends on `nvhw/drf.h` and `nvhw/ref/gh100/dev_xtl_ep_pri.h`. Integrates with GH100 interrupt handling outside this file.

## Risks And Test Signals
Risks include incorrect generated register bounds and assuming top-level ACK always handles MSI. Test config read/write through the GH100 aperture, MSI interrupt delivery, and builds against nvhw GH100 headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/gh100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/gk104.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/gk104.c

## Purpose
Implements GK104/Kepler PCIe Gen3-capable speed capability, link control, max speed detection, link initialization, and link retrain behavior.

## Important APIs, Types, And Functions
Key helpers are `gk104_pcie_version_supported`, `gk104_pcie_set_cap_speed`, `gk104_pcie_cap_speed`, `gk104_pcie_set_lnkctl_speed`, `gk104_pcie_lnkctl_speed`, `gk104_pcie_max_speed`, `gk104_pcie_set_link_speed`, `gk104_pcie_init`, `gk104_pcie_set_link`, and exported `gk104_pci_new`.

## Control Flow
Init exits if the PCIe version is below 2, then aligns capability and link-control speed to hardware max speed. Link setting clamps requested speed to both cap speed and link-control speed before programming retrain register `0x8c040`. Version support reads `0x8c1c0`.

## State And Persistence
Hardware state persists in PUNITS/device registers `0x8c1c0`, `0x8c040`, and PCI config offset `0xa8`. Common PCI state tracks requested speed/width.

## Dependencies And Integration Points
Depends on GF100 version/cap helpers, G84 current speed and PCI init, NV40 MSI rearm, and common PCIe policy in `pcie.c`.

## Risks And Test Signals
Risks include Gen3 cap misprogramming, clamping to stale lnkctl speed, typo-prone register masks, and max-speed decode fallback. Test 2.5/5.0/8.0 GT/s slots, forced lower bus max speed, suspend/resume, user-requested link changes, and MSI delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/gk104.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/gp100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/gp100.c

## Purpose
Defines GP100 PCI backend with a GP100-specific MSI rearm write and no PCIe link management callbacks.

## Important APIs, Types, And Functions
Exports `gp100_pci_new`. Internal `gp100_pci_msi_rearm` writes zero to config offset `0x0704`.

## Control Flow
Construction delegates to `nvkm_pci_new_`; runtime behavior is limited to MSI rearm through the function table.

## State And Persistence
Common PCI state stores config aperture and MSI enabled state. Rearm writes config hardware state.

## Dependencies And Integration Points
Depends on common PCI base. Lack of PCIe callbacks means common PCIe init/set-link paths become no-op or unsupported.

## Risks And Test Signals
Risk is MSI rearm polarity/value mismatch and missing PCIe management where expected. Test GP100 interrupt delivery, pending MSI at load, and absence of link-management regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/gp100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/nv04.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/nv04.c

## Purpose
Defines the NV04 PCI backend with the legacy PCI config aperture address.

## Important APIs, Types, And Functions
Exports `nv04_pci_new`. The function table sets `.cfg.addr = 0x001800` and `.cfg.size = 0x1000`.

## Control Flow
No generation-specific runtime callbacks are provided; construction delegates to common PCI allocation.

## State And Persistence
Common PCI state stores the config aperture. Hardware state is only changed by common helpers if called.

## Dependencies And Integration Points
Depends on `priv.h` and `nvkm_pci_new_`. Selected for earliest NVIDIA chipsets.

## Risks And Test Signals
Risk is using the wrong config aperture for legacy chips. Test config-space reads/writes and ROM shadow access on NV04-class hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/nv04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/nv40.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/nv40.c

## Purpose
Defines NV40 PCI backend and its PRI-based MSI rearm helper.

## Important APIs, Types, And Functions
Exports `nv40_pci_msi_rearm` and `nv40_pci_new`. The function table uses config aperture `0x088000` and the NV40 rearm callback.

## Control Flow
MSI rearm writes byte `0xff` to config offset `0x0068` through NVKM config aperture helpers. Construction delegates to common PCI setup.

## State And Persistence
Common PCI state tracks MSI enablement; rearm modifies hardware interrupt state.

## Dependencies And Integration Points
Used directly by NV40 and reused by G94/GF106/GK104 function tables.

## Risks And Test Signals
Risk is using PRI rearm on chips where it is broken. Test MSI interrupt delivery and rearm after load/suspend on NV40 and users of this helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/nv40.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/nv46.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/nv46.c

## Purpose
Defines NV46 PCI backend and an alternate Linux PCI config-space MSI rearm path for chips where PRI rearm is broken.

## Important APIs, Types, And Functions
Exports `nv46_pci_msi_rearm` and `nv46_pci_new`. The function table sets aperture `0x088000` and uses the alternate rearm callback.

## Control Flow
`nv46_pci_msi_rearm` obtains the Linux `pci_dev` from the NVKM device and calls `pci_write_config_byte(pdev, 0x68, 0xff)`.

## State And Persistence
Common PCI state stores MSI enablement; the Linux PCI config write rearms the interrupt state.

## Dependencies And Integration Points
Depends on `core/pci.h`. G84/G86/G92 use this helper because the file comments note PRI-based rearm is broken there too.

## Risks And Test Signals
Risks include config write failures hidden by void API and wrong offset on unsupported chips. Test MSI rearm on NV46/NV50/G84/G86/G92 and compare with PRI rearm behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/nv46.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/nv4c.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/nv4c.c

## Purpose
Defines NV4C PCI backend with the standard `0x088000` config aperture and no generation-specific callbacks.

## Important APIs, Types, And Functions
Exports `nv4c_pci_new`.

## Control Flow
Construction delegates to common PCI setup; runtime behavior comes from common code only.

## State And Persistence
Common `struct nvkm_pci` state persists the config aperture and MSI/link state if applicable.

## Dependencies And Integration Points
Depends on `priv.h` and common PCI constructor.

## Risks And Test Signals
Risk is absence of MSI rearm or PCIe callbacks for hardware that might need them. Test config access and interrupt behavior on NV4C-class devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/nv4c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/pcie.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/pcie.c

## Purpose
Provides common PCIe speed/version policy: speed enum conversion, version raise during init, one-time max-speed logging, and requested link speed setting.

## Important APIs, Types, And Functions
Exports `nvkm_pcie_oneinit`, `nvkm_pcie_init`, and `nvkm_pcie_set_link`. Internal helpers are `nvkm_pcie_speed`, `nvkm_pcie_get_version`, `nvkm_pcie_get_max_version`, and `nvkm_pcie_set_version`.

## Control Flow
Init reads current and max version; if the card supports a higher version, it calls generation `set_version` and warns on failure. It then runs generation PCIe init and applies any stored requested speed/width. `nvkm_pcie_set_link` validates PCIe presence and callback availability, clamps requested speed to bus and card max, stores requested speed/width, skips if already current, and calls generation `set_link`.

## State And Persistence
Stores desired link speed/width in `pci->pcie`. Hardware link/version state persists through generation callbacks.

## Dependencies And Integration Points
Depends on Linux PCI bus speed reporting and `nvkm_pci_func.pcie` callbacks. All generation files with PCIe support plug into this policy.

## Risks And Test Signals
Risks include out-of-range speed-string indexing, unsupported 16 GT/s fallback to 8 GT/s, callback absence, clamping mistakes, and version raise failures. Test Gen1/Gen2/Gen3 boards, bus max lower than card max, stored requested speed across init, and non-PCIe/unsupported callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/pcie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/priv.h

## Purpose
Defines the private PCI subdevice function table and declares shared generation helper functions.

## Important APIs, Types, And Functions
Defines `nvkm_pci(p)`, `struct nvkm_pci_func`, and `nvkm_pci_new_`. Declares MSI rearm helpers, G84/GF100/GK104 PCIe helper APIs, and common PCIe lifecycle functions.

## Control Flow
No executable control flow exists.

## State And Persistence
The `nvkm_pci_func` layout is the persistent cross-file callback contract for config aperture, init, MSI rearm, and PCIe operations.

## Dependencies And Integration Points
Includes public `<subdev/pci.h>`. Used by every PCI implementation file.

## Risks And Test Signals
Risk is ABI-like callback drift between declaration and implementation. Build tests catch signatures; runtime PCIe/MSI tests catch semantic mismatches in populated callback tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/Kbuild

## Purpose
Lists PMU subdevice objects linked into NVKM, covering common PMU code, memory scripts, and generation-specific PMU backends.

## Important APIs, Types, And Functions
Declaratively adds `base.o`, `memx.o`, `gt215.o`, `gf100.o`, `gf119.o`, `gk104.o`, `gk110.o`, `gk208.o`, `gk20a.o`, `gm107.o`, `gm200.o`, `gm20b.o`, `gp102.o`, and `gp10b.o`.

## Control Flow
No runtime control flow exists.

## State And Persistence
No runtime state. Build membership persists via `nvkm-y`.

## Dependencies And Integration Points
Integrates with nouveau Kbuild and generation constructor tables that expect these PMU objects.

## Risks And Test Signals
Risk is missing PMU object linkage or stale object names after refactors. Test allmodconfig-style builds and unresolved PMU constructor/helper symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/base.c

## Purpose
Provides common NVKM PMU subdevice construction, firmware interface loading, falcon queue setup, lifecycle hooks, fan-control policy, message send/receive wrappers, and interrupt dispatch.

## Important APIs, Types, And Functions
Exports `nvkm_pmu_fan_controlled`, `nvkm_pmu_pgob`, `nvkm_pmu_send`, `nvkm_pmu_ctor`, and `nvkm_pmu_new_`. Internal hooks include `nvkm_pmu_recv`, `nvkm_pmu_intr`, `nvkm_pmu_init`, `nvkm_pmu_fini`, and `nvkm_pmu_dtor`.

## Control Flow
Construction initializes mutex/workqueue/waitqueue state, loads the matching firmware interface via `nvkm_firmware_load`, constructs a falcon at base `0x10a000`, then creates queue manager, high-priority command queue, low-priority command queue, and message queue. Init/fini/intr delegate to generation function callbacks when present. Send returns `-ENODEV` if no PMU or send callback exists.

## State And Persistence
Persists `struct nvkm_pmu`, selected `pmu->func`, falcon state, command/message queues, send mutex, receive work/waitqueue, and `wpr_ready` completion. Destructor tears queue and falcon state down.

## Dependencies And Integration Points
Depends on `core/firmware.h`, falcon queue APIs, timer infrastructure, and generation `nvkm_pmu_fwif` tables. Other subdevices call PMU fan-control, PGO/B, and send wrappers.

## Risks And Test Signals
Risks include partial constructor failure leaks, firmware-interface mismatch, queue creation order, work item racing with teardown, and fan-control policy differences between internal and board firmware. Test PMU init/fini/unload, interrupt receive, command send/reply, firmware fallback, fan control exposure, and failure injection for each queue allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/fuc/gf100.fuc3.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/fuc/gf100.fuc3.h

## Purpose
Embeds GF100 PMU falcon firmware data and code arrays generated from the fuc3 PMU sources. It is included by `pmu/gf100.c`.

## Important APIs, Types, And Functions
Defines `static uint32_t gf100_pmu_data[]` and `static uint32_t gf100_pmu_code[]`. The data array begins with process descriptors such as `proc_kern`; the code array contains raw falcon instruction words.

## Control Flow
There is no C control flow. Runtime control flow occurs inside the PMU falcon after these arrays are uploaded by GT215/GF100 PMU init code.

## State And Persistence
The arrays are compiled into the kernel object and persist as read-only firmware payloads. Runtime PMU state is in falcon IMEM/DMEM after upload, not in this header.

## Dependencies And Integration Points
Included by `gf100.c` and referenced through `nvkm_pmu_func.code/data`. It depends on the fuc build process remaining consistent with `fuc/os.h` message/process constants and GT215 falcon loader expectations.

## Risks And Test Signals
Risks include generated array corruption, size mismatch, stale firmware relative to host message protocols, and accidental edits to raw words. Test by building GF100 PMU, booting Fermi hardware, verifying PMU init/send/recv, MEMX/I2C messages, and comparing generated arrays against fuc source regeneration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/fuc/gf100.fuc3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/fuc/gf119.fuc4.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/fuc/gf119.fuc4.h

## Purpose
Embeds GF119-class PMU falcon firmware data and code arrays generated from fuc4 sources. It is included by `gf119.c` and, with macro aliasing, by `gk104.c`.

## Important APIs, Types, And Functions
Defines `static uint32_t gf119_pmu_data[]` and `static uint32_t gf119_pmu_code[]` unless including code aliases those identifiers first.

## Control Flow
No C control flow exists. The binary instruction stream executes on the PMU falcon after upload by common GT215-derived PMU code.

## State And Persistence
Arrays are compiled into the driver and used as firmware payloads. Falcon DMEM/IMEM state is runtime state after loading.

## Dependencies And Integration Points
Included by GF119 and GK104 PMU backends. It must remain compatible with `gt215_pmu_flcn`, `gt215_pmu_init`, message queues, and `fuc/os.h` protocol definitions.

## Risks And Test Signals
Risks include alias misuse in `gk104.c`, generated data/code mismatch, and protocol drift. Test GF119 and GK104 PMU startup, command/reply paths, PGO/B calls on GK104, and regeneration from fuc4 source.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/fuc/gf119.fuc4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/fuc/gk208.fuc5.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/fuc/gk208.fuc5.h

## Purpose
Embeds GK208 PMU falcon firmware data and code arrays generated from fuc5 sources.

## Important APIs, Types, And Functions
Defines `static uint32_t gk208_pmu_data[]` and `static uint32_t gk208_pmu_code[]`, with process metadata followed by falcon instruction words.

## Control Flow
No host-side C control flow exists. Execution occurs on the PMU falcon after a generation backend uploads the arrays.

## State And Persistence
Compiled arrays are persistent firmware payload data. Runtime state is in falcon memory and PMU queues after initialization.

## Dependencies And Integration Points
Used by the GK208/GM107 family PMU backends outside this work item. Must match the falcon loader, queue protocol, and `fuc/os.h` constants.

## Risks And Test Signals
Risks include stale generated output, wrong array names expected by includers, and host/firmware protocol mismatch. Test PMU init and message handling on GK208/GM107-class devices and compare against regenerated fuc5 output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/fuc/gk208.fuc5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/fuc/gt215.fuc3.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/fuc/gt215.fuc3.h

## Purpose
Embeds GT215 PMU falcon firmware data and code arrays generated from fuc3 sources. It is the baseline firmware payload for the GT215 PMU backend used by later PMU helpers.

## Important APIs, Types, And Functions
Defines `static uint32_t gt215_pmu_data[]` and `static uint32_t gt215_pmu_code[]`.

## Control Flow
There is no C control flow. The firmware instruction stream executes on falcon hardware after upload.

## State And Persistence
The arrays persist in the compiled driver. Runtime state is created in PMU falcon IMEM/DMEM and command/message queues.

## Dependencies And Integration Points
Included by the GT215 PMU backend outside this work item and indirectly important because GF100/GF119/GK104 reuse GT215 PMU loader/send/recv/intr helpers. Protocol constants are shared with `fuc/os.h`.

## Risks And Test Signals
Risks include raw data corruption, protocol mismatch, and loader assumptions about array size/layout. Test GT215 PMU init, command queues, MEMX/I2C firmware messages, and regeneration from fuc3 source.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/fuc/gt215.fuc3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/fuc/os.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/fuc/os.h

## Purpose
Defines PMU falcon firmware process names, message identifiers, MEMX opcodes, and I2C message bitfield layouts shared by fuc firmware and host-side expectations.

## Important APIs, Types, And Functions
Defines process IDs `PROC_KERN`, `PROC_IDLE`, `PROC_HOST`, `PROC_MEMX`, `PROC_PERF`, `PROC_I2C_`, and `PROC_TEST`; message IDs such as `KMSG_FIFO`, `KMSG_ALARM`, `MEMX_MSG_INFO`, `MEMX_MSG_EXEC`; MEMX script opcodes; and I2C bitfield ranges.

## Control Flow
No executable C control flow exists.

## State And Persistence
No state is stored. The constants form a persistent ABI between generated firmware and driver message construction/parsing.

## Dependencies And Integration Points
Included by fuc assembly sources and reflected by host PMU/MEMX/I2C code. Changing values affects generated headers and runtime PMU protocol.

## Risks And Test Signals
Risks include ABI drift, bitfield range mistakes, and process ID mismatch. Test by regenerating all fuc firmware headers and running PMU MEMX/I2C command/reply paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/fuc/os.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/gf100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/gf100.c

## Purpose
Defines GF100 PMU backend using embedded GF100 fuc3 firmware and GT215 PMU runtime helpers, plus MC-based reset/enabled checks.

## Important APIs, Types, And Functions
Exports `gf100_pmu_reset`, `gf100_pmu_enabled`, `gf100_pmu_nofw`, and `gf100_pmu_new`. The `gf100_pmu` function table points at `gt215_pmu_flcn`, `gf100_pmu_code`, `gf100_pmu_data`, GT215 init/fini/intr/send/recv, and GF100 reset/enabled helpers.

## Control Flow
Reset disables and enables the PMU subdevice through MC. Constructor passes `gf100_pmu_fwif` to common PMU allocation; `gf100_pmu_nofw` accepts the embedded firmware path by returning zero.

## State And Persistence
Common PMU state owns falcon and queues. This file contributes static firmware payload pointers and MC reset state changes.

## Dependencies And Integration Points
Depends on `fuc/gf100.fuc3.h`, `subdev/mc.h`, and GT215 PMU helper symbols. GF119/GK104 reuse `gf100_pmu_enabled`, `gf100_pmu_reset`, and `gf100_pmu_nofw`.

## Risks And Test Signals
Risks include MC reset sequencing errors, firmware size mismatch, and assuming GT215 helpers match GF100 firmware. Test PMU reset/enable, firmware upload, interrupt handling, command send/recv, and fan-control policy on GF100 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/gf100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/gf119.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/gf119.c

## Purpose
Defines GF119 PMU backend using embedded GF119 fuc4 firmware and the GF100/GT215 PMU support stack.

## Important APIs, Types, And Functions
Exports `gf119_pmu_new`. The local function table points at `gf119_pmu_code`, `gf119_pmu_data`, `gf100_pmu_enabled`, `gf100_pmu_reset`, and GT215 init/fini/intr/send/recv helpers.

## Control Flow
Construction delegates to `nvkm_pmu_new_` with a firmware-interface table that accepts embedded firmware through `gf100_pmu_nofw`.

## State And Persistence
No local heap state. Static firmware arrays are compiled in; common PMU state persists falcon queues and selected function table.

## Dependencies And Integration Points
Depends on `fuc/gf119.fuc4.h`, GF100 PMU helpers, and GT215 PMU helper symbols. Selected by GF119-class device initialization.

## Risks And Test Signals
Risks include firmware/helper protocol mismatch and missing GF100 helper linkage. Test PMU initialization, message queues, interrupts, and unload on GF119-family GPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/gf119.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/gk104.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/gk104.c

## Purpose
Defines GK104 PMU backend using aliased GF119 fuc4 firmware arrays and adds PGO/B power-gating control with chipset-specific register workarounds.

## Important APIs, Types, And Functions
Exports `gk104_pmu_new`. Important local helpers are `magic_`, `magic`, and `gk104_pmu_pgob`. The function table uses `gk104_pmu_code/data`, GF100 reset/enabled helpers, GT215 PMU runtime helpers, and `.pgob = gk104_pmu_pgob`.

## Control Flow
`gk104_pmu_pgob` first checks fuse bit `0x31c`. If enabled, it gates relevant MC bits, toggles PMU control register `0x10a78c`, sets power gating bits in `0x020004`, ungates state, and optionally runs `War00C800_0` magic sequences for chipsets `0xe4`, `0xe6`, and `0xe7`. `magic_` writes `0x00c800/0x00c808`, waits for bit `0x40000000`, drains zero writes to `0x00c804`, and clears control.

## State And Persistence
Persistent effects are hardware register power-gating state and selected workaround writes. Static firmware arrays are compiled in via macro aliasing before including `gf119.fuc4.h`.

## Dependencies And Integration Points
Depends on `core/option.h`, fuse reads, timer polling, GF100 PMU helpers, GT215 PMU helpers, and the `War00C800_0` config option. Called through common `nvkm_pmu_pgob`.

## Risks And Test Signals
Risks include fuse misread, power-gating register sequencing mistakes, 50 ms delay sensitivity, workaround overapplication, and firmware alias confusion. Test PGO/B enable/disable on GK104 variants, chipsets e4/e6/e7 workaround paths, `War00C800_0=0`, PMU init/intr/send/recv, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/gk104.c -->

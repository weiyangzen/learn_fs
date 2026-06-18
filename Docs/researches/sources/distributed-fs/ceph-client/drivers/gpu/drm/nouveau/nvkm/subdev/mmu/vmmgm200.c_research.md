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

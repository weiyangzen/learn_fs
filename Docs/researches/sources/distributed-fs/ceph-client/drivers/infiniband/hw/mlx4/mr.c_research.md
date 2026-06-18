# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/mr.c

## Purpose
`mr.c` implements mlx4 memory registration verbs: DMA MRs, user MRs, reregistration, deregistration, memory windows, fast-registration MRs, and scatterlist mapping into fast-reg page lists. It translates ib_core access flags and memory objects into mlx4 MPT/MTT resources and keeps user memory pinning synchronized with hardware memory translation state.

## Important APIs, types, and functions
- `convert_access()` maps `IB_ACCESS_*` bits to mlx4 `MLX4_PERM_*` flags and always grants local read.
- `to_mlx4_type()` maps ib_core MW type 1/2 to mlx4 MW type values.
- `mlx4_ib_get_dma_mr()` allocates and enables a whole-address-space DMA MR for a PD.
- `mlx4_ib_umem_write_mtt()` iterates DMA blocks in an `ib_umem` and writes them into an mlx4 MTT.
- `mlx4_get_umem_mr()` pins user memory, upgrading to local write when the VMA is writable so later reregistration can add write access without repinning.
- `mlx4_ib_reg_user_mr()` pins user memory, chooses an optimal MTT page shift, allocates an MPT/MTT, writes MTT entries, enables the MR, and returns lkey/rkey/page size.
- `mlx4_ib_rereg_user_mr()` updates PD, access flags, and/or translation for an existing MR using hardware MPT get/change/write helpers.
- `mlx4_alloc_priv_pages()` and `mlx4_free_priv_pages()` allocate a DMA-mapped private page list for fast-reg MRs.
- `mlx4_ib_dereg_mr()` frees private pages, mlx4 MR hardware resources, user memory, and wrapper memory.
- `mlx4_ib_alloc_mw()` and `mlx4_ib_dealloc_mw()` manage mlx4 memory windows.
- `mlx4_ib_alloc_mr()` creates fast-reg memory MRs with private page lists.
- `mlx4_ib_map_mr_sg()` maps a scatterlist into a fast-reg MR page array through `ib_sg_to_pages()` and `mlx4_set_page()`.

## Control flow
DMA MR allocation creates a zeroed wrapper, allocates an mlx4 MR with base zero and size `~0ull`, enables it, mirrors the hardware key into lkey/rkey, and returns the embedded `ib_mr`. Failure paths free the partially created mlx4 MR and wrapper.

User MR registration rejects DMA handles, allocates a wrapper, pins memory with `mlx4_get_umem_mr()`, computes best page size through `mlx4_ib_umem_calc_optimal_mtt_size()`, allocates an mlx4 MR with the requested IOVA/length/access and number of MTTs, writes each DMA block to the MTT, enables the MR, sets keys and `ibmr.page_size`, and unwinds in reverse on error.

Reregistration first obtains the hardware MPT entry and assumes uverbs serializes deregistration against reregistration. It optionally changes PD, validates access upgrades against `umem->writable`, changes access permissions, and for translation changes cleans old memory translation, releases old umem, pins the new region, rewrites MPT memory parameters and MTT entries, updates cached IOVA/size, then writes the MPT back. On failure it returns `ERR_PTR(err)` and leaves deregistration responsible for cleanup when hardware transfer could not be completed.

Fast-reg MR allocation validates `IB_MR_TYPE_MEM_REG` and `MLX4_MAX_FAST_REG_PAGES`, allocates an MR with empty translation, allocates a single page for the DMA-visible page list aligned to `MLX4_MR_PAGES_ALIGN`, enables the MR, and records max pages. Mapping resets `npages`, syncs the page list for CPU, uses `ib_sg_to_pages()` to append present-bit physical addresses, then syncs back for device.

## State and persistence behavior
MR/MW state is per-object and persists until deregistration/deallocation. User MRs own an `ib_umem` pin and mlx4 `struct mlx4_mr`; fast-reg MRs own a DMA-mapped private page list plus mlx4 MR; MWs own mlx4 MW resources. Keys are hardware-generated and copied into ib_core objects. There is no disk persistence. Hardware translation state persists in MPT/MTT tables until explicitly freed or rewritten.

## Dependencies and integration points
`mr.c` depends on ib_core verbs, `ib_umem`, RDMA DMA block iterators, scatterlist-to-pages helpers, Linux MM VMA locking, DMA mapping APIs, and mlx4 core MR/MW/MPT/MTT helpers. It is wired into ib_device ops by `main.c` through `get_dma_mr`, `reg_user_mr`, `rereg_user_mr`, `dereg_mr`, `alloc_mr`, `map_mr_sg`, `alloc_mw`, and `dealloc_mw`. It relies on wrapper definitions and page-size helper from `mlx4_ib.h`.

## Risks and edge cases
- `mlx4_get_umem_mr()` only checks a single VMA for read-only registration optimization; multi-VMA registrations conservatively become writable, but behavior depends on current MM layout.
- Reregistration translation failure after releasing the old umem can leave the MR partially updated; callers rely on later deregistration cleanup and the explicit `umem = NULL` guard for failed repinning.
- Access upgrade is rejected if the existing umem is not writable, but correctness depends on `umem->writable` accurately reflecting the original pin.
- Fast-reg private page allocation uses one page and assumes `max_pages <= MLX4_MAX_FAST_REG_PAGES` keeps the aligned map within that page.
- `mlx4_set_page()` fails with `-ENOMEM` when scatterlist expansion exceeds `max_pages`; callers must respect partial mapping failures.
- DMA sync direction and page-list lifetime must remain paired with QP fast-reg use to avoid stale device-visible page addresses.

## Test signals
- User MR tests should cover read-only and writable mappings, multi-VMA ranges, access flag combinations, invalid DMA handle use, large page-size selection, and MTT write failures.
- Reregistration tests should cover PD-only, access-only, translation-only, combined changes, access upgrade rejection, repin failure, MPT write failure, and deregistration after failed reregistration.
- Fast-reg tests should cover max page boundary, scatterlist offsets, too many SG pages, DMA sync correctness, and deregistration after mapping.
- MW tests should cover type 1/type 2 allocation, invalid type rejection through core setup, enable failure unwind, and deallocation.

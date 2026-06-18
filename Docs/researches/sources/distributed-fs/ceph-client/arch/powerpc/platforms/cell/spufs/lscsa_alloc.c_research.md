# sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/lscsa_alloc.c

Purpose: allocates and frees the local-store context save area (`lscsa`) used by SPU context switching. This large region contains saved local store and SPU register spill data.

Important APIs: `spu_alloc_lscsa(struct spu_state *csa)` and `spu_free_lscsa(struct spu_state *csa)`.

Control flow: allocation uses `vzalloc(sizeof(struct spu_lscsa))`, stores the pointer in `csa->lscsa`, then marks every page covering the `ls` array as reserved via `SetPageReserved(vmalloc_to_page(p))`. Freeing checks for a null pointer, clears the reserved bit on the same page range, and calls `vfree()`.

State and dependencies: tied to `spu_init_csa()` and `spu_fini_csa()` in `switch.c`, and to mmap handling in `file.c`, where saved local store is mapped through `vmalloc_to_pfn()`. Risks include mismatched reserve clear on partial initialization, page-flag leaks, and assumptions that vmalloc pages are stable for PFN insertion. Test signals are repeated context allocate/free under debug VM, local-store mmap of saved contexts, and no reserved-page warnings after context teardown.

# sources/distributed-fs/ceph-client/include/drm/ttm/ttm_tt.h

Purpose: declares Translation Table backing storage for BOs not directly backed by fixed VRAM/AGP memory, including page arrays, DMA addresses, swap/backup storage, caching, population, swap, backup/restore, kmap iterator support, and optional AGP backend.

Important APIs/types/functions: `struct ttm_tt` stores pages, flags, page count, SG table, DMA addresses, swap and backup files, caching, and restore state. Flags describe swapped, zero-alloc, external, external-mappable, decrypted, backed-up, and private-populated states. `struct ttm_kmap_iter_tt` adapts TT pages to kmap iteration. APIs create/init/fini/destroy TT, populate/unpopulate, swap in/out, mark for clear, initialize global TT manager, initialize TT kmap iterator, query page limit, configure backup, backup/restore TT, and optional AGP create/bind/unbind/destroy/is_bound.

Control flow: BO creation creates a TT without pages, validation/population allocates or restores pages, moves bind them into aperture resources, shrink/swap backs or swaps them out, and destroy unbinds/unpopulates/frees backend state.

State and persistence: TT state is the page vector plus flags and backup/swap handles. External flags prevent TTM from swapping or mapping externally owned pages directly.

Dependencies and integration: depends on pagemap, caching, kmap iterator, TTM device/resource/BO, pool backup, shmem, DMA, SG, and optional AGP.

Risks and test signals: external page handling, backup flag clearing, decrypted pgprot assumptions, population flag correctness, and AGP binding are key risks. Test populate/unpopulate, swapout/swapin, backup/restore, external SG/userptr pages, zero allocation, decrypted mappings, and AGP builds.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_lmtt.c

## Purpose
`xe_lmtt.c` manages Local Memory Translation Tables for SR-IOV PF operation. LMTT maps VF-visible local-memory offsets to PF VRAM backing pages, sets the root directory in hardware, and invalidates GT/MERT TLBs when mappings change.

## Important APIs, Types, And Functions
- Public API: `xe_lmtt_init()`, `xe_lmtt_init_hw()`, `xe_lmtt_invalidate_hw()`, `xe_lmtt_prepare_pages()`, `xe_lmtt_populate_pages()`, `xe_lmtt_drop_pages()`, `xe_lmtt_estimate_pt_size()`, and `xe_lmtt_page_size()`.
- Variant selection uses `lmtt_2l_ops` or `lmtt_ml_ops` based on graphics version.
- `lmtt_pt_alloc()` creates VRAM-backed, 64K-capable page table BOs and stores child pointers in flexible arrays.
- `lmtt_alloc_range()` and `__lmtt_alloc_range()` recursively allocate VF page-table hierarchy.
- `lmtt_insert_bo()` walks a VRAM BO resource cursor and writes leaf PTEs.
- `lmtt_setup_dir_ptr()` programs LMEM/MERT directory pointer registers.

## Control Flow
PF initialization selects ops, allocates a root page directory, and registers managed cleanup. Hardware initialization programs the directory pointer after reset. VF setup calls `xe_lmtt_prepare_pages()` for the supported range, then `xe_lmtt_populate_pages()` for BO backstore. VF teardown calls `xe_lmtt_drop_pages()`, invalidates the PDE, invalidates GT TLBs, and recursively frees child page tables. Explicit hardware invalidation also triggers MERT invalidation on capable root tiles.

## State And Persistence
`struct xe_lmtt` stores root PD and ops. Each `struct xe_lmtt_pt` owns a pinned mapped VRAM BO plus child pointers. LMTT page-table contents persist in VRAM across normal operation and are re-registered after resets by `xe_lmtt_init_hw()`. Managed cleanup asserts all VF child entries are dropped before freeing the root.

## Dependencies And Integration Points
The file depends on Xe BO creation/mapping, tile/GT topology, SR-IOV PF checks, TLB invalidation fences, MERT invalidation, MMIO LMEM config registers, resource cursors, and the common `xe_map` memory access wrappers. It includes KUnit tests when built with `CONFIG_DRM_XE_KUNIT_TEST`.

## Risks
Recursive allocation error handling can leave partially populated child structures if a deeper allocation fails after PDE writes; callers need robust teardown on failure. Index assertions use `<=` in places where `<` may be expected. Mapping insertion assumes prepared leaf tables already exist. The `vram_offset` adjustment is marked `XXX`, signaling hardware address interpretation risk. Missing invalidations can expose stale VF translations.

## Test Signals
KUnit should cover 2L and ML page sizes, PTE encoding/indexing, range allocation/drop, PT size estimates, invalidation calls, partial allocation failures, and BO population over fragmented VRAM resources.

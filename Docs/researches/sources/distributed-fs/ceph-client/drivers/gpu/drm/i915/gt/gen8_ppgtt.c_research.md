<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen8_ppgtt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen8_ppgtt.c

## Purpose
`gen8_ppgtt.c` implements Gen8+ per-process graphics translation table management. It allocates and tears down multi-level page-table trees, encodes PTEs/PDEs, inserts normal and huge-page mappings, clears ranges back to scratch entries, initializes scratch tables, handles vGPU page-table notifications, and constructs `i915_ppgtt` address spaces.

## Important APIs, Types, and Functions
The exported entry point is `gen8_ppgtt_create()`. PTE/PDE encoding helpers include `gen8_pde_encode()`, `gen8_pte_encode()`, and `gen12_pte_encode()`. Tree helpers include `gen8_pd_range()`, `gen8_pd_contains()`, `gen8_pt_count()`, `gen8_pd_top_count()`, `gen8_pdp_for_page_index()`, and `gen8_pdp_for_page_address()`. Lifecycle functions include `gen8_ppgtt_cleanup()`, `gen8_ppgtt_alloc()`, `gen8_ppgtt_clear()`, `gen8_ppgtt_foreach()`, `gen8_init_scratch()`, `gen8_alloc_top_pd()`, `gen8_preallocate_top_level_pdp()`, and `gen8_init_rsvd()`. Mapping functions include `gen8_ppgtt_insert()`, `gen8_ppgtt_insert_pte()`, `gen8_ppgtt_insert_huge()`, `xehp_ppgtt_insert_huge()`, `gen8_ppgtt_insert_entry()`, and `xehp_ppgtt_insert_entry()`.

## Control Flow
Creation initializes the `i915_ppgtt`, chooses 3- or 4-level topology, selects read-only support and LMEM/SMEM page-table allocators, installs PTE insertion/clear/foreach callbacks, initializes scratch objects, allocates the top page directory, preallocates 3-level PDP entries when needed, notifies vGPU if active, and reserves a workaround VMA if required. Range allocation walks page-directory levels, pulls tables from the stash, fills them with scratch encodings, installs them under `pd->lock`, and updates `used` counters. Range clearing recursively replaces PTEs/PDEs with scratch entries and frees empty page-table pages. Insert paths walk scatter-gather DMA segments, encode PTEs with PAT/cache/read-only/LMEM bits, support 2M and 64K layouts, flush CPU caches for written page-table pages, and record actual GTT page sizes.

## State and Persistence
Persistent state lives in `ppgtt->pd`, `vm->scratch[]`, page-table objects, `px_used()` counters, `pt->is_compact`, `vma_res->page_sizes_gtt`, and optional `vm->rsvd` workaround objects. vGPU creation/destruction writes PDP addresses and notifications through the vgt interface. Page-table memory is GPU-visible and remains active until VM cleanup or range clear frees unused subtrees.

## Dependencies and Integration Points
This file depends on GEM internal/LMEM allocation, scatterlist DMA iteration, `intel_gtt` page-table helpers, PAT/cache helpers, vGPU PV info, and GT platform feature predicates. Its callbacks are consumed by VMA bind/unbind paths, context VM setup, GGTT/PPGTT invalidation flows, and selftests that validate huge-page behavior.

## Risks and Edge Cases
Risks center on concurrency and page-table accounting: `used` counters must prevent freeing tables still being walked, locks must be dropped around allocation safely, and scratch entries must match page size/layout. Huge-page insertion is subtle for mixed SG alignment, compact 64K LMEM layout, and scratch padding. Gen11/Gen12 read-only disablement is a hardware workaround. vGPU notification increments top PD use so virtualized page tables are never removed prematurely.

## Test Signals
Strong tests include bind/unbind range stress, random VM allocation/clear, 4K/64K/2M page-size combinations, LMEM versus system memory mappings, read-only PTE faults on supported gens, vGPU create/destroy paths, reserved-wa VMA placement, and debug assertions under concurrent VM teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen8_ppgtt.c -->

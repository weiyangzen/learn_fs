# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_gem_gtt.c

## Purpose
This file is the i915 GEM GTT selftest suite. It validates GPU virtual address-space behavior across mock GGTT, live GGTT, and per-process PPGTT address spaces. The main target is correctness of allocation, page-table population, hole walking, fixed-offset pinning, eviction, shrinker interaction, resource-backed VMA reservation/insertion, misalignment handling, and direct GGTT page insertion.

## Important APIs, Types, And Functions
- `i915_gem_gtt_mock_selftests()` builds a mock GEM device, assigns and initializes a mock GGTT, then runs mock subtests.
- `i915_gem_gtt_live_selftests()` runs live PPGTT/GGTT subtests through `i915_live_subtests()`.
- `fake_dma_object()`, `fake_get_pages()`, `fake_put_pages()`, and `fake_ops` provide synthetic GEM objects with preallocated scatterlists so address-space tests can allocate very large objects without real backing content.
- Hole exercisers include `lowlevel_hole()`, `fill_hole()`, `walk_hole()`, `pot_hole()`, `drunk_hole()`, `shrink_hole()`, `shrink_boom()`, and `misaligned_pin()`.
- Wrappers `exercise_ppgtt()`, `exercise_ggtt()`, and `exercise_mock()` apply those exercisers to the desired VM.
- `reserve_gtt_with_resource()` and `insert_gtt_with_resource()` allocate `i915_vma_resource` metadata and call `i915_gem_gtt_reserve()` / `i915_gem_gtt_insert()`.

## Control Flow
The suite creates a target address space, identifies a hole range, then drives one of several placement patterns. Fixed-offset tests bind and unbind VMAs at exact offsets; random tests generate shuffled orders with `i915_random_order()`; power-of-two boundary tests straddle page-table boundaries; shrink tests enable fault injection on `vm->fault_attr`; misalignment tests iterate memory regions and compare expected VMA/node size expansion. GGTT testing sorts the `drm_mm` hole stack and restarts traversal after mutations to avoid stale hole iteration. Mock tests build a synthetic context VM and cap the range to system RAM.

## State And Persistence
State is intentionally transient: mock devices, contexts, fake GEM objects, VMAs, page-table stashes, `drm_mm_node`s, and runtime PM wakerefs are created only for each test and released before return. The file mutates `vm->fault_attr` for shrink fault injection and restores it to zero. It temporarily changes GGTT mappings through `insert_entries`, `insert_page`, and `clear_range`; cleanup drains freed GEM objects to prevent cross-test pollution. No persistent on-disk state exists.

## Dependencies And Integration Points
It depends on GEM object internals, PPGTT/GGTT VM methods, `drm_mm`, runtime PM, memory-region page-size rules, mock GEM/GTT setup, and selftest helpers (`i915_random`, `igt_flush_test`, `mock_context`). The live suite integrates with the driver selftest dispatcher via `i915_live_subtests`; the mock suite integrates via `i915_subtests`.

## Risks
These tests intentionally stress large address spaces and can hit allocation pressure; many allocation failures are treated as expected when they stem from test scale. Cleanup correctness is high risk because leaked pinned pages or bound VMAs would corrupt later selftests. Misaligned and shrinker cases rely on exact page-size and fault-injection behavior, so changes in memory-region alignment, GGTT page-size selection, or resource ownership can produce subtle false failures.

## Test Signals
Success is signaled by exact VMA placement, `drm_mm_node` allocation state, expected `-EINVAL`/`-ENOSPC` errors for invalid requests, no stale mappings after unbind, correct direct GGTT reads after `insert_page`, and clean mock/live subtest completion. Failures log detailed offsets, sizes, expected placements, and errnos.

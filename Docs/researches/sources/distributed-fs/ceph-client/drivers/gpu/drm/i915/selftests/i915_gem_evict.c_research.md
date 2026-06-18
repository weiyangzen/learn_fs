# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_gem_evict.c

Purpose: Mock and live selftests for GEM/GGTT eviction behavior under full, pinned, color-constrained, VM-wide, overcommit, and context-allocation pressure scenarios.

Important APIs/functions: `i915_gem_evict_mock_selftests()`, `i915_gem_evict_live_selftests()`, `igt_evict_something()`, `igt_overcommit()`, `igt_evict_for_vma()`, `igt_evict_for_cache_color()`, `igt_evict_vm()`, and `igt_evict_contexts()`.

Control flow: Mock tests fill GGTT with page-sized internal objects marked by a tiling quirk for cleanup ownership. They verify eviction fails while objects are pinned, succeeds after unpinning, fails overcommit pinning, handles fixed-node eviction, respects cache-color constraints, and evicts whole VMs under a ww context. Live context test reserves/fills GGTT with unevictable nodes to simulate small space, creates many contexts/requests per engine with submission held by a fence, and verifies request/context construction triggers eviction rather than unexpected allocation failures.

State/persistence: Temporarily fills GGTT bound lists, pins/unpins VMAs, mutates `ggtt->vm.mm.color_adjust`, reserves DRM MM nodes, uses `igt_evict_ctl.fail_if_busy`, and holds runtime PM during live context pressure. Cleanup drains freed objects and removes reserved nodes.

Dependencies/integration: GEM internal objects, GGTT VM insertion/eviction, DRM MM, cache coloring/PAT indices, software fences, contexts, GT idle waits, runtime PM, mock GEM device, and `igt_flush_test`.

Risks: Cleanup depends on tiling quirk as an ownership marker and must clear all pinned VMAs. Changing color-adjust semantics or GGTT cache-color policy can invalidate assumptions. Live test is meaningful only with full PPGTT and skips otherwise. Unevictable reservations must always be removed to avoid corrupting subsequent tests.

Test signals: Explicit error messages for unexpected `-ENOSPC`/`-EBUSY`, failed eviction calls, color eviction mistakes, GT idle failures, and request allocation errors under pressure.

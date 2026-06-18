# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/huge_pages.c

## Purpose
Tests i915 GEM huge-page handling for 4K, 64K, and 2M pages across mock and live PPGTT paths. It validates page-size selection, scatterlist construction, memory-region huge-page masks, misaligned DMA behavior, compact/mixed page tables, THP fallback, object shrink, and GPU/CPU readback.

## APIs And Control Flow
Key helpers are `hugepage_ctx()`, `get_huge_pages()`, `huge_pages_object()`, fake huge-page object ops, `igt_check_page_sizes()`, `gpu_write()`, and `cpu_check()`. Mock entry `i915_gem_huge_page_mock_selftests()` builds a 48-bit PPGTT and checks supported page sizes and 64K scratch. Live entry `i915_gem_huge_page_live_selftests()` runs shrink, tmpfs fallback, smoke, compact, mixed, fill, and 64K tests when PPGTT is available and the GT is not wedged.

## State, Dependencies, Integration, Risks, And Tests
State is transient in GEM objects, sg tables, VM page tables, scratch pages, and request fences. Dependencies include GEM region/lmem/internal APIs, PPGTT VM helpers, mock device/region helpers, random test utilities, and `igt_gem_utils`. Risks center on memory-pressure-sensitive allocations, page-size mask accounting, 64K scratch scrubbing, mixed compact mappings, and CPU cache flushing. Test signals are page-size mismatch logs, GPU write/readback mismatch, missing scratch pages, THP fallback/shrink failures, and expected skips without PPGTT.

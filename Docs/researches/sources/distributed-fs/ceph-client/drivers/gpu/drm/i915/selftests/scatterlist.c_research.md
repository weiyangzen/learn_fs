# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/scatterlist.c

Purpose: selftests Linux/i915 scatter-gather table allocation, iteration, and trimming behavior over varied segment layouts.

Important APIs/functions: `alloc_table()` constructs an `sg_table` with synthetic contiguous PFNs and variable segment lengths. `expect_pfn_sg()`, `expect_pfn_sg_page_iter()`, and `expect_pfn_sgtiter()` verify order and lengths through `for_each_sg`, `for_each_sg_page`, and `for_each_sgt_page`. Segment generators include `one`, `grow`, `shrink`, `random`, and `random_page_size_pages`. `igt_sg_alloc()` validates `sg_alloc_table()`. `igt_sg_trim()` validates `i915_sg_trim()`. `scatterlist_mock_selftests()` registers both subtests.

Control flow and state: tests iterate over prime sizes and offsets to stress boundary behavior around continuation allocations. The PRNG is reseeded with `i915_selftest.random_seed` before allocation and verification so expected lengths match. Timeouts use `IGT_TIMEOUT` and `igt_timeout()` to avoid unbounded loops.

Dependencies and integration: depends on Linux scatterlist/page iteration APIs, prime-number iteration, pseudo-random state, and i915 selftest utilities. It specifically exercises `i915_sg_trim()` and generic scatterlist allocation limits.

Risks: relies on `pfn_to_page()` contiguity in sparse memory; if the synthetic PFN range is not contiguous, tests return `-ENOSPC` and stop that variant. Very large segment lengths are constrained to avoid overflowing `sg->length`.

Test signals: pass means all three iteration APIs traverse the expected PFN span and trimmed tables retain expected `nents/orig_nents` and page ordering.

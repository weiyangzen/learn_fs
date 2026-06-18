# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/i915_gem_coherency.c

## Purpose
Stress-tests GEM cache-domain coherency by mixing CPU, GGTT, write-combined, and GPU store-dword writes/reads to the same cachelines.

## APIs And Control Flow
`struct context` carries the object and engine, while `struct igt_coherency_mode` defines access-mode callbacks. Core callbacks are `cpu_set/get()`, `gtt_set/get()`, `wc_set/get()`, and `gpu_set()`. `igt_gem_coherency()` selects a random engine, iterates overwrite/write/read mode triples, writes stale inverse values, overwrites them with random values, and verifies every valid reader over prime-sized cacheline subsets.

## State, Dependencies, Integration, Risks, And Tests
State is transient in a one-page object, cache-domain metadata, GGTT iomaps, WC maps, and request fences. Dependencies include prepare/finish access, clflush, GGTT pinning, engine PM, `MI_STORE_DWORD_IMM`, and random helpers. Risks are missing clflush-before/after handling, domain transition bugs, GPU write ordering mistakes, and invalid skips for fence/store-dword support. Test signals name the overwrite/write/read modes and offset on value mismatch.

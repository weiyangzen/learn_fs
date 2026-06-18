# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_bo.c

## Purpose

`xe_bo.c` contains live KUnit tests for Xe buffer-object behavior: flat-CCS migration preservation/clearing, global VRAM eviction and restoration, and TTM shrinker/swap behavior for system BOs.

## Important APIs, Types, and Functions

- CCS migration path: `ccs_test_migrate`, `ccs_test_run_tile`, `ccs_test_run_device`, and `xe_ccs_migrate_kunit`.
- Eviction path: `evict_test_run_tile`, `evict_test_run_device`, and `xe_bo_evict_kunit`.
- Shrinker path: `struct xe_bo_link`, `shrink_test_fill_random`, `shrink_test_verify`, `shrink_test_run_device`, and `xe_bo_shrink_kunit`.
- Suites: exported `xe_bo_test_suite` and `xe_bo_shrink_test_suite`.

## Control Flow

The CCS test creates a user BO, validates it into VRAM where applicable, optionally clears data and CCS via `xe_migrate_clear`, evicts it to system memory with `xe_bo_evict`, waits on reservation fences, maps the TTM backing pages, checks first/last CCS values, and writes values for the next round. It skips unsupported flat-CCS or Xe2+ discrete cases as needed.

The eviction test creates VM-backed and external BOs, pins the external BO, calls `xe_bo_evict_all`, sanitizes and resets GTs, restores kernel and user BOs, then checks that pinned external BOs remain in VRAM while normal BOs are evicted. The shrinker test allocates roughly twice free RAM in 64 MiB system BOs, marks some purgeable when swap is insufficient, fills non-purgeable BOs with deterministic PRNG data, validates/readbacks under shrink pressure, and reports interrupted/successful readbacks.

## State and Persistence Behavior

The tests mutate live device memory placement, BO TTM resources, reservation fences, VM state, GT reset state, purgeable accounting, and runtime PM state. BO data and CCS metadata are expected to persist correctly across migration, eviction, restore, and shrinker pressure unless intentionally purgeable.

## Dependencies and Integration Points

It depends on live Xe devices from `xe_pci_live_device_gen_param`, KUnit helpers for runtime PM, BO creation/locking/validation, `xe_bo_evict`, `xe_bo_restore_early/late`, migration clear, GT reset/sanitize, TTM swap/shrinker behavior, PRNG helpers, and sysinfo/swap accounting.

## Risks and Edge Cases

- These are live tests and can be slow or disruptive, especially shrinker and GT reset flows.
- Shrinker coverage depends on available RAM/swap and skips large-memory systems to avoid excessive runtime.
- CCS validation inspects only first and last values in the first CCS page, so middle-page corruption can escape.
- Eviction test comments call out CTB/ADS snapshot risk and compensates with GT reset; failures can indicate fragile restore ordering.

## Test Signals

Passing live suites indicate CCS metadata survives migration, clears correctly, pinned external BOs resist eviction, user BOs restore from eviction, and non-purgeable system BO contents survive shrink pressure. Timeouts, wrong placement, PRNG mismatch, or restore errors are strong regression signals.

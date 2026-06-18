# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_id_mgr.c

## Purpose
Implements a GuC context ID manager for normal submission allocation and SR-IOV PF range provisioning.

## Important APIs, Types, And Functions
Exports `xe_guc_id_mgr_init`, locked reserve/release APIs, unlocked PF reserve/release APIs, and `xe_guc_id_mgr_print`. Internal helpers include `find_last_zero_area`, `idm_reserve_chunk_locked`, `idm_release_chunk_locked`, and `__fini_idm`.

## Control Flow
Initialization validates the requested limit, converts `~0` to `GUC_ID_MAX`, allocates a bitmap, records total count, and registers DRM-managed cleanup. Normal submission reservations search from low IDs. PF reservations with a nonzero retain requirement first ensure `used + count + retain <= total`, then reserve the highest suitable free range to leave low IDs available. Release checks bounds and bit state in debug builds, clears bits, and decrements `used`.

## State And Persistence
State is `idm->bitmap`, `idm->total`, and `idm->used`, protected by `guc->submission_state.lock`. The manager persists until DRM cleanup; teardown reports unclean allocations when debug is enabled.

## Dependencies And Integration Points
Depends on bitmap helpers, DRM managed cleanup, GuC submission lock, `GUC_ID_MAX`, and GT printing/assertion helpers. It backs GuC execution queue IDs and PF-to-VF context ID partitioning.

## Risks And Test Signals
`used` must remain synchronized with bitmap state; double release or out-of-range release is caught only by assertions. High-end PF allocations intentionally differ from low-end submission allocations, so tests should verify both strategies. Built-in KUnit coverage is included through `tests/xe_guc_id_mgr_test.c`.

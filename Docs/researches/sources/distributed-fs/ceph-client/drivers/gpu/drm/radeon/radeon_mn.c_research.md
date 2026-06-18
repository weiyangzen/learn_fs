<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_mn.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_mn.c

## Purpose

`radeon_mn.c` connects Radeon userptr buffer objects to the Linux MMU interval-notifier API. It registers notifiers for user-backed BO address ranges, invalidates GPU bindings when the CPU page tables change, waits for outstanding GPU use, migrates affected BOs back to CPU/system placement, and unregisters notifiers during BO cleanup.

## Important APIs, Types, and Functions

- `radeon_mn_invalidate()`: MMU interval invalidation callback for one BO. It checks whether the BO has a bound TTM TT, rejects non-blockable invalidations by returning `false`, reserves the BO, waits on its reservation object, changes placement to `RADEON_GEM_DOMAIN_CPU`, validates/migrates it through TTM, and unreserves it.
- `radeon_mn_ops`: `mmu_interval_notifier_ops` table pointing at the invalidate callback.
- `radeon_mn_register(struct radeon_bo *bo, unsigned long addr)`: inserts the interval notifier for `current->mm`, the user address, and `radeon_bo_size(bo)`, then starts an interval read sequence.
- `radeon_mn_unregister(struct radeon_bo *bo)`: removes the notifier if registered and clears `bo->notifier.mm`.

## Control Flow

Registration is called when a Radeon BO wraps user memory. The notifier watches the user virtual range in the current process. When the MM subsystem invalidates that range, the callback first ignores BOs that are not bound into GPU-visible TT memory. If the invalidation cannot block, it returns `false` so the MMU notifier core can retry in a blockable context. In blockable mode it reserves the BO, waits indefinitely for bookkeeping usage on the reservation object, switches allowed placement to CPU, validates the TTM BO to unbind/move it, logs errors, unreserves, and returns `true`.

Unregister is idempotent and does nothing when no `mm` is recorded. After removal it clears the pointer to prevent duplicate unregister attempts.

## State and Persistence Behavior

The persistent state is the `mmu_interval_notifier` embedded in `struct radeon_bo` and the BO's TTM placement/binding. Invalidation may persistently move the BO out of GPU/GTT placement into CPU/system memory. Reservation fences and waits coordinate with in-flight GPU work before CPU page-table changes are allowed to proceed.

## Dependencies and Integration Points

This file depends on Linux `mmu_interval_notifier`, TTM BO validation, Radeon BO reserve/unreserve and placement helpers, Radeon TTM userptr binding checks, DMA reservation waits, and current process `mm`. It is integrated with GEM userptr BO creation and cleanup.

## Risks and Edge Cases

- The source contains an explicit FIXME: Radeon appears to allow `get_user_pages` during invalidate start/end and should use the full `mmu_interval_read_begin()` scheme around GUP reads for safe PTE sampling.
- Invalidation waits with `MAX_SCHEDULE_TIMEOUT`; stuck GPU work or reservation misuse can stall mm invalidation.
- Errors during reserve, wait, or validate are logged but the callback generally returns `true`, so the MM path may continue after a failed migration.
- Registration uses `current->mm`; callers must ensure this is the owning mm for the userptr range.
- Non-blockable invalidations rely on the core retrying later; incorrect caller assumptions can cause missed unbinding.

## Test Signals

Test with userptr BOs under munmap, mremap, fork/exit, swap, memory pressure, and concurrent GPU access; invalidation from blockable and non-blockable paths; forced TTM validation failure; BO cleanup idempotent unregister; lockdep coverage for reservation inside mmu notifier callbacks; and stress tests for userptr command submission while CPU mappings change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_mn.c -->

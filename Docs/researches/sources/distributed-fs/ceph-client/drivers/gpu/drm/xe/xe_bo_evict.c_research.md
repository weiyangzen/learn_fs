# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_bo_evict.c

## Purpose
This file coordinates whole-device BO eviction and restoration for suspend, hibernate, runtime PM transitions, and PCI removal. It is the list-management layer over per-BO helpers in `xe_bo.c`, especially for pinned VRAM objects that TTM cannot evict normally.

## Important APIs, Types, and Functions
Public entry points are `xe_bo_notifier_prepare_all_pinned`, `xe_bo_notifier_unprepare_all_pinned`, `xe_bo_evict_all_user`, `xe_bo_evict_all`, `xe_bo_restore_early`, `xe_bo_restore_late`, `xe_bo_pci_dev_remove_all`, and `xe_bo_pinned_init`. The key internal helper is `xe_bo_apply_to_pinned`, which safely walks pinned lists while dropping the spinlock around slow BO operations.

## Control Flow
Pinned-list operations take a BO reference, move the entry to a temporary list, drop `xe->pinned.lock`, run the requested callback, then splice entries into a destination list. Suspend first evicts non-pinned user BOs via TTM, then pinned external and late kernel BOs, waits for migrate engines, and finally evicts early kernel BOs. Resume restores early BOs before GT init, then late kernel/external BOs after migrate engines are available, remapping GGTT entries where needed. PCI remove evicts/purges normal BOs and dma-unmaps pinned BOs.

## State and Persistence Behavior
The file owns transitions among `xe->pinned.early.kernel_bo_present`, `early.evicted`, `late.kernel_bo_present`, `late.evicted`, and `late.external`. It preserves pinned BO contents through backup/restore and ensures remaining pinned DMA mappings are dropped on teardown. The lists are volatile runtime state but determine whether VRAM contents survive power loss.

## Dependencies and Integration Points
It integrates with TTM resource managers, `xe_bo_evict_pinned`, `xe_bo_restore_pinned`, `xe_bo_notifier_prepare_pinned`, GGTT remapping, tile migrate waits, PM notifier paths in `xe_pm.c`, and PCI remove in `xe_device_remove`.

## Risks
Ordering is critical: early BOs may be required before GT/migrate engines are available, while late BOs can use GPU copies. List movement must handle races with unpinning during PM notifier callbacks. Missing migrate waits can leave backup/restore copies incomplete. PCI removal deliberately purges many BOs, so only exported/pagemap-relevant data should be preserved.

## Test Signals
Suspend/resume on DGFX, hibernation with flat CCS, external pinned dma-buf scenarios, forced PCI removal/unplug, PM notifier failure injection, list-state assertions after pin/unpin, and migrate-engine wait coverage are important signals.

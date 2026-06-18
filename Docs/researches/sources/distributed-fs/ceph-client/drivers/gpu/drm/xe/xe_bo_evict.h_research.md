# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_bo_evict.h

## Purpose
This header declares the Xe whole-device BO eviction/restoration API used by PM and device teardown code.

## Important APIs, Types, and Functions
It exposes `xe_bo_evict_all`, `xe_bo_evict_all_user`, pinned notifier prepare/unprepare functions, early and late restore functions, `xe_bo_pci_dev_remove_all`, and `xe_bo_pinned_init`.

## Control Flow
There is no executable flow in the header. The declared functions represent explicit lifecycle phases: initialize pinned tracking, prepare pinned backups, evict user/all BOs, restore early/late pinned BOs, undo prepare state, and remove PCI-device mappings.

## State and Persistence Behavior
The header stores no state but gives callers access to state transitions in `xe->pinned` lists and pinned BO backup objects.

## Dependencies and Integration Points
It forward-declares `struct xe_device` and is consumed by PM, debug, and device lifecycle code. It pairs with `xe_bo.c` per-object helpers and `xe_bo_evict.c` list orchestration.

## Risks
Misordering declared phases can lose VRAM contents or attempt GPU-assisted restore before GT/migrate infrastructure is available. Signature drift would break PM integration at build time.

## Test Signals
Build coverage, system suspend/resume, hibernate, PCI remove, and DGFX pinned BO tests validate that these hooks stay wired correctly.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt.h

## Purpose
Declares the core GT API, engine iteration helpers, reset wrappers, GT type helpers, and selected topology/engine macros.

## Important APIs and Macros
- `for_each_hw_engine` iterates valid hardware engines in `gt->hw_engines`.
- `RCS_INSTANCES`, `VCS_INSTANCES`, `VECS_INSTANCES`, `CCS_INSTANCES`, and `GSCCS_INSTANCES` derive instance masks from `gt->info.engine_mask`.
- Lifecycle/reset declarations mirror `xe_gt.c`.
- Inline helpers identify main/media GTs, USM-reserved hardware engines, indirect ring-state support, and VF recovery pending state.
- `xe_fault_inject_gt_reset` exposes debugfs fault injection when configured.

## Integration and Risks
This header is broadly included by Xe subsystems. Macros assume valid GT info masks and stable enum bit layout. `xe_gt_reset` is synchronous only because it queues and then flushes reset work; callers must be prepared for PM and reset side effects.

## Test Signals
Compilation across PF/VF and debugfs-disabled configs is important because inline helpers depend on configuration and included SR-IOV VF declarations.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_klv_thresholds_set_types.h

## Purpose
Defines the single macro list of tracked GuC VF adverse-event threshold KLVs and derives the count and enum indexes from it.

## Important APIs, Types, And Functions
`MAKE_XE_GUC_KLV_THRESHOLDS_SET` lists thresholds for CAT errors, engine resets, page faults, H2G storms, IRQ storms, doorbell storms, and multi-LRC count with a firmware-version annotation. `XE_GUC_KLV_NUM_THRESHOLDS` computes the count, and `enum xe_guc_klv_threshold_index` generates indexes.

## Control Flow
There is no runtime flow. Other headers expand the macro list to generate switch cases, string names, and indexes.

## State And Persistence
No state is stored; this file is a compile-time source of truth.

## Dependencies And Integration Points
Depends on `xe_args.h` macro utilities. Integrated with KLV stringification and threshold key/index helpers.

## Risks And Test Signals
Adding a threshold in one place updates generated users, but ABI key and length definitions must exist. Compile-time failures catch missing ABI constants; round-trip conversion tests catch ordering or count mistakes.

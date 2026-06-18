# File Research: sources/block-storage/lvm2/lib/vdo/vdo.c

## Purpose
Implements LVM2 segment-type support for VDO. It registers `vdo` logical volumes layered on VDO pools and `vdo-pool` segments backed by data LVs, handles VDO metadata import/export, device-mapper target construction, kernel feature probing, and optional dmeventd monitoring.

## Main Responsibilities
- `vdo` segment:
  - Represents a linear mapping onto a VDO pool after the pool header.
  - Imports/exports `vdo_pool` and `vdo_offset`.
  - Emits a linear/striped target area pointing at the backing VDO pool device.
- `vdo-pool` segment:
  - Stores data LV, header size, virtual extents, and full `dm_vdo_target_params`.
  - Imports/exports compression, deduplication, metadata hints, IO size, block-map/cache/index/slab sizing, thread counts, discard size, sparse index, and write policy.
  - Emits the actual dm-vdo target and uses the VDO virtual size rather than physical LV size.

## Key Functions
- `_vdo_text_import()` attaches the VDO LV to its VDO pool LV and marks the LV as `LV_VDO`.
- `_vdo_add_target_line()` builds a linear mapping onto the VDO pool, offset by header size plus logical extent offset.
- `_vdo_pool_text_import()` reads the data LV and VDO parameters, attaches the data LV as `LV_VDO_POOL_DATA`, marks the pool, and hides the data LV.
- `_vdo_pool_text_export()` serializes all VDO pool parameters.
- `_vdo_check()` computes incremental pool-size constraint deltas and calls `check_vdo_constraints()`.
- `_vdo_pool_add_target_line()` builds the dm-vdo target with target format version 2 or 4 depending on feature support.
- `_vdo_target_present()` requires a sufficiently new VDO target, checks linear/striped target availability, derives feature bits, and applies `global/vdo_disabled_features`.
- `init_vdo_segtypes()` registers both `vdo` and `vdo-pool`.

## Feature Gates
- Minimum VDO target version is effectively 6.2.x.
- `VDO_FEATURE_ONLINE_RENAME` requires target version 6.2.3.
- `VDO_FEATURE_VERSION4` requires target version 8.2.0.
- Feature bits can be disabled by `global/vdo_disabled_features`.

## Edge Cases and Invariants
- `minimum_io_size` is stored in target params as sectors but serialized as bytes.
- VDO pool target construction skips constraint checking during critical sections.
- VDO requires the VDO target and linear/striped mapping support.
- The pool handler may gain `SEG_MONITORED` if a dmeventd VDO DSO is configured.

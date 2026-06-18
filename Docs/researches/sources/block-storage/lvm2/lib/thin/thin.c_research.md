# File Research: sources/block-storage/lvm2/lib/thin/thin.c

## Purpose
Implements LVM2 segment-type support for device-mapper thin provisioning. It registers both `thin-pool` and `thin` segment types, imports/exports their text metadata, builds activation-time device-mapper table lines, probes kernel target feature support, and wires optional dmeventd monitoring for thin pools.

## Main Responsibilities
- `thin-pool` segment:
  - Stores pool metadata LV, pool data LV, transaction id, chunk size, discard behavior, zero-new-blocks behavior, crop-metadata state, and queued thin-pool messages.
  - Imports metadata keys such as `metadata`, `pool`, `transaction_id`, `chunk_size`, `discards`, `zero_new_blocks`, `crop_metadata`, and message blocks.
  - Exports the same state back to LVM text metadata.
  - Builds a `thin-pool` target line with low-water-mark, discard settings, no-space behavior, metadata cropping, and queued create/delete/set-transaction messages.
- `thin` segment:
  - Stores its pool LV, transaction id, device id, optional origin, optional external origin, and optional merge LV.
  - Exports/imports `thin_pool`, `transaction_id`, `device_id`, `external_origin`, `origin`, and `merge`.
  - Builds a `thin` target line pointing to the pool and device id, with special handling for merging thin snapshots and external origins.

## Key Functions
- `_thin_pool_text_import()` validates pool metadata/data LV references, chunk size bounds, discard mode, zeroing, crop metadata, and message blocks.
- `_thin_pool_text_export()` serializes pool configuration and validates message consistency before writing message blocks.
- `_thin_pool_add_target_line()` converts pool metadata into a dm tree node using `dm_tree_node_add_thin_pool_target_v1()`, applies discard/no-space options, and sends queued pool messages when requested by activation options.
- `_thin_text_import()` resolves pool/origin/external-origin/merge LVs and attaches the thin LV to its pool.
- `_thin_add_target_line()` emits the thin target and external-origin dependency when present.
- `_thin_target_present()` probes the `thin-pool` kernel target version, derives feature bits, and applies `global/thin_disabled_features`.
- `init_multiple_segtypes()` / `init_thin_segtypes()` register `thin-pool` and `thin`.

## Important Data Flow
Text metadata import attaches related LVs into `lv_segment`, then activation asks the segtype handler to produce dm-table nodes. Thin-pool activation also converts pending LVM metadata messages into dm-thin messages and finally sends a transaction-id update after all messages.

## Feature Gates
Kernel target feature detection controls:
- discard support
- external origin support
- non-power-of-two chunk sizes
- metadata resize
- error-if-no-space
- smaller external origin extension

Runtime configuration can mask detected features through `global/thin_disabled_features`.

## Edge Cases and Invariants
- Thin pool chunk size must be within `DM_THIN_MIN_DATA_BLOCK_SIZE` and `DM_THIN_MAX_DATA_BLOCK_SIZE`.
- Non-power-of-two chunk sizes require target support.
- Device ids above `DM_THIN_MAX_DEVICE_ID` are rejected.
- Thin-pool messages are only added when activation options allow message sending.
- External-origin LVs smaller than the thin LV require `THIN_FEATURE_EXTERNAL_ORIGIN_EXTEND`.
- Thin snapshot merge is represented by swapping device ids rather than emitting a distinct merge target.

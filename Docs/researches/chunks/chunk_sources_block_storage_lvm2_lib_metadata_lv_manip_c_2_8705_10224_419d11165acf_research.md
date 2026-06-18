# Chunk Research: sources/block-storage/lvm2/lib/metadata/lv_manip.c lines 8705-10224

## Scope

This chunk covers the tail of pvmove/layer insertion helpers, LV wiping helpers, activation-skip policy, feature validation, and the main single-LV creation path.

## APIs and Entry Points

- `insert_layer_for_segments_on_pv()` inserts a mapping layer under selected `lv_where` segments after pvmove size splitting and PE-range boundary alignment.
- `wipe_lv()` wipes signatures and/or initializes an active LV, using `BLKZEROOUT` when possible and `dev_set_bytes()` as fallback.
- `activate_and_wipe_lvlist()` validates, activates, wipes, and deactivates a list of visible writable LVs.
- `activate_and_wipe_lv()` wraps the list path for one LV.
- `lv_set_activation_skip()` sets/clears `LV_ACTIVATION_SKIP`, defaulting thin snapshots to skip when configured.
- `lv_activation_skip()` decides whether activation should be skipped; deactivation is never skipped.
- `lv_create_single()` handles implicit pool creation, then delegates final LV creation to `_lv_create_an_lv()`.

## Key Control Flow

Pvmove/layer insertion:
1. Split oversized pvmove segments using `allocation_pvmove_max_segment_size_mb_CFG`.
2. Align segment boundaries to selected PE ranges.
3. Record affected lock-holder LVs in `lvs_changed`.
4. Move matching segment areas into `layer_lv` via `_extend_layer_lv_for_segment()`.

Wiping:
1. Require active local LV.
2. Resolve `/dev/<vg>/<lv>`, open read-write via label scan.
3. Optionally wipe known signatures.
4. Zero metadata fully or only initial sectors depending on config.
5. Invalidate label scan and clear `LV_NOSCAN` on success.

LV creation:
1. Validate duplicate names, VG feature support, activation support, stripe size, extents, pool size, and PV count.
2. Resolve pools/origins and classify thin/cache/VDO/snapshot behavior.
3. Create and extend the LV, then apply type-specific setup.
4. Write/commit VG metadata before activation.
5. Activate, wipe, and finalize VDO/cache/snapshot conversions.
6. Revert through centralized deactivate/unlock/remove paths where possible.

## State and Dependencies

Mutated state includes segment lists, LV sizes, `lvcreate_params`, thin pool transaction/device IDs, pool messages, and flags such as `LV_NOSCAN`, `LV_TEMPORARY`, `LV_ACTIVATION_SKIP`, `LV_NOAUTOACTIVATE`, `LV_NOTSYNCED`, `LVM_WRITE`, and `FIXED_MINOR`.

Major dependencies include dev-cache/label-scan wiping APIs, `lv_create_empty()`, `lv_extend()`, `vg_write()/vg_commit()`, activation/deactivation helpers, thin/cache/VDO conversion helpers, and lockd operations.

## Risks and Edge Cases

- Pvmove max segment size conversion can truncate from `uint64_t` to `uint32_t`.
- Stripe alignment can exceed the configured max segment size to preserve stripe boundaries.
- Segment splitting mutates lists while iteration still uses the original `seg`.
- Some `wipe_lv()` failure paths do not visibly call `label_scan_invalidate()`.
- Full metadata zeroing passes a shifted size through `size_t`, risking truncation on narrow platforms.
- `activate_and_wipe_lvlist()` deactivates all listed LVs, including ones already active before entry.
- `_lv_create_an_lv()` has many partial-state exits; not all go through full revert.
- Thin snapshot failure handling manually restores transaction IDs with acknowledged uncertainty.
- Cache/snapshot/VDO finalization paths include manual-intervention cases on failure.
- Revert skips `lv_remove()` for `lvconvert`, intentionally leaving possible abandoned LVs.

## Cross-Chunk References

- `_match_seg_area_to_pe_range()` begins before this chunk and is completed at the start of it.
- `_extend_layer_lv_for_segment()` is defined immediately before this chunk and performs the actual layer remapping.
- `_round_to_stripe_boundary()` is called here but defined earlier.
- Higher-level `lv_create_single()` callers and later orchestration are outside this chunk.
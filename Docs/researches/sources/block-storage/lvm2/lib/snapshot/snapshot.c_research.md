# File Research: sources/block-storage/lvm2/lib/snapshot/snapshot.c

## Purpose

`snapshot.c` implements the LVM segment type handler for snapshot volumes, including metadata import/export, device-mapper target selection/status, module requirements, dmeventd monitoring hooks, and segment type initialization.

## Metadata Import/Export

- `_snap_text_import()` reads `chunk_size`, `origin`, and either `cow_store` or `merging_store` from text metadata.
- It validates that both COW and merging stores are not specified at the same time.
- It resolves origin and COW LVs via `find_lv()` and initializes the segment with `init_snapshot_seg()`.
- `_snap_text_export()` writes `chunk_size`, `origin`, and either `cow_store` or `merging_store` depending on `MERGING` status.

## Device-Mapper Support

When `DEVMAPPER_SUPPORT` is enabled:

- `_snap_target_name()` returns `snapshot-merge` during merge activation unless `laopts->no_merging` is set; otherwise it returns the normal segment target name.
- `_snap_target_status_compatible()` accepts `snapshot-merge` status.
- `_snap_target_percent()` parses snapshot target status, reports invalid/merge-failed states, accumulates used/total sectors, handles metadata-only cases as 0%, and reports full devices as 100%.
- `_snap_target_present()` caches target availability checks for `snapshot`, `snapshot-origin`, and conditionally `snapshot-merge`; it also records `SNAPSHOT_FEATURE_FIXED_LEAK` based on target version.
- `_snap_modules_needed()` adds the snapshot kernel module name to the module list.

## Dmeventd Hooks

When `DMEVENTD` is enabled:

- `_target_registered()` checks monitoring registration for the COW LV.
- `_target_set_events()` registers/unregisters events through the snapshot DSO with a fixed timeout.
- `_target_register_events()` and `_target_unregister_events()` wrap event toggling.

## Segment Type Registration

`_snapshot_ops` wires import/export, target/status/presence/percent/module, dmeventd, and destroy callbacks.

`init_snapshot_segtype()` or shared-object `init_segtype()` allocates and initializes a `struct segment_type` with:

- name `SEG_TYPE_NAME_SNAPSHOT`
- flags `SEG_SNAPSHOT | SEG_CANNOT_BE_ZEROED | SEG_ONLY_EXCLUSIVE`
- optional `SEG_MONITORED` when a dmeventd DSO path is configured.

## Important Edge Cases

- Snapshot metadata import rejects missing or incorrectly typed `origin`/COW entries.
- Merge target presence is checked only for merging snapshot segments.
- Target support checks are cached statically for process lifetime.

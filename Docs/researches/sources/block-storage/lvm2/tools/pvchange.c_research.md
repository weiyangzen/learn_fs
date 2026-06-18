# File Research: sources/block-storage/lvm2/tools/pvchange.c

## Purpose

`pvchange.c` implements `pvchange`, which mutates attributes of existing physical volumes: allocatability, tags, metadata-ignore state, and PV UUID.

## Main Entry Points

- `pvchange()`: validates command options, prepares processing state, handles global locking/hints for UUID changes, and calls `process_each_pv()`.
- `_pvchange_single()`: applies the requested changes to one PV and writes either VG metadata or standalone PV metadata.

## Supported Mutations

- `--allocatable`: sets or clears `ALLOCATABLE_PV`.
- `--addtag` / `--deltag`: changes PV tags, only when the PV is in a VG that supports tags.
- `--metadataignore`: toggles PV metadata area ignore state, with confirmation when overriding VG metadata copy preferences.
- `--uuid`: creates a new random PV UUID and updates both PV/VG metadata and the devices file entry when present.

## Safety Checks

- Rejects invocation without any mutation option.
- Requires either PV paths, `--all`, or selection.
- Rejects mixing `--all` with explicit PV paths.
- Blocks VG updates when duplicate PV devices exist unless config explicitly allows changes.
- For UUID changes, rejects duplicate-PV situations and active LVs in the containing VG.
- For orphan PVs, rejects tag changes and requires `-ff` if the PV appears used by a VG but metadata is missing.
- Converts the global lock to exclusive when mutating orphan PVs.

## Metadata Commit Behavior

- Non-orphan PV changes are written through `vg_write()` and `vg_commit()`, followed by `backup(vg)`.
- Orphan PV changes are written with `pv_write()`.
- UUID changes on non-orphan PVs first call `pv_write(cmd, pv, 1)` with the old ID saved in `pv->old_id`.

## Devices File Integration

When changing a UUID:

- `cmd->edit_devices_file` is enabled.
- The global lock is taken exclusive before clearing hints to preserve lock ordering.
- `get_du_for_pvid()` locates the existing devices-file record.
- After commit, the record's PVID is updated and `device_ids_write()` persists it.

## Output and Accounting

`pvchange_params` tracks total processed and changed PVs. The command prints a final changed/not-changed summary.

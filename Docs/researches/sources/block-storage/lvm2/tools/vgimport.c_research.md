# File Research: sources/block-storage/lvm2/tools/vgimport.c

Purpose: implements `vgimport`, clearing exported state from VGs/PVs and optionally assigning local system ID or starting persistent reservations.

Read coverage: complete file read, 112 lines.

Key responsibilities:
- Requires explicit VGs, selection, or `-a`; rejects combining `-a` with names/selection.
- Validates that the VG is exported and not partial unless `--force` enables missing-PV handling.
- Clears `EXPORTED_VG` from the VG and all PVs.
- For non-shared VGs, assigns the local command system ID when configured.
- Runs `persist_start_include()` before metadata write when persistent reservation start is requested.
- Writes and commits metadata, reports success, and invalidates hints.

Dependencies:
- Uses VG exported/partial status checks, persistent reservation include helper, hint invalidation, and process-each-VG update flow.

Risks and edge cases:
- `--force` is intentionally required to import partial VGs to avoid accidental import when disks were forgotten.
- `--persist start` disables PR-required checks during read so PR can be started before the imported VG metadata is written.

# File Research: sources/block-storage/lvm2/tools/pvdisplay.c

## Purpose

`pvdisplay.c` implements the legacy `pvdisplay` views and dispatches columnar output to `pvs`.

## Main Entry Points

- `pvdisplay_cmd()`: traditional per-PV display path using `process_each_pv()`.
- `pvdisplay_columns_cmd()`: columnar/reporting path; delegates to `pvs()`.
- `pvdisplay()`: placeholder that reports an internal command-definition error.

## Per-PV Display Behavior

`_pvdisplay_single()`:

- Computes displayed size as full PV size for orphan PVs.
- Computes free size for PVs in a VG as `(pe_count - pe_alloc_count) * pe_size`.
- `--short` prints only capacity.
- Warns for exported VG membership.
- Identifies orphan PVs as new physical volumes.
- Uses colon output via `pvdisplay_colons()` when `--colon` is set.
- Uses full output via `pvdisplay_full()` otherwise.
- Prints segment maps with `pvdisplay_segments()` when `--maps` is set.

## Column Mode Behavior

`pvdisplay_columns_cmd()` disables hints when `--all` is set because that mode needs to inspect all devices, including non-hinted devices, then delegates to `pvs()`.

## Design Note

This file is mostly command glue; formatting and report generation live in shared display/report helpers.

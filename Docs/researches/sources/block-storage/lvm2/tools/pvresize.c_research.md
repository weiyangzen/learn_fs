# File Research: sources/block-storage/lvm2/tools/pvresize.c

## Purpose

`pvresize.c` implements `pvresize`, resizing or updating PV size metadata for one or more physical volumes.

## Main Entry Points

- `pvresize()`: validates arguments, parses requested new size, prepares a processing handle, and calls `process_each_pv()`.
- `_pvresize_single()`: applies resize to one PV.

## Flow

- Requires at least one PV argument.
- Rejects negative `--setphysicalvolumesize`.
- Stores requested size in `pvresize_params.new_size`; zero means auto-detect/default behavior in lower layers.
- Enables PV notification with `set_pv_notify()`.
- Uses `READ_FOR_UPDATE` while processing PVs.
- For orphan PVs, converts the global lock to exclusive because orphan metadata is being changed.
- Calls `pv_resize_single(cmd, vg, pv, new_size, yes_count)` for actual resize logic.
- Tracks total and successful PVs and prints a summary.

## Delegated Behavior

This file does not implement the actual resizing algorithm. Space validation, metadata updates, and prompts are handled by `pv_resize_single()`.

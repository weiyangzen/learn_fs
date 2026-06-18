# File Research: sources/block-storage/lvm2/tools/pvmove.c

## Purpose

`pvmove.c` implements setup and command orchestration for `pvmove`, which relocates extents off a source PV by temporarily inserting mirror layers, activating affected LVs, updating metadata, and then using the polling framework to complete or abort the move.

## Main Entry Points

- `pvmove()`: command entry. Validates target support and lockd/lvmpolld constraints, parses source PV and optional destination PVs/LV name, runs setup or abort discovery, releases global lock, then calls `pvmove_poll()`.
- `pvmove_poll()`: wraps `poll_daemon()` with pvmove-specific callbacks.
- `_pvmove_setup_single()`: sets up a new pvmove or resumes an existing one for a source PV.
- `_pvmove_read_single()`: used for abort mode to locate an in-progress pvmove.

## Setup Flow

For a new pvmove:

- Parse and normalize the source PV argument, including PE ranges after colon syntax.
- Optional `--name` can target one LV; `_extract_lvname()` accepts `/dev/vg/lv`, `vg/lv`, or `lv`.
- Build the source PV list with `create_pv_list()`.
- Build destination allocation candidates with `_get_allocatable_pvs()`.
- Create an empty temporary `pvmove%d` LV with `PVMOVE | LOCKED`.
- Identify affected LVs and insert pvmove mirror layers with `insert_layer_for_segments_on_pv()`.
- Convert the temporary LV to mirrored form with `lv_add_mirrors()`.
- Split parent segments for the inserted layer.
- Activate changed LVs, copy the operation ID, update/reload metadata for the initial setup, then poll.

## Existing Pvmove Flow

If `find_pvmove_lv()` finds an existing temporary mirror:

- Command arguments after the source PV are ignored.
- `lvs_using_lv()` gathers affected LVs.
- The code determines whether exclusive activation is required.
- The temporary mirror is activated and polling resumes.

## Allocation and Redundancy Safety

- `_get_allocatable_pvs()` excludes the source PV unless allocation policy is `ALLOC_ANYWHERE`, and removes full PVs.
- `_set_up_pvmove_lv()` first inspects top-level RAID/mirror LVs to trim destination PVs that would break redundancy.
- `_remove_sibling_pvs_from_trim_list()` preserves RAID data/meta sibling collocation for targeted sub-LV moves.
- `_trim_allocatable_pvs()` removes forbidden PVs from destination candidates.

## LV Eligibility Checks

The setup rejects or skips:

- Converting or merging LVs.
- Writecache cachevol devices.
- Writecache whose cachevol is on the source PV.
- RAID with integrity.
- Locked LVs.
- Shared VG pvmove without a named LV and exclusive LV lock.
- Internal sanlock LVs.
- LVs that cannot be activated locally/exclusively as required.

## Locking and Activation

- `pvmove` requires `lvmpolld` when `lvmlockd` is in use.
- Shared VGs require named LV and exclusive LV lock.
- Exclusive pvmove is inferred from origins, COWs, and exclusive segment holders.
- After setup, the global lock is released before long polling.

## Poll Integration

The pvmove poll callbacks are:

- `get_copy_name_from_lv = get_pvmove_pvname_from_lv_mirr`
- `poll_progress = poll_mirror_progress`
- `update_metadata = pvmove_update_metadata`
- `finish_copy = pvmove_finish`

`pvmove_poll()` skips real polling in test mode.

## Notable Edge Cases

- No-argument `pvmove` is allowed generally to poll all in-progress moves, but not with `lvmlockd`.
- Abort mode uses shared/default lock behavior to locate the pvmove and then delegates abort completion to the poll framework.
- The temporary pvmove LV is expected to remain locked while movement is active.

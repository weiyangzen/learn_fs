# File Research: sources/block-storage/lvm2/tools/pvmove_poll.c

## Purpose

`pvmove_poll.c` implements pvmove-specific poll callbacks for metadata progression and final cleanup after a pvmove copy finishes or aborts.

## Main Entry Points

- `pvmove_update_metadata()`: advances pvmove metadata between mirror sections by calling `lv_update_and_reload()`.
- `pvmove_finish()`: detaches the temporary pvmove mirror, resumes affected LVs, deactivates temporary components, removes the temporary LV, and commits final VG metadata.

## Mirror Detach Logic

- `_detach_pvmove_mirror()` removes one pvmove mirror image with `lv_remove_mirrors()`.
- In abort mode, if the first segment uses an LV area, it removes the second mirror leg.
- `_is_pvmove_image_removable()` validates that a candidate mirror image belongs to the expected mirror segment and requested image index.

## Finish Flow

`pvmove_finish()`:

- Records the initial visible LV count.
- Detaches pvmove mirror image if there are affected LVs.
- Requires the temporary mirror LV to have been replaced by an error segment.
- Calls `lv_update_and_reload()` on the temporary LV.
- Calls `activate_pvmoved_lvs()` to refresh/resume all affected LVs.
- Synchronizes local device names.
- Deactivates invisible component LVs that were activated only for pvmove and have `open_count == 0`.
- Deactivates the temporary pvmove LV.
- Removes the temporary LV from metadata.
- Writes and commits the final VG.
- Verifies visible LV count did not increase, warning about orphan temporary LVs if cleanup failed.

## Safety Notes

- Cleanup is conservative around component LV deactivation: it checks existence and open count before deactivation.
- Errors are logged as aborting failures because incomplete cleanup can leave temporary volumes.
- Final metadata is not committed until after temporary mirror removal and LV cleanup.

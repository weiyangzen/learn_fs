# File Research: sources/block-storage/lvm2/tools/vgexport.c

Purpose: implements `vgexport`, marking VGs and their PVs exported so they can be moved/imported elsewhere.

Read coverage: complete file read, 86 lines.

Key responsibilities:
- Requires explicit VG arguments, `--select`, or `-a`; rejects combining `-a` with names or selection.
- Refuses export if any LVs in the VG are active.
- For shared VGs, attempts exclusive LV locks to ensure lock-using LVs are inactive on all hosts.
- Sets `EXPORTED_VG` on the VG and all PVs and clears `system_id`.
- Writes and commits VG metadata.
- Optionally stops persistent reservations when `--persist stop` is requested.

Dependencies:
- Uses activation checks, lvmlockd LV locks, persistent reservation stop helper, and VG metadata write/commit.

Risks and edge cases:
- Shared VG export requires cross-host inactivity, not just local inactivity.
- PR stop failure is warned but does not turn a successful export into command failure.

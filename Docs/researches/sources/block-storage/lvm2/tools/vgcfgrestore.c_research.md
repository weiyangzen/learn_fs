# File Research: sources/block-storage/lvm2/tools/vgcfgrestore.c

Purpose: implements `vgcfgrestore`, listing archived VG metadata or restoring a selected VG from archive/default backup or an explicit file.

Read coverage: complete file read, 159 lines.

Key responsibilities:
- Validates that restore targets a single VG unless listing a file archive.
- Implements overloaded `--list` behavior to show archive entries for a VG or an explicit file.
- Scans all device-mapper devices, splits LVM names, and warns if restored VG has active LVs.
- Prompts unless `--yes` is set before restoring metadata over a VG with active volumes.
- Takes global exclusive lock, VG write lock, clears hints, scans labels, and enables unknown-segment handling.
- Calls `backup_restore_from_file()` or `backup_restore()` with force count.
- Unlocks the VG and reports restore success/failure.

Dependencies:
- Uses libdevmapper task listing, `dm_split_lvm_name()`, archiver restore APIs, LVM locking, hint clearing, and lvmcache label scanning.

Risks and edge cases:
- Active LV detection is based on device-mapper names, with a TODO about UUID-prefix validation.
- Restoring while active can create kernel/metadata mismatches, hence the explicit warning and prompt.
- Error paths carefully unlock VG locks after failed scans/restores, but global lock lifetime is managed by broader command context.

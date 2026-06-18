# File Research: sources/block-storage/lvm2/tools/vgimportclone.c

Purpose: implements `vgimportclone`, importing duplicated/cloned PV devices as a distinct VG by assigning new VG/PV UUIDs, a unique VG name, local ownership, and optional devices-file entries.

Read coverage: complete file read, 528 lines.

Key responsibilities:
- Builds a list of user-specified cloned devices, scans only those devices, and verifies they belong to one VG.
- Clears cloned-device cache state, scans all other visible devices, and chooses a unique new VG name from `--basevgname` or the old name plus numeric suffix.
- Locks both old and new VG names, rescans the cloned devices read/write, and reads the VG with exported VGs included.
- Validates the cloned VG is complete, not active on the supplied devices, and that the supplied device set exactly matches the VG’s PV set.
- Optionally imports an exported VG, creates a new VG UUID, renames the VG, clears shared lock type/args and PR flags, assigns local system ID, and creates new PV UUIDs.
- Updates LV LVID VG component and clears LV lock args.
- Adds device IDs before writing VG metadata when devices-file support is enabled or `--importdevices` is requested.
- Writes VG metadata and writes the devices file at the end when relevant.

Dependencies:
- Uses device cache/filtering, label scan variants, lvmcache, device-id handling, VG read/write/commit, locking, and command memory pools.

Risks and edge cases:
- The command deliberately alternates scans of cloned devices and other devices to avoid duplicate metadata conflicts in lvmcache.
- All PVs from the cloned VG must be supplied together; partial clone import is rejected.
- Active LV detection checks whether each cloned device is used by an active LV because ordinary active-LV checks cannot distinguish original versus clone.
- Shared VG clones are imported as local VGs, with lock metadata and PR settings cleared.

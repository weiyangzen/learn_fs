# File Research: sources/block-storage/lvm2/tools/vgextend.c

Purpose: implements `vgextend`, adding new PVs to a VG or clearing missing-PV status for restored devices.

Read coverage: complete file read, 204 lines.

Key responsibilities:
- Parses VG name and PV arguments, using pvcreate parameter defaults but preserving existing PV metadata.
- Disallows forced pvcreate behavior inside `vgextend`.
- Takes global lock, clears hints, enables devices-file editing, scans labels, and optionally runs `pvcreate_each_device()`.
- Allows extending VGs with missing PVs to support repair workflows.
- Adds PVs with `vg_extend_each_pv()`, starts persistent reservation on new devices when VG PR requires/autostarts it, and adjusts metadata copy preference when `--metadataignore` changes usable MDA count.
- Implements `--restoremissing` by finding named missing PVs, clearing `MISSING_PV`, and committing the VG.

Dependencies:
- Uses PV create/extend helpers, VG metadata copy helpers, persistent reservation extend helper, devices-file locking, lvmcache scanning, and process-each-VG framework.

Risks and edge cases:
- `--restoremissing` only succeeds if at least one listed PV was truly restorable or had its unused missing flag cleared.
- Metadata copy count may be changed to match actual used MDAs after adding ignored metadata areas.
- Devices-file lock is released after PV creation setup before VG processing continues.

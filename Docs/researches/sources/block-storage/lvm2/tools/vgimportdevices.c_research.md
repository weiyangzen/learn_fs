# File Research: sources/block-storage/lvm2/tools/vgimportdevices.c

Purpose: implements `vgimportdevices`, adding PV devices from existing VGs into the LVM devices file and optionally updating VG metadata with device IDs.

Read coverage: complete file read, 326 lines.

Key responsibilities:
- Supports importing devices from all accessible VGs, selected VGs, foreign VGs with `--foreign`, shared VGs, and the root VG with `--rootvg`.
- For `--auto --rootvg`, skips work if `system.devices` already exists or the auto-import marker is absent.
- Takes global lock, prepares and locks the devices file, creates it if missing, and clears hints for the default devices file.
- Forces scanning beyond any existing devices file by skipping the device-id filter and using regex filtering with devices-file entries retained for writing.
- Disables lockd VG/global locking to bootstrap shared VGs into the devices file.
- Per VG, skips missing-PV VGs, adds each PV device ID, and updates VG metadata with device IDs only for local non-shared/non-foreign VGs.
- Writes the devices file, prints device count, and removes auto-import trigger files for root-VG auto import.

Dependencies:
- Uses devices-file setup/locking/writing, device-id add/write helpers, root VG DM UUID detection, lvmcache, activation/root helper APIs, and process-each-VG.

Risks and edge cases:
- If no devices are added, command fails and removes a newly created devices file.
- Foreign and shared VGs can contribute devices but are not modified with new device IDs.
- Missing PVs cause the VG to be skipped rather than partially imported into the devices file.
- Root-VG detection compares the DM UUID’s embedded VG id against each processed VG.

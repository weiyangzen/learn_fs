# File Research: sources/block-storage/lvm2/tools/vgmknodes.c

Purpose: implements `vgmknodes`, ensuring device nodes exist for LVs and optionally refreshing visible LVs first.

Read coverage: complete file read, 43 lines.

Key responsibilities:
- If udev sync support is unavailable, calls `lv_mknodes(cmd, NULL)` to create missing nodes globally.
- Processes each selected LV under VG read locks.
- With `--refresh`, refreshes visible LVs and syncs local device names before node creation.
- Calls `lv_mknodes()` for each LV.

Dependencies:
- Uses udev sync detection, LV refresh, LV node creation, device-name sync, and process-each-LV framework.

Risks and edge cases:
- Refresh is limited to visible LVs.
- Non-udev fallback creates nodes before the per-LV iteration.

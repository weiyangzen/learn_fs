# File Research: sources/block-storage/lvm2/tools/vgscan.c

Purpose: implements `vgscan`, reporting discovered VGs, optional node creation, and dbus notification trigger setup.

Read coverage: complete file read, 64 lines.

Key responsibilities:
- With `--notifydbus`, verifies dbus support and config enablement, then marks PV/VG/LV notifications and returns.
- Treats `vgscan --cache` as obsolete because lvmetad is no longer used.
- Processes each VG and prints found/exported status plus metadata type.
- Checks current backup state for each VG.
- With `--mknodes`, runs `vgmknodes()` after scanning and returns the worst result.

Dependencies:
- Uses lvmnotify support/config, process-each-VG, backup freshness checking, and `vgmknodes()`.

Risks and edge cases:
- `--notifydbus` does not scan VGs; it only sets notification markers after validation.
- `--cache` is accepted but ignored for compatibility.

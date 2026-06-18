# File Research: sources/block-storage/lvm2/tools/vgremove.c

Purpose: implements `vgremove`, removing an entire VG, including contained LVs, pool metadata spare, PV metadata, lock resources, online state, and persistent reservation cleanup.

Read coverage: complete file read, 124 lines.

Key responsibilities:
- Requires VG arguments or `--select`.
- Takes global exclusive lock, clears hints, enables outdated-PV wiping and missing-PV handling.
- Prompts before removing VGs containing visible LVs unless force/yes suppresses prompt.
- Removes all LVs in the VG using `lvremove_single()` with selection disabled at the per-LV level.
- Removes pool metadata spare LV if present.
- Coordinates persistent reservation finish-before/after when PR is required or autostarted.
- Frees lockd VG resources, checks VG removal safety when not forced, removes online state, removes PVs, removes VG metadata, and finalizes lockd cleanup.

Dependencies:
- Uses LV removal, online VG removal, persistent reservation finish helpers, lockd free helpers, VG remove/check/PV removal helpers, and process-each-VG.

Risks and edge cases:
- Selection is intentionally applied at VG level, not per LV, to avoid partially removing selected LVs within a selected VG.
- Force count and `--yes` have nuanced prompt behavior; stronger force is still required where lower-level removal requires it.
- PR and lockd cleanup span before/after phases around metadata removal.

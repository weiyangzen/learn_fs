# File Research: sources/block-storage/lvm2/tools/vgdisplay.c

Purpose: implements `vgdisplay` variants for colon, general, short, verbose, and columns output.

Read coverage: complete file read, 89 lines.

Key responsibilities:
- Filters `-A/--activevolumegroups` output to VGs with activated LVs.
- Emits colon-formatted VG display through `vgdisplay_colons()`.
- Emits short or full display through `vgdisplay_short()`/`vgdisplay_full()`.
- In verbose mode, displays each LV fully and each PV briefly after the VG output.
- Checks current backup state after general display.
- Delegates columns mode to `vgs()`.

Dependencies:
- Uses display helpers, process-each-VG/LV/PV helpers, active-LV checks, and backup freshness checking.

Risks and edge cases:
- `-A` is rejected when explicit VG names are supplied.
- The generic `vgdisplay()` entry is an internal-error fallback; command definitions should select a concrete variant.

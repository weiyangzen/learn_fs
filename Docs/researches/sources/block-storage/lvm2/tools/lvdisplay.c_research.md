# File Research: sources/block-storage/lvm2/tools/lvdisplay.c

This file implements the `lvdisplay` command variants.

Functions:
- `_lvdisplay_colon_single()` skips hidden LVs unless `--all` is set, then prints colon-format output with `lvdisplay_colons()`.
- `_lvdisplay_general_single()` skips hidden LVs unless `--all` is set, prints full LV details with `lvdisplay_full()`, and prints segment maps with `lvdisplay_segments()` when `--maps` is set.
- `lvdisplay_colon_cmd()` processes target LVs with `_lvdisplay_colon_single()`.
- `lvdisplay_general_cmd()` processes target LVs with `_lvdisplay_general_single()`.
- `lvdisplay_columns_cmd()` delegates column output to `lvs()`.
- Generic `lvdisplay()` is an internal-error fallback for missing command-definition dispatch.

Behavior:
- The file is a thin command wrapper around shared display functions.
- Hidden/internal LVs are filtered by default and shown only with `--all`.
- Column-mode output is intentionally delegated to the reporting command implementation rather than duplicated here.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_vbios.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_vbios.c

## Purpose

`ast_vbios.c` implements AST's built-in VBIOS-like mode timing database and lookup logic. It maps common display resolutions and refresh rates to AST-specific timing entries and chooses the best entry for a requested DRM display mode.

## Important APIs, Types, And Functions

- Static `res_*` arrays of `struct ast_vbios_enhtable`: timing tables for 4:3, 16:9, and 16:10 modes from 640x480 through 1920x1200. Entries include totals, active area, porches, sync widths, DCLK index, flags, refresh, refresh index, and mode ID.
- Resolution table groups: `res_table_wuxga`, `res_table_fullhd`, `res_table_wsxga_p`, and base `res_table`.
- `__ast_vbios_find_mode_table()`: scans a null-terminated table group for matching `hde` and `vde`.
- `ast_vbios_find_mode_table()`: chooses which resolution groups are available based on `ast->support_wuxga`, `support_fullhd`, and `support_wsxga_p`, then falls back to the base table.
- `ast_vbios_find_mode()`: filters candidate refresh entries by sync polarity and chooses the highest table refresh rate not greater than the requested mode refresh.

## Control Flow

The public lookup starts by selecting a resolution table allowed by device capability flags. If no resolution table matches, it returns `NULL`. Otherwise it computes requested refresh through `drm_mode_vrefresh()`, iterates valid table entries until `AST_VBIOS_INVALID_MODE`, skips entries whose sync polarity conflicts with the DRM mode flags, and returns the closest non-higher refresh entry.

## State And Persistence Behavior

The file stores static read-only timing tables. It does not mutate state. The selected timing entry drives later AST register programming and therefore influences persistent display-timing state in hardware.

## Dependencies And Integration Points

It depends on `ast_drv.h`, `ast_vbios.h`, and DRM display mode fields. It integrates with AST CRTC/modeset code that translates `ast_vbios_enhtable` entries into VGA/AST register writes, and with output capability discovery that sets the `support_*` flags.

## Risks And Edge Cases

The lookup intentionally refuses refresh rates above the request, so a request slightly below a supported rate may fail to choose an otherwise usable higher refresh. Sync polarity filtering can eliminate all modes for a resolution. Capability flags gate wide/full-HD/WUXGA modes, so incorrect transmitter detection can hide modes. Table data is hardware-specific and brittle.

## Test Signals

Mode-validation and modeset tests should cover each resolution group, capability-flag combinations, sync polarity mismatches, refresh selection boundaries, and actual display output at wide/full-HD/WUXGA timings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_vbios.c -->

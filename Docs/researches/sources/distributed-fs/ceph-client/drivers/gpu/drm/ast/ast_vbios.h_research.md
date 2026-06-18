<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_vbios.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_vbios.h

## Purpose

`ast_vbios.h` defines AST enhanced-mode timing flags, DCLK indexes, the `struct ast_vbios_enhtable` layout, and the mode lookup API used by AST modeset code.

## Important APIs, Types, And Macros

- Timing flags: character clock, half/double scan, border, line compare, widescreen/new-mode indicators, polarity flags, and `AST2500PreCatchCRT`.
- Sync bundles: `SyncPP`, `SyncPN`, `SyncNP`, and `SyncNN`.
- DCLK index macros from `VCLK25_175` through `VCLK118_25`; these are AST clock-table indexes, not raw frequencies.
- `struct ast_vbios_enhtable`: horizontal/vertical totals, active area, porch/sync fields, clock index, flags, refresh metadata, and AST mode ID.
- `AST_VBIOS_INVALID_MODE` and `ast_vbios_mode_is_valid()`: sentinel construction and validity test.
- `ast_vbios_find_mode()`: public lookup prototype.

## Control Flow

Only the inline validity helper has logic: a mode is valid when horizontal total, vertical total, and refresh rate are nonzero. All other macros define data consumed by `ast_vbios.c` and modeset register programming.

## State And Persistence Behavior

No mutable state exists in this header. The constants encode display timing choices that persist in hardware after consumers program a mode.

## Dependencies And Integration Points

It includes Linux types and forward-declares AST/DRM structures. It is paired with `ast_vbios.c`, AST clock programming, and CRTC modeset code that interprets the flags and DCLK indexes.

## Risks And Edge Cases

DCLK indexes are semantic indexes into another clock-programming table; treating them as frequencies would be wrong. The invalid sentinel relies on zero total/refresh fields. Polarity flags are used inversely in some mode-filtering checks, so changes must be validated against `ast_vbios_find_mode()`.

## Test Signals

Build coverage, static checks for sentinel termination of timing arrays, mode lookup unit tests if available, and display output tests for modes using every DCLK index are useful validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_vbios.h -->

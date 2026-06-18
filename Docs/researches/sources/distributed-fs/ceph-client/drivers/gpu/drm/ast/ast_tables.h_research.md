<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_tables.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_tables.h

## Purpose

`ast_tables.h` contains legacy VGA standard-mode programming tables ported from the xf86-video-ast driver. These tables define sequencer, CRTC, attribute, and graphics-controller register values for text, EGA, VGA, high-color, and true-color baseline modes.

## Important APIs, Types, And Macros

- Mode index macros: `TextModeIndex`, `EGAModeIndex`, `VGAModeIndex`, `HiCModeIndex`, and `TrueCModeIndex`.
- `vbios_stdtable[]`: static table of `struct ast_vbios_stdtable` entries, each with a misc output byte and arrays for sequencer, CRTC, attribute, and graphics-controller values. Register arrays use `0xff` as visible terminators in several sub-arrays.

## Control Flow

The header has no executable control flow. Modesetting code indexes the table, then writes the contained values to VGA register groups in the order expected by the AST hardware/VBIOS model.

## State And Persistence Behavior

No software state is stored. The table values become persistent VGA register state once a consumer programs them during mode setup or reset.

## Dependencies And Integration Points

It includes `ast_drv.h` for the `struct ast_vbios_stdtable` definition. It integrates with AST VGA modeset code that needs a known standard VGA register base before enhanced timing programming.

## Risks And Edge Cases

The data is a hardware programming contract; a single byte can change sync, timing, memory layout, or attribute behavior. Because it is a header with a `static const` definition, each including translation unit receives its own private copy. Consumers must not assume every sub-array has the same terminator semantics.

## Test Signals

Validation signals are successful AST mode initialization from text/VGA-style defaults, regression tests around standard modes, visual output on legacy VGA/DVI paths, and diffs against the original vendor or xf86-video-ast tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_tables.h -->

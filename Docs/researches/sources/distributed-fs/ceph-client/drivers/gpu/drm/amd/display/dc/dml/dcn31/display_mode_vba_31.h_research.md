# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn31/display_mode_vba_31.h

## Purpose

`display_mode_vba_31.h` is the public DCN 3.1 Display Mode Library VBA header. It declares the generation-specific entry points that run the DCN 3.1 mode-support and system-configuration calculations and exposes the writeback DISPCLK helper used by display validation and bandwidth programming code.

The file is intentionally small. It is a contract header for the large `display_mode_vba_31.c` implementation and lets other DML/DCN code call DCN 3.1 VBA logic without depending on implementation-private functions.

## Important APIs, Types, And Functions

- `dml31_recalculate(struct display_mode_lib *mode_lib)`: recalculates the current `display_mode_lib` VBA state after inputs have been populated.
- `dml31_ModeSupportAndSystemConfigurationFull(struct display_mode_lib *mode_lib)`: runs the full DCN 3.1 mode-support and system-configuration pass.
- `dml31_CalculateWriteBackDISPCLK(...)`: computes the DISPCLK requirement for writeback from writeback pixel format, pixel clock, horizontal/vertical ratios, filter taps, source/destination widths, total timing width, and writeback line-buffer size.
- `struct display_mode_lib` and `enum source_format_class`: referenced but not defined here; callers must include the broader DML headers that provide those definitions before or alongside this header.

## Control Flow

There is no executable control flow in this header. Compile-time control flow is limited to the include guard `__DML31_DISPLAY_MODE_VBA_H__`. Runtime behavior is entirely in the implementation file that provides these declarations.

The expected call pattern is that DCN 3.1 resource validation code populates `struct display_mode_lib`, calls the full mode-support pass or recalculation entry point, and then reads derived VBA fields. Writeback code can call `dml31_CalculateWriteBackDISPCLK` independently when sizing writeback clock requirements.

## State And Persistence Behavior

This header owns no state and performs no persistence. The declared functions operate on caller-owned `struct display_mode_lib` instances or scalar writeback parameters. Persistent effects, if any, are in the implementation and are expected to be in-memory DML state updates only.

## Dependencies And Integration Points

The header is part of AMDGPU Display Core's DML generation split under `dcn31`. It integrates with:

- DCN 3.1 VBA implementation code.
- DML callers that hold a `struct display_mode_lib`.
- Writeback validation paths that need a DCN 3.1-specific DISPCLK calculation.
- Neighbor headers such as `display_mode_lib.h`, `display_mode_vba.h`, and generation FPU/resource code that provide concrete types and call sites.

## Risks And Edge Cases

- The header forward-uses `struct display_mode_lib` and `enum source_format_class` without including their definitions. This is fine for translation units that already include DML base headers, but include-order mistakes can produce build errors.
- Function declarations are generation-specific. Accidentally wiring DCN 3.0 or DCN 3.14 callers to these declarations can silently apply the wrong hardware model if signatures still match.
- `dml31_CalculateWriteBackDISPCLK` takes a mix of `double`, `unsigned int`, and `long` values. Callers must preserve units and avoid truncation before invoking it.

## Test Signals

- Kernel build coverage catches missing type declarations, signature drift from the implementation, and incorrect include ordering.
- DML validation tests should compare DCN 3.1 mode-support results and writeback DISPCLK values against known-good tables.
- Runtime issues would usually surface outside this header as rejected modes, unexpected writeback clock requests, or mismatches between DCN generation-specific validation and hardware programming.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/display_mode_vba.h

## Purpose
`display_mode_vba.h` declares the DML VBA getter surface and defines `struct vba_vars_st`, the central state object for display mode calculations.

## Important APIs, Types, And Functions
The header declares `ModeSupportAndSystemConfiguration()`, scalar and pipe-scoped `get_*` accessors, aggregate helpers, `dml_get_voltage_level()`, `get_is_phantom_pipe()`, `PixelClockAdjustmentForProgressiveToInterlaceUnit()`, `Calculate256BBlockSizes()`, `CalculateMinAndMaxPrefetchMode()`, and `CalculateWriteBackDISPCLK()`. `struct vba_vars_st` embeds SoC/IP parameters, cached pipe inputs, dummy scratch structs, and many input, intermediate, debug, mode-support, and output arrays.

## Control Flow
There is no executable flow, but the layout defines the DML data flow: copy inputs, calculate mode support and performance, then read outputs through getters. Field groups track SoC, IP, pipe/plane inputs, calculated outputs, support reasons, per-state locals, and performance locals.

## State, Persistence, And Dependencies
`vba_vars_st` persists for the lifetime of `display_mode_lib` and caches previous SoC/IP/pipe inputs. Dependencies include DC/DML enum classes, limits, pipe parameter structs, watermarks, DML pipe structures, and SoC helper structures.

## Integration Points
Most DML calculation files read or write this struct. DC mode validation consumes support booleans and reason flags; register calculators consume timing, PTE, swath, VM, and MALL fields; tests and debug paths consume getter declarations.

## Risks
The struct is large and heavily indexed by plane, surface, state, and combine mode. Similar names can differ by luma/chroma, current/per-state, or nominal/vblank/flip semantics. New fields must be initialized on all paths to avoid stale cache behavior.

## Test Signals
Compile coverage is essential. Runtime tests should check getter consistency, hsplit/overlay pipe-plane mapping, voltage-state arrays, MALL/VM/DCC fields, and cached debug values across repeated getter calls.

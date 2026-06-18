# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/display_mode_vba.c

## Purpose
`display_mode_vba.c` bridges driver-facing pipe inputs and AMD DML's VBA calculation state. It copies SoC, IP, and pipe parameters into `mode_lib->vba`, invokes recalculation and validation callbacks, and exposes calculated watermarks, clocks, bandwidths, prefetch values, MALL values, PTE metadata timings, and per-pipe attributes through getters.

## Important APIs, Types, And Functions
The main public entry is `dml_get_voltage_level()`. Macro-generated `get_*` functions expose scalar and pipe-scoped attributes. Other public helpers include aggregate immediate-flip and prefetch bandwidth getters, `get_det_buffer_size_kbytes()`, `get_is_phantom_pipe()`, `Calculate256BBlockSizes()`, `CalculateMinAndMaxPrefetchMode()`, `PixelClockAdjustmentForProgressiveToInterlaceUnit()`, `ModeSupportAndSystemConfiguration()`, and `CalculateWriteBackDISPCLK()`. Private helpers transfer state and manage caches: `fetch_socbb_params()`, `fetch_ip_params()`, `fetch_pipe_params()`, `recalculate_params()`, `get_pipe_idx()`, `CursorBppEnumToBits()`, and `cache_debug_params()`.

## Control Flow
Getter calls first run `recalculate_params()`, which compares current SoC/IP/pipes against cached copies and calls `mode_lib->funcs.recalculate()` when inputs changed. `dml_get_voltage_level()` refreshes caches, chooses recalculation or direct fetch, validates, and snapshots debug margins. `fetch_pipe_params()` walks pipes, collapses hsplit pipes into planes, maps source/dest/output fields into VBA arrays, handles overlays, VM enablement, forced page-table levels, MALL flags, viewport caps, cursors, and PTE buffer mode assertions.

## State, Persistence, And Dependencies
Persistent state lives in `struct display_mode_lib`, especially `mode_lib->vba`, `cache_pipes`, and `cache_num_pipes`. Dependencies include `display_mode_lib.h`, `display_mode_vba.h`, `dml_inline_defs.h`, DML math wrappers, logger macros, and callback hooks in `mode_lib->funcs`.

## Integration Points
The file is used by AMD display mode validation and watermark, clock, DSC, writeback, MALL, immediate flip, and RQ/DLG programming paths. Generated getters are the stable access layer for other DC/DML files.

## Risks
`memcmp()` over input structs assumes initialized padding. Array indexing assumes valid pipe counts and pipe-plane mappings. Similar parallel array names are easy to confuse. Several TODOs remain around multistream, audio layout, DCC rate, viewport stationary, and hsplit recout behavior.

## Test Signals
Test cache invalidation, hsplit and overlay mappings, interlace/P2I adjustment, GPUVM and HostVM forced levels, MALL phantom/static-screen modes, immediate flip aggregation, writeback DISPCLK formulas, and 256-byte block and prefetch mode boundaries.

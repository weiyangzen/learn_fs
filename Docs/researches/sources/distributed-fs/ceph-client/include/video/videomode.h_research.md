<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/videomode.h -->
# sources/distributed-fs/ceph-client/include/video/videomode.h

## Purpose
This header defines a subsystem-independent video mode representation and conversion helpers from display timing data.

## Important APIs, Types, And Functions
- `struct videomode` stores pixel clock, horizontal active/front/back/sync values, vertical active/front/back/sync values, and display flags.
- `videomode_from_timing()` converts one `struct display_timing` into a `videomode`.
- `videomode_from_timings()` selects an indexed entry from `struct display_timings` and converts it.

## Control Flow
The helper functions are called by display drivers after reading firmware or device-tree timing tables. They normalize timing data into the compact `videomode` structure used by panels, bridges, and controllers.

## State And Persistence
The header declares no persistent state. The resulting `videomode` is caller-owned and usually becomes part of mode-setting state.

## Dependencies And Integration Points
It depends on `<video/display_timing.h>` and Linux types. Integration points include device-tree display timings, panel drivers, fbdev/DRM mode conversion, and controller-specific timing register programming.

## Risks And Edge Cases
Invalid timing indexes should be surfaced by `videomode_from_timings()`. Drivers must handle flags and units correctly; pixel clock is in Hz while some hardware registers use kHz, periods, or divisors.

## Test Signals
Tests should compare converted timing fields against known device-tree entries, verify out-of-range indexes fail, and confirm downstream mode programming receives the expected polarity/edge flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/videomode.h -->

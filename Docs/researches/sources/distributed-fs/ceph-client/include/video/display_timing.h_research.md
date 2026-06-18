<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/display_timing.h -->
# sources/distributed-fs/ceph-client/include/video/display_timing.h

Purpose: defines generic display timing data structures and flags for describing panel/display signal ranges before conversion to concrete video modes.

Important APIs and types: `enum display_flags` encodes hsync/vsync/data-enable polarity, pixel-data edge, interlace, doublescan, doubleclock, and sync edge. `timing_entry` stores min/typ/max values. `display_timing` groups pixel clock, horizontal/vertical active/porch/sync timings, and flags. `display_timings` holds an array of timings plus native mode. `display_timings_get()` safely retrieves an indexed timing, and `display_timings_release()` frees a collection.

Control flow: firmware/DT/panel parsers produce `display_timings`; drivers choose native or supported entries, convert timing ranges to `videomode`/DRM/fb modes, and release allocated timing arrays on teardown.

State and persistence: structures are runtime representations of persistent panel/firmware timing descriptions. The header does not own state.

Dependencies and integration points: depends on bitops and types. It integrates with OF display timing parsing, panel drivers, fbdev/DRM mode conversion, and `include/video/videomode.h`.

Risks and test signals: risks include invalid min/typ/max ordering, conflicting polarity flags, native index out of range, and memory ownership of timing arrays. Test DT timing parsing, multiple modes, native mode selection, invalid ranges, and release paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/display_timing.h -->

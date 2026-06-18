# sources/distributed-fs/ceph-client/drivers/video/of_display_timing.c

Purpose: Open Firmware/devicetree parser for `display-timings` nodes. It translates timing subnodes into `struct display_timing` and aggregate `struct display_timings` objects.

Important APIs, types, and functions: exported `of_get_display_timing` and `of_get_display_timings`; internal `parse_timing_property` and `of_parse_display_timing`. It fills `struct timing_entry`, `struct display_timing`, and `struct display_timings`.

Control flow: individual timing properties may contain one cell (typical only) or three cells (min/typ/max). `of_parse_display_timing` reads required horizontal, vertical, and clock properties, optional polarity/edge booleans, and mode flags. `of_get_display_timing` parses a named child. `of_get_display_timings` locates the `display-timings` child, resolves `native-mode` or first child, allocates an array, parses every child, records the native index, and releases nodes on success/error.

State and persistence: allocates `display_timings` and per-timing objects for the caller to release with `display_timings_release`. No global state.

Dependencies and integration points: depends on OF property APIs, `display_timing` structures, and slab allocation. Used by framebuffer/display drivers such as `wm8505fb.c` and by `of_videomode.c`.

Risks: required property parsing ORs errors together and reports a generic timing-property error. Any invalid child makes the whole timing set fail to avoid accepting wrong devicetrees. Ownership must be honored by callers to avoid leaks. Timing node order defines fallback native mode.

Test signals: DT parsing tests for one-cell and three-cell properties, missing required values, invalid cell counts, native-mode phandle, first-child fallback, polarity and interlace/doublescan/doubleclk flags, and error cleanup.

# sources/distributed-fs/ceph-client/drivers/video/of_videomode.c

Purpose: convenience OF helper that retrieves one videomode from a node's display timings and converts it into `struct videomode`.

Important APIs, types, and functions: exported `of_get_videomode(struct device_node *np, struct videomode *vm, int index)`.

Control flow: calls `of_get_display_timings`, maps `OF_USE_NATIVE_MODE` to the timing set's native index, converts the selected timing with `videomode_from_timings`, releases the display timing set, and returns the conversion status.

State and persistence: no persistent state; allocates through `of_get_display_timings` and releases before returning.

Dependencies and integration points: bridges `of_display_timing.c` and `videomode.c`; used by display drivers that only need one mode rather than the full timing table.

Risks: callers cannot inspect alternate modes through this API. Missing timings are reported as `-EINVAL`. Index bounds are delegated to `videomode_from_timings`.

Test signals: parse native and explicit indexes; test missing `display-timings`, invalid index, and release behavior under kmemleak-style checks.

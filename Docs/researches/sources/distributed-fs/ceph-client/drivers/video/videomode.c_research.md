# sources/distributed-fs/ceph-client/drivers/video/videomode.c

Purpose: generic conversion helpers from `struct display_timing`/`struct display_timings` to `struct videomode`.

Important APIs, types, and functions: exported `videomode_from_timing` and `videomode_from_timings`.

Control flow: `videomode_from_timing` copies the typical pixel clock, active area, porch, sync length, and flags fields into a videomode. `videomode_from_timings` fetches a timing by index with `display_timings_get`, returns `-EINVAL` if missing, and delegates conversion.

State and persistence: no state; pure transformation of caller-provided structures.

Dependencies and integration points: used by `of_videomode.c` and display drivers converting parsed timing tables to a single active mode. Depends on `<video/display_timing.h>` and `<video/videomode.h>`.

Risks: min/max timing ranges are discarded in favor of typical values. Index validation is only as strong as `display_timings_get`.

Test signals: convert valid timing with flags; invalid index returns `-EINVAL`; verify min/max ranges do not affect output except through `.typ`.

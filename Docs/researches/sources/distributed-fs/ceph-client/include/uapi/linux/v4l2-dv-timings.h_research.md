# sources/distributed-fs/ceph-client/include/uapi/linux/v4l2-dv-timings.h

## Purpose
Provides compile-time initializer macros for common digital video timings used by V4L2. The catalog covers CEA-861 HDTV/HDMI modes, VESA DMT/CVT monitor modes, and a small SDI timing.

## Important APIs, Types, And Constants
`V4L2_INIT_BT_TIMINGS` works around old GCC anonymous-union initializer behavior. Each `V4L2_DV_BT_*` macro expands to a `struct v4l2_dv_timings` initializer with type `V4L2_DV_BT_656_1120` and embedded BT timings: active width/height, interlace flag, sync polarities, pixel clock, horizontal/vertical porch/sync values, timing standards (`DMT`, `CEA861`, `CVT`, `SDI`), flags such as reduced blanking, half-line, CE video, aspect/VIC presence, CEA VIC, and HDMI VIC where applicable. Several DMT modes alias CEA definitions where standards overlap.

## Control Flow, State, And Persistence
No runtime logic exists. Drivers and helper tables include these macros to advertise, validate, or set DV timings. Device state is maintained by receivers/transmitters after timing negotiation; the header only supplies canonical presets.

## Dependencies And Integration Points
The macros require `struct v4l2_dv_timings` and related `V4L2_DV_*` constants from the broader V4L2 API. They integrate with HDMI/DVI/SDI receiver drivers, EDID/DV timing enumeration, and applications that select standard modes.

## Risks And Test Signals
Risks include incorrect pixel clocks, porch values, sync polarities, flags, or VIC numbers, which can break display lock or mode matching. Tests should compare preset values against CEA/DMT/SDI references, exercise driver timing enumeration, verify aliases, and perform hardware mode set/query round trips for common and edge modes.

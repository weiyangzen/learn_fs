# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/events.h

## Purpose
Provides the compile-time event reporting facade used by GlusterFS code to emit structured operational events when event support is enabled.

## APIs, Types, and Functions
When `USE_EVENTS` is defined, the header includes `eventtypes.h` and declares `_gf_event(eventtypes_t event, const char *fmt, ...)` with printf-format checking. Without event support, `_gf_event()` is a static inline no-op returning 0. The `gf_event(event, fmt...)` macro validates the format through `FMT_WARN()` and calls `_gf_event()`.

## Control Flow, State, and Persistence
The control flow is compile-time gated. Runtime event delivery is delegated to the enabled implementation; otherwise calls are compiled as no-ops. This header stores no state.

## Dependencies and Integration
Integrated into management and translator paths that announce cluster or process events. Depends on event type definitions and common format-check macros from the broader logging/common-utils stack.

## Risks and Test Signals
Risks include event call sites silently doing nothing in builds without `USE_EVENTS`, format-string mismatch, and assuming event delivery is synchronous or reliable. Test signals include builds with and without event support, compiler format warnings, event daemon integration tests, and checks that key operational transitions emit expected event IDs.

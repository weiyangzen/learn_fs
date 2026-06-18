# sources/distributed-fs/ceph/src/osd/object_state_fmt.h

## Purpose

`object_state_fmt.h` supplies a `fmt` formatter specialization for `ObjectState`, letting fmt-based logging and diagnostics render object existence plus the embedded `object_info_t`.

## Important APIs and Types

The only public item is `template <> struct fmt::formatter<ObjectState>`. `parse()` accepts no custom format syntax and returns the beginning iterator. `format()` writes `exists <bool> oi <object_info_t>` through `fmt::format_to()`.

## Control Flow

Formatting is direct: callers using `fmt::format("{}", object_state)` enter the specialization, which delegates object-info rendering to the formatter support pulled in by `osd/osd_types_fmt.h`. For fmt 9 and newer the file includes `<fmt/ostream.h>`, allowing ostream-backed formatting where needed by dependent types.

## State and Persistence Behavior

There is no mutable or persistent state. The formatter only reads `ObjectState::exists` and `ObjectState::oi`.

## Dependencies and Integration Points

The header includes `osd/object_state.h` and `osd/osd_types_fmt.h`; it therefore tracks both the state struct and object info formatting contract. It integrates with any OSD code using fmtlib instead of ostream operators for structured diagnostics.

## Risks and Test Signals

The main risks are compile-time formatter drift when fmt versions change or when `object_info_t` formatting changes. Since parse accepts no specifiers, callers cannot request alternate layouts. Test signals are compile coverage under the repository's supported fmt versions and log/diagnostic tests that include `ObjectState` in fmt strings.

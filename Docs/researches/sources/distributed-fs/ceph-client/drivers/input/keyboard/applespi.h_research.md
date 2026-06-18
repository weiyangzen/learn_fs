# sources/distributed-fs/ceph-client/drivers/input/keyboard/applespi.h

## Purpose

`applespi.h` is the shared local trace/protocol classification header for the Apple SPI keyboard/touchpad driver. It defines the event categories and packet directions used by `applespi.c` and `applespi_trace.h`.

## Important APIs, Types, and Functions

- `enum applespi_evt_type` assigns bit-valued categories for touchpad init commands, backlight commands, caps-lock commands, keyboard reads, touchpad reads, unknown reads, IRQ notification, and CRC failure.
- `enum applespi_pkt_type` names packet views as `PT_READ`, `PT_WRITE`, and `PT_STATUS`.

## Control Flow

The header has no runtime flow. `applespi.c` chooses an `applespi_evt_type` for the current command or received packet and passes it with an `applespi_pkt_type` to the tracepoint wrappers defined in `applespi_trace.h`.

## State and Persistence Behavior

It owns no state. Its enum values become part of tracepoint payloads and therefore influence userspace tracing interpretation.

## Dependencies and Integration Points

The file depends on `BIT()` being available before use; `applespi.c` includes kernel headers before it, and `applespi_trace.h` includes it before declaring tracepoint fields. It is private to the Apple SPI driver directory.

## Risks and Edge Cases

Changing enum numeric values can break trace consumers and `applespi_get_trace_fun()` assumptions. Because values are bit masks rather than dense small integers, callers should not use them as compact array indexes.

## Test Signals

Compile coverage with tracing enabled, tracepoint format inspection, and runtime traces for each event category are the main validation signals.

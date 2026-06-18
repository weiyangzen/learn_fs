# sources/distributed-fs/ceph-client/drivers/input/keyboard/applespi_trace.h

## Purpose

`applespi_trace.h` declares ftrace tracepoints for Apple SPI keyboard/touchpad traffic. It lets developers capture raw read packets, command writes, write-status bytes, IRQ notifications, and CRC-failed buffers without adding ad hoc logging.

## Important APIs, Types, and Functions

- `DECLARE_EVENT_CLASS(dump_message_template)` records `evt_type`, `pkt_type`, dynamic byte buffer, and length.
- `DEFINE_DUMP_MESSAGE_EVENT()` instantiates packet-dump events for touchpad init, backlight, caps-lock, keyboard data, touchpad data, unknown data, and bad CRC.
- `TRACE_EVENT(applespi_irq_received)` records GPE/read IRQ notification.
- `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` point trace generation at this local header.

## Control Flow

When `CREATE_TRACE_POINTS` is defined in `applespi.c`, this header expands into tracepoint definitions. Runtime callers invoke the generated `trace_applespi_*()` helpers around SPI write, status, read, IRQ, and CRC-failure paths.

## State and Persistence Behavior

Tracepoints do not persist driver state. When enabled, they copy packet bytes into per-event tracing buffers, so the original SPI buffers can be reused after the trace call.

## Dependencies and Integration Points

The file depends on Linux tracepoint infrastructure, `linux/types.h`, `linux/tracepoint.h`, and local `applespi.h`. It integrates with ftrace/perf tooling and the raw packet parsing in `applespi.c`.

## Risks and Edge Cases

Tracing full 256-byte packets can expose input data and increase overhead if enabled during high-rate touchpad activity. The trace include path is relative to the kernel trace generator and can break if the driver is moved. The IRQ tracepoint currently prints only a newline, so consumers rely on fields rather than formatted text.

## Test Signals

Build with `CONFIG_TRACEPOINTS`, enable each applespi event under tracingfs, verify packet lengths and hex dumps, and confirm trace generation for bad CRC and GPE notification paths.

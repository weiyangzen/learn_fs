# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/trace.h

## Purpose

`trace.h` declares a Tegra DRM trace system for MMIO register reads and writes. It defines one event class carrying device, register offset, and value, then derives per-block events for display controller, HDMI, DSI, DPAUX, and SOR access.

## Important APIs, Types, and Definitions

- `TRACE_SYSTEM tegra` names the trace namespace.
- `DECLARE_EVENT_CLASS(register_access, ...)` defines the common payload and print format.
- `DEFINE_EVENT(register_access, dc_writel/readl, ...)`, `hdmi_*`, `dsi_*`, `dpaux_*`, and `sor_*` create block-specific tracepoints.
- `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` point trace generation back to the driver-local header.

## Control Flow

The header is included by normal code for tracepoint declarations and by `trace.c` for definitions. At runtime, register wrappers call generated `trace_*` functions; the tracepoint fast path records events only when enabled by tracing infrastructure.

## State and Persistence Behavior

Tracepoint enablement and recorded events are managed by kernel tracing. This header owns no driver state. It exposes device pointers in event payloads and prints `dev_name()`, offset, and value.

## Dependencies and Integration Points

It includes `<linux/device.h>` and `<linux/tracepoint.h>` and ends with `<trace/define_trace.h>` outside the include guard as required by kernel tracepoint conventions. It integrates with MMIO wrappers throughout the Tegra DRM driver, especially `sor.c`.

## Risks and Edge Cases

Trace include paths are fragile because they are relative to kernel trace generation. Event payloads store a raw `struct device *`; trace consumers should not assume more lifetime than the trace framework supports. Adding a new block requires both a `DEFINE_EVENT` here and call-site wrappers.

## Test Signals

Build tests catch trace-generation failures. Runtime tracing should show events with device names, four-digit register offsets, and eight-digit values when tracepoints are enabled.

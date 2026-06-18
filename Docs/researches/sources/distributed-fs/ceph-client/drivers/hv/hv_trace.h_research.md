<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv_trace.h -->
# sources/distributed-fs/ceph-client/drivers/hv/hv_trace.h

## Purpose

`hv_trace.h` declares tracepoints for Hyper-V VMBus channel management and channel operations. It gives maintainers observability into host messages, offers, rescinds, open/close, GPADL setup/teardown, version negotiation, event scheduling, and modify-channel operations.

## Important APIs, Types, and Functions

- Event class `vmbus_hdr_msg` backs `vmbus_on_msg_dpc` and `vmbus_on_message`.
- `TRACE_EVENT(vmbus_onoffer)` records relid, monitor ID, dedicated interrupt flag, connection ID, interface GUIDs, channel flags, MMIO size, and sub-channel index.
- Response events cover rescind, open result, GPADL created/torndown, modify-channel response, and version response.
- Send-side events cover request-offers, open, close, establish GPADL header/body, teardown GPADL, negotiate version, release relid, TL connect, and modify-channel.
- Event class `vmbus_channel` backs channel scheduling, set-event, and channel callback events.

## Control Flow

The header follows Linux trace event convention: it defines `TRACE_SYSTEM hyperv`, guards declarations with `_HV_TRACE_H` and `TRACE_HEADER_MULTI_READ`, sets `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE`, and includes `<trace/define_trace.h>` outside the guard. Call sites invoke generated `trace_vmbus_*()` functions; enabled tracepoints copy selected fields into trace buffers and format them via `TP_printk`.

## State and Persistence Behavior

The header defines static tracepoint metadata, field layouts, and print formats. Runtime state is owned by the tracing subsystem. The selected fields are stable observability contracts: changing field names or types affects trace consumers and tooling.

## Dependencies and Integration Points

Trace arguments depend on VMBus protocol structures from `hyperv_vmbus.h` and GUID export formatting. Events are used by `channel_mgmt.c`, `connection.c`, and channel/ring code to debug VMBus lifecycle and host communication.

## Risks and Edge Cases

Tracepoints must not dereference invalid channel or message pointers after an object can be freed. GUID arrays must be filled with `export_guid()` before `%pUl` formatting. Print formats and field names are user-visible in tracefs and should be treated as compatibility-sensitive. Include-path settings must match the source layout or trace generation fails.

## Test Signals

Enable each event group under tracefs, run VMBus device enumeration, channel open/close, GPADL creation, rescind, CPU retargeting, and TL connect scenarios, and verify field values match host messages without build warnings from trace macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv_trace.h -->

# sources/distributed-fs/ceph-client/drivers/scsi/sd_trace.h

## Purpose

`sd_trace.h` defines tracepoints for SCSI disk zoned-block behavior. It is included by `sd_zbc.c` with `CREATE_TRACE_POINTS` so tracing can observe zone append preparation and write-pointer update details.

## Important APIs, Types, and Functions

The trace system is `sd`. `TRACE_EVENT(scsi_prepare_zone_append)` records SCSI identity, LBA, and write-pointer offset. `TRACE_EVENT(scsi_zone_wp_update)` records SCSI identity, request sector, write-pointer offset, and good bytes. Both derive host/channel/id/lun from `struct scsi_cmnd`.

## Control Flow

The file is declarative. Runtime emission happens only when call sites execute and the tracepoints are enabled through tracefs/perf/ftrace. The bottom sets `TRACE_INCLUDE_PATH` and includes `trace/define_trace.h` outside the include guard, as required by tracepoint generation.

## State and Persistence Behavior

There is no driver state. Enabled events write records into kernel tracing buffers using the fixed schema declared here.

## Dependencies and Integration Points

It depends on Linux tracepoint infrastructure and SCSI command/device types. It integrates with `sd_zbc.c` as the tracepoint definition unit and with userspace tracing tools through the `sd` trace system.

## Risks and Edge Cases

Field types and print formats must stay aligned with call-site values, especially `sector_t` printed as `%llu`. The relative `TRACE_INCLUDE_PATH` is tied to the source layout. In this snapshot, the visible `sd_zbc.c` code does not show direct calls to these events, so they may support nearby-version or conditional zone append paths.

## Test Signals

Compile with tracing enabled and `sd_zbc.c` defining tracepoints. Enable `sd:scsi_prepare_zone_append` and `sd:scsi_zone_wp_update` on a zoned SCSI disk and verify identity, LBA, offset, and good-byte fields.

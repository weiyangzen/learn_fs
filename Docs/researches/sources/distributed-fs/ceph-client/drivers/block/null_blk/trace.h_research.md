# sources/distributed-fs/ceph-client/drivers/block/null_blk/trace.h

## Purpose
This header defines ftrace trace events for null_blk zoned operations and report-zones activity.

## Important APIs, Types, And Functions
It sets `TRACE_SYSTEM nullb`, declares `nullb_trace_disk_name()`, defines `__print_disk_name()`, and provides `__assign_disk_name()` for copying a `gendisk` name into trace entries. `TRACE_EVENT(nullb_zone_op)` records disk, request operation, zone number, and zone condition for a `struct nullb_cmd`. `TRACE_EVENT(nullb_report_zones)` records disk and number of zones reported for a `struct nullb`.

## Control Flow
Zoned code can call generated trace hooks when a zone operation or report-zones path occurs. The tracepoint fast-assign blocks copy stable values into the trace entry, and `TP_printk()` renders them using block operation and zone-condition string helpers.

## State And Persistence Behavior
Trace events do not alter device state. They capture transient snapshots into the ftrace ring buffer when enabled.

## Dependencies And Integration Points
The header depends on Linux tracepoint/trace_seq APIs, `null_blk.h`, gendisk names, blk-mq request access through `blk_mq_rq_from_pdu()`, `blk_op_str()`, and `blk_zone_cond_str()`. `TRACE_INCLUDE_PATH .` and `TRACE_INCLUDE_FILE trace` align with the local Makefile include path and generated trace code.

## Risks
Trace headers are sensitive to include guards and the `TRACE_HEADER_MULTI_READ` pattern. The event uses `__field_struct(enum req_op, op)` because normal `__field()` signedness handling does not work for bitwise enum types. Incorrect request-to-PDU assumptions would break trace assignment.

## Test Signals
Build with tracing and zoned null_blk enabled, then enable `nullb:nullb_zone_op` and `nullb:nullb_report_zones` through tracefs. Zone operations should report disk name, request operation, zone number, condition, and reported-zone counts.

# sources/distributed-fs/ceph-client/include/uapi/linux/blktrace_api.h

## Purpose

`sources/distributed-fs/ceph-client/include/uapi/linux/blktrace_api.h` exports the block I/O tracing event ABI. The complete 197-line header was read. It defines trace category masks, action codes, notify events, trace record layouts, remap payloads, setup states, and setup structures for the original and extended blktrace interfaces.

## Important APIs, Types, and Functions

There are no functions. Important enums are `blktrace_cat`, `blktrace_act`, and `blktrace_notify`. Important action macros combine base actions with category masks through `BLK_TC_ACT`, including queue, merge, request allocation, requeue, issue, complete, plug/unplug, insert, split, remap, abort, driver data, zone append/plug/unplug, and notify actions. Important structs are `blk_io_trace`, `blk_io_trace2`, `blk_io_trace_remap`, `blk_user_trace_setup`, and `blk_user_trace_setup2`.

## Control Flow

The header has no executable flow. Trace control flow is driven by setup ioctls in the block layer: userspace configures action masks, buffers, LBA ranges, and PID filters, starts tracing, reads event records, and stops tracing. Event consumers parse `magic` to distinguish `BLK_IO_TRACE_VERSION` and `BLK_IO_TRACE2_VERSION`, then decode action/category bits and any post-record PDU such as cgroup IDs, messages, driver data, or remap payloads.

## State and Persistence Behavior

The file owns no storage. It describes transient tracing sessions with states `Blktrace_setup`, `Blktrace_running`, and `Blktrace_stopped`. Trace records are runtime observations of block I/O, carrying sequence number, timestamp, sector, byte count, action, PID, device, CPU, error, and PDU length. Persistence occurs only if userspace records the trace stream.

## Dependencies and Integration Points

The direct dependency is `<linux/types.h>`. Integration points are kernel block tracepoints, relay/per-CPU trace buffers, legacy blktrace tooling, parsers that understand v1/v2 records, cgroup-aware tracing, zoned block tracing categories, and block driver-specific data PDUs.

## Risks and Edge Cases

Version handling matters: v1 has a 32-bit `action` and `__u16 act_mask`, while v2 extends action/masks to 64 bits for newer categories. Old tooling can miss zone or write-zeroes categories above bit 15. `pdu_len` requires bounds checking before reading trailing payload. `blk_io_trace_remap` uses big-endian fields. Setup names have different fixed lengths in v1 and v2. Trace streams are high volume, so buffer sizing and loss accounting need runtime validation outside this header.

## Test Signals

Useful tests include v1/v2 parser tests using `magic` and version fields, category mask tests above and below bit 16, remap payload endian tests, trace setup validation for LBA/PID filters, stress tests under high I/O to detect dropped events, and compatibility tests with existing blktrace/blkparse tools.

# sources/distributed-fs/ceph-client/drivers/android/binder_trace.h

## Purpose
`binder_trace.h` defines the Binder ftrace event surface for ioctl, read/write completion, waits, transactions, object/ref translation, fd transfer, buffer allocation/release, allocator page activity, commands/returns, and netlink reports.

## Important APIs, Types, And Functions
The file declares `TRACE_SYSTEM binder`, forward-declares Binder structs, and defines many `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, and `DEFINE_EVENT` entries. Major groups are `binder_ioctl`, function return events, `binder_wait_for_work`, transaction latency/free and send/receive events, node/ref translation events, fd send/recv events, buffer lifecycle events, page LRU/map/unmap events, `binder_command`, `binder_return`, and `binder_netlink_report`.

## Control Flow
The header expands into tracepoint definitions through `<trace/define_trace.h>`. Runtime Binder code calls `trace_binder_*` functions generated from this file. When tracing is disabled, event overhead is minimal; when enabled, fast-assign blocks read Binder struct fields and publish formatted event data.

## State And Persistence
Trace events do not own Binder state. They snapshot selected fields into the tracing ring buffer. Event definitions are compile-time ABI for tracing tools and persist as kernel tracepoint names and field layouts.

## Dependencies
It depends on Linux tracepoint infrastructure, Binder UAPI command/return string arrays, and stable field names in `struct binder_buffer`, `binder_alloc`, `binder_node`, `binder_ref_data`, `binder_proc`, `binder_thread`, and `binder_transaction`.

## Integration Points
`binder_alloc.c` emits page and buffer events. C Binder core and Rust Binder wrappers emit ioctl, command, return, wait, transaction, and fd events. Observability tools under ftrace/perf/tracefs consume the event schema.

## Risks
Tracepoint fast-assign code dereferences Binder structs, so layout changes must update event definitions. Rust Binder has a separate transaction representation and uses generated layout metadata; mismatches are risky. Trace fields are user-visible diagnostic ABI in practice, so renaming/removing events can break tooling. Netlink report trace fields assume C `binder_transaction` members such as `to_proc` and `to_thread`.

## Test Signals
Compile with tracing enabled, list `binder:*` events in tracefs, enable transaction/buffer/page events during Binder IPC stress, verify event field values against Binder debug logs, run allocator KUnit with page tracepoints enabled, and test Rust Binder trace wrapper build compatibility.

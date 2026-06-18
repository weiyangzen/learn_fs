# sources/distributed-fs/ceph-client/net/core/net-traces.c

## Purpose

`net-traces.c` centralizes creation and export of networking tracepoints. By defining `CREATE_TRACE_POINTS` and including networking trace event headers, it emits the storage/metadata for tracepoints used across the networking stack.

## Important APIs, Types, And Functions

The file has no regular functions. Its important operations are trace-event header inclusion and `EXPORT_TRACEPOINT_SYMBOL_GPL()` calls for selected tracepoints. Exported tracepoints include bridge FDB/MDB events when bridge is enabled, neighbor events (`neigh_update`, `neigh_update_done`, `neigh_timer_handler`, `neigh_event_send_done`, `neigh_event_send_dead`, `neigh_cleanup_and_release`), `kfree_skb`, `napi_poll`, TCP reset/checksum events, UDP receive queue failure, and `sk_data_ready`.

## Control Flow

At build time, trace event headers expand into tracepoint definitions because `CREATE_TRACE_POINTS` is set before inclusion. At module/link time, the selected tracepoints are exported so GPL modules can attach or reference them. Conditional includes depend on `CONFIG_BRIDGE` and `CONFIG_PAGE_POOL`.

## State And Persistence Behavior

Tracepoint definitions are static kernel instrumentation state. Runtime tracing state is controlled by ftrace/perf/BPF/tracing subsystems, not by this file. No persistent data is stored here.

## Dependencies And Integration Points

This file integrates with the kernel tracepoint subsystem and networking trace headers for skb, net, napi, sock, udp, tcp, fib, qdisc, bridge, page_pool, and neigh events. It is an observability bridge for core networking, protocol code, and loadable modules.

## Risks

Tracepoint ABI stability matters because BPF and tracing tools can depend on event names and fields defined in the included headers. Missing exports can break modules that reference tracepoints; exporting too broadly can expose unstable instrumentation. Conditional compilation must match the availability of trace headers and features.

## Test Signals

Build tests across configs with and without bridge/page_pool are important. Runtime signals include listing events under tracefs, attaching perf/ftrace/BPF programs to exported tracepoints, and verifying neighbor, NAPI, skb drop, TCP, UDP, and bridge trace events fire in expected paths.

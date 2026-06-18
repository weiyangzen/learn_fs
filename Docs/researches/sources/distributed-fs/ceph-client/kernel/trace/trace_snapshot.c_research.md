# sources/distributed-fs/ceph-client/kernel/trace/trace_snapshot.c

## Purpose

`trace_snapshot.c` manages ftrace snapshot and max-latency buffers. It handles boot snapshot parameters, manual snapshot tracefs operations, conditional snapshots, max trace updates, snapshot mmap exclusion, ftrace snapshot commands, and boot-time snapshot capture. The complete 1066-line file was read.

## Important APIs, Types, and Functions

Important APIs include `tracing_snapshot_instance()`, `tracing_snapshot_cond()`, `tracing_cond_snapshot_data()`, `resize_buffer_duplicate_size()`, `tracing_alloc_snapshot_instance()`, `free_snapshot()`, `tracing_arm_snapshot_locked()`, `tracing_arm_snapshot()`, `tracing_disarm_snapshot()`, `tracing_snapshot_alloc()`, `tracing_snapshot_cond_enable()`, `tracing_snapshot_cond_disable()`, `trace_create_maxlat_file()`, `update_max_tr()`, `update_max_tr_single()`, `get_snapshot_map()`, `put_snapshot_map()`, `register_snapshot_cmd()`, `trace_allocate_snapshot()`, `do_allocate_snapshot()`, and `ftrace_boot_snapshot()`.

## Control Flow

Boot parameters request early allocation or named-instance snapshots. Manual writes to `snapshot` allocate, swap, clear, reset, or free buffers depending on value and CPU scope. Snapshot updates check allocation, NMI context, mapped buffers, active snapshot-using tracers, and conditional callbacks before swapping buffers under `max_lock`. Ftrace `:snapshot` commands arm snapshot accounting before registering probes.

## State and Persistence Behavior

Per-trace-array state includes `allocated_snapshot`, `snapshot_buffer`, arm count, mapped count, `cond_snapshot`, `max_latency`, max trace task metadata, and optional fsnotify work. Global boot state tracks allocation requests and boot snapshot names.

## Dependencies and Integration Points

It integrates with ring buffer resize/swap APIs, trace array locking, tracefs, raw buffers, latency tracers, ftrace function commands, fsnotify/irq_work, boot setup parsing, and snapshot-compatible tracer policy.

## Risks and Edge Cases

Snapshots are mutually exclusive with mapped buffers, active snapshot-using tracers, and conditional updates. Per-CPU swaps can fail during commit or resize. Arm/disarm accounting must be balanced. Conditional callbacks run under `max_lock`. Boot name matching can allocate all instances when no names are supplied.

## Test Signals

Test boot parameters, manual `snapshot` writes for 0/1/other values, per-CPU behavior, raw reads, conditional snapshots, mmap exclusion, ftrace snapshot commands with counts, and max-latency file updates.

# sources/control-plane/mayastor/io-engine/src/core/device_monitor.rs

## Purpose
Provides a lightweight asynchronous monitor loop for deferred device-management commands. Its current command closes or retires a failed child from a nexus on the primary reactor rather than directly from the device event callback path.

## Important APIs, Types, and Functions
- `DeviceCommand::RetireDevice { nexus_name, child_device }` is the only queued command.
- `DEV_CMD_QUEUE` is a global `WorkQueue<DeviceCommand>`.
- `device_cmd_queue()` exposes the queue to device-event handlers.
- `device_monitor_loop()` polls the queue every 10 ms and schedules work on the primary SPDK thread with `Reactor::spawn_at_primary`.

## Control Flow and State
Producers enqueue `RetireDevice` commands, for example when a nexus child receives device removal or admin-queue failure events. The monitor loop ticks forever. For each command it looks up the nexus by name, calls `close_child(child_device).await`, logs verbose errors, and awaits the oneshot returned by `spawn_at_primary`.

State is volatile queue state only. Commands are not persisted, deduplicated, or retried after process restart.

## Dependencies and Integration Points
Depends on `WorkQueue`, `Reactor`, `nexus_lookup`, and `VerboseError`. It bridges event paths into reactor-affine nexus mutation, avoiding direct manipulation from arbitrary async contexts.

## Risks and Test Signals
The loop consumes one command per tick and has no backpressure beyond the unbounded `SegQueue`; a storm of device events can build latency. Failed scheduling logs and drops the command. Tests should verify retire commands are scheduled on primary, nexus lookup absence is harmless, close errors are logged, and queue ordering/throughput remain acceptable under bursts.

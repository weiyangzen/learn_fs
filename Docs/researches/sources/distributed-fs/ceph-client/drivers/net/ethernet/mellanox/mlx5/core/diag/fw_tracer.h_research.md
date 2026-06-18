# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/fw_tracer.h

## Purpose

`fw_tracer.h` defines the firmware tracer data model, constants, firmware event layouts, state bits, and public lifecycle/API entry points.

## Important APIs, Types, and Functions

- Constants define string DB section counts/read sizes, trace buffer geometry, block size, saved trace count, parameter limits, and timestamp masks.
- `struct mlx5_fw_trace_data` is the saved decoded trace object exported to devlink.
- `struct mlx5_fw_tracer` holds core device pointer, EQ notifier, workqueue/work items, string DB state, DMA buffer state, saved trace ring, timestamp/hash/list state, and locks.
- `struct tracer_string_format`, `struct tracer_event`, `struct tracer_string_event`, and `struct tracer_timestamp_event` describe decoded or partially decoded firmware trace records.
- Public prototypes cover create/init/cleanup/destroy, core dump trigger, saved trace export, and reload.

## Control Flow

The header separates software resource creation from hardware activation: callers create once, initialize when device hardware is up, cleanup before teardown/reset, destroy at final device release, and reload on firmware string DB update.

## State and Persistence Behavior

The declared `mlx5_fw_tracer` object persists across active tracing sessions and reloads. It owns memory that firmware writes through an mkey, cached string DB data, saved decoded traces, and synchronization state.

## Dependencies and Integration Points

Depends on Linux mlx5 driver headers and `mlx5_core.h`. It is consumed by `fw_tracer.c`, the tracepoint header, and health/devlink diagnostics that dump saved firmware traces.

## Risks and Edge Cases

- Buffer geometry constants assume `TRACE_BUFFER_SIZE_BYTE` is a power-of-two multiple of `TRACER_BLOCK_SIZE_BYTE`.
- `SAVED_TRACES_NUM` is used with bitmask wrapping, so it must remain a power of two.
- Firmware event bitfield declarations must match device IFC layouts.
- Public callers must treat `ERR_PTR` and `NULL` tracer returns as valid unsupported/error states.

## Test Signals

Compile with firmware tracer users. Add static/build checks if constants change. Exercise lifecycle: create, init, cleanup, reload, destroy, and saved trace export.

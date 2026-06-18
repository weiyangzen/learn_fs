# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/dev/diag/dev_tracepoint.h

## Purpose

`sf/dev/diag/dev_tracepoint.h` defines tracepoints for SF auxiliary device creation and deletion. It provides observability for the SF device table in `sf/dev/dev.c`.

## Important APIs and Control Flow

The file declares an event class `mlx5_sf_dev_template` with fields for parent device name, SF device pointer, auxiliary id, hardware function id, and SF number. It then defines `mlx5_sf_dev_add` and `mlx5_sf_dev_del` events from that class. The trace include path/file footer enables Linux tracepoint code generation when included with `CREATE_TRACE_POINTS`.

## State and Dependencies

Tracepoints do not mutate driver state. They depend on Linux tracepoint infrastructure, `struct mlx5_core_dev`, and `struct mlx5_sf_dev`. The fast assignment reads `dev_name(dev->device)`, `sfdev->fn_id`, and `sfdev->sfnum`.

## Risks and Test Signals

The header must remain include-guarded for multi-read trace generation and the relative include path to `dev.h` must match the source tree. Test by enabling ftrace/perf trace events and confirming add/delete events fire with matching auxiliary ids and function ids during SF activation and teardown.

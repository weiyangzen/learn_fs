# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/en_tc_tracepoint.c

## Purpose

`en_tc_tracepoint.c` instantiates mlx5 TC tracepoints and provides helpers to convert Linux flow action IDs into printable action names.

## Important APIs, Types, and Functions

- `CREATE_TRACE_POINTS` causes `en_tc_tracepoint.h` tracepoints to be defined here.
- `put_ids_to_array()` copies `flow_action_entry.id` values into tracepoint dynamic arrays.
- `parse_action()` formats an array of action IDs into action names using `FLOWACT2STR`.
- `FLOWACT2STR` maps supported `FLOW_ACTION_*` IDs to fixed 16-byte names.

## Control Flow

TC tracepoint fast-assign code calls `put_ids_to_array()` to snapshot action IDs. Print formatting calls `parse_action()`, which writes action names into the trace sequence and returns the resulting buffer pointer.

## State and Persistence Behavior

No persistent driver state is changed. Output exists only in trace buffers.

## Dependencies and Integration Points

Depends on `en_tc_tracepoint.h`, Linux `flow_offload.h`, and trace sequence helpers. It integrates with mlx5e TC flower configure/delete/stats tracepoints.

## Risks and Edge Cases

- `FLOWACT2STR` must track `NUM_FLOW_ACTIONS`; newer action IDs not listed print `UNKNOWN`.
- Names are fixed-width by declaration, so longer future names require updating `NAME_SIZE`.

## Test Signals

Compile after kernel flow action enum changes. Enable `mlx5e_configure_flower` tracing and install TC flower rules with varied actions to verify printed action names and unknown handling.

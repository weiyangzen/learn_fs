# sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_strings.c

## Purpose

`drbd_strings.c` maps DRBD state enums and state-change error codes to stable human-readable strings. It is used by logging, state transition diagnostics, and any output path that needs textual names for connection, role, disk, or state validation results.

## Important APIs and Data

The file defines static indexed string tables for connection states (`drbd_conn_s_names`), roles (`drbd_role_s_names`), disk states (`drbd_disk_s_names`), and negative state-machine return codes (`drbd_state_sw_errors`). Exported functions are `drbd_conn_str(enum drbd_conns)`, `drbd_role_str(enum drbd_role)`, `drbd_disk_str(enum drbd_disk_state)`, and `drbd_set_st_err_str(enum drbd_state_rv)`.

## Control Flow

Each conversion function is a bounds-checked table lookup. Invalid high enum values return `"TOO_LARGE"`. `drbd_set_st_err_str()` additionally checks whether an error is below the known negative range and returns `"TOO_SMALL"` before indexing with `-err` into the negative-code table.

## State and Persistence Behavior

The file is read-only at runtime. It has no persistence behavior and no mutable state. Its table indexes must stay aligned with the enum numeric values in DRBD public/core headers.

## Dependencies and Integration Points

The file includes `<linux/drbd.h>` for enum definitions and `drbd_strings.h` for prototypes. It is directly used by `drbd_state.c` to print failed transitions and state changes, and likely by other DRBD modules for logs or diagnostics.

## Risks and Edge Cases

Sparse designated initializers make enum drift visible at compile time only if constants remain defined, but not if ranges change without table updates. The error table indexes negative enum values; a bad range check would turn an invalid code into an out-of-bounds access. Callers should not parse these strings as protocol because they are diagnostic names.

## Test Signals

Compile coverage catches missing enum constants. Runtime checks should cover all valid connection, role, disk, and state-error values plus out-of-range high/low values. State-transition failure tests should assert useful messages appear for two-primary rejection, no up-to-date disk, active resync, missing verify algorithm, unsupported protocol, transient state, and peer-refused cluster-wide change.

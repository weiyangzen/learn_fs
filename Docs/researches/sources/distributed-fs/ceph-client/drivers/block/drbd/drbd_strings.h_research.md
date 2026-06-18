# sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_strings.h

## Purpose

`drbd_strings.h` declares the enum-to-string helpers implemented in `drbd_strings.c`. It is a narrow diagnostic interface for translating DRBD connection, role, disk, and state return-code values.

## Important APIs

The header exports `drbd_conn_str()`, `drbd_role_str()`, `drbd_disk_str()`, and `drbd_set_st_err_str()`. Each returns a `const char *` for use in logs, state dumps, and error messages.

## Control Flow

The header has no control flow beyond include guards. Callers include it when they need textual state names and delegate all bounds checking to the implementation.

## State and Persistence Behavior

There is no state or persistence. The functions expose static string data owned by `drbd_strings.c`; callers must treat returned pointers as immutable.

## Dependencies and Integration Points

The prototypes rely on DRBD enum declarations being visible before use, typically through `<linux/drbd.h>` or DRBD internal headers. Integration points are diagnostic paths in `drbd_state.c`, request/worker logging, and any administrative or notification formatting code that wants canonical state names.

## Risks and Edge Cases

Because the header does not include the enum-defining header itself, include order matters for standalone users. The interface is unsuitable for wire-format compatibility because string spelling is diagnostic, not a negotiated protocol.

## Test Signals

Build tests should catch missing enum declarations at include sites. Runtime tests belong with `drbd_strings.c` and should verify valid and invalid enum conversions.

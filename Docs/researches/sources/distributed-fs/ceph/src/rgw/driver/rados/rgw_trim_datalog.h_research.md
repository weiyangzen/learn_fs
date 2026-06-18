# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_trim_datalog.h

## Purpose

`sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_trim_datalog.h` declares factory functions for periodic and admin data-log trim coroutines.

## Important APIs, Types, and Functions

`create_data_log_trim_cr()` creates the periodic datalog trim coroutine from a `DoutPrefixProvider`, `RadosStore`, `RGWHTTPManager`, shard count, and interval. `create_admin_data_log_trim_cr()` creates a one-shot/admin trim coroutine with caller-supplied last markers.

## Control Flow

The header contains no executable flow. Callers choose the periodic factory for daemon trim loops or the admin factory for direct trim commands.

## State and Persistence Behavior

No state is owned by the header. The admin factory accepts a marker vector by reference so the implementation can update caller-visible in-memory trim positions.

## Dependencies and Integration Points

It depends on `common/dout.h`, forward-declared RGW coroutine/RADOS/HTTP types, and `utime_t`. It integrates with RGW service startup and radosgw-admin trim commands.

## Risks and Edge Cases

Callers must pass the correct shard count and a marker vector sized consistently with the datalog. Incorrect values can limit or misdirect trimming in the implementation.

## Test Signals

Compile coverage for service/admin callers and runtime tests that instantiate both factories with representative shard counts and intervals.

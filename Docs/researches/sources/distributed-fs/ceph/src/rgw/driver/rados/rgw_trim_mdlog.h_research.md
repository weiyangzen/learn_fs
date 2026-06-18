# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_trim_mdlog.h

## Purpose

`sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_trim_mdlog.h` declares factory functions for metadata-log trim coroutines.

## Important APIs, Types, and Functions

`create_meta_log_trim_cr()` creates the daemon periodic metadata-log trim coroutine. `create_admin_meta_log_trim_cr()` creates a one-shot/admin metadata-log trim coroutine. Both take a `DoutPrefixProvider`, `RadosStore`, `RGWHTTPManager`, and shard count; the periodic factory also takes a `utime_t` interval.

## Control Flow

The header has no executable flow. The implementation chooses master or peer trim behavior based on the zone service's metadata-master role and validates endpoints before returning a coroutine.

## State and Persistence Behavior

No state is owned by the header. The returned coroutines mutate mdlog RADOS state and mdlog history through the implementation.

## Dependencies and Integration Points

The header forward declares RGW coroutine, RADOS store, HTTP manager, and interval types. It is consumed by RGW service startup and radosgw-admin trim paths.

## Risks and Edge Cases

Callers must provide the correct shard count and a live HTTP manager; a null returned coroutine from failed endpoint sanity checks must be handled by callers.

## Test Signals

Compile coverage for daemon/admin callers and runtime tests for factory behavior in metadata-master and peer zones, including misconfigured endpoints.

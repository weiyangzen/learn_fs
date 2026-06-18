# sources/distributed-fs/ceph/src/rgw/rgw_usage.h

## Purpose
`rgw_usage.h` declares static helpers for RGW usage-log reporting and maintenance.

## Important APIs, Types, and Functions
`RGWUsage::show()` formats usage logs over a time range with optional entries, summaries, and category filtering. `trim()` removes usage records for a scope. `clear()` removes all usage records through the driver.

## Control Flow
The API is stateless; callers choose driver/user/bucket pointers to define scope and pass a formatter flusher for output.

## State and Persistence Behavior
The class itself has no fields. Persistence is owned by the SAL backend invoked by the implementation.

## Dependencies and Integration Points
Depends on Formatter, Dout, RGW formats, RADOS user types, SAL forwards, and optional yield context. Used by `radosgw-admin usage` style operations.

## Risks
Null/non-null pointer combinations define behavior and must be passed consistently. Static API makes mocking require mock SAL objects.

## Test Signals
Compile and integration tests should validate scope precedence: bucket over user over driver.

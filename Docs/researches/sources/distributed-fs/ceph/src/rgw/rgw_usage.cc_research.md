# sources/distributed-fs/ceph/src/rgw/rgw_usage.cc

## Purpose
`rgw_usage.cc` implements display, trim, and clear operations for RGW usage logs.

## Important APIs, Types, and Functions
`dump_usage_categories_info()` emits per-category bytes/ops counters with optional filtering. `RGWUsage::show()` pages usage entries from a bucket, user, or all-driver scope, formats detailed entries and/or summaries, and flushes output incrementally. `trim()` delegates usage deletion by scope. `clear()` clears all usage through the driver.

## Control Flow
`show()` opens a top-level `usage` object, loops while backend results are truncated, reads up to 1000 entries at a time, optionally emits entries grouped by user, aggregates per-user summaries, handles `-ENOENT` as empty, then emits summary totals if requested.

## State and Persistence Behavior
Usage data is read and trimmed through SAL bucket/user/driver interfaces. Local `summary_map` aggregates transient display totals. `trim()` and `clear()` mutate persisted usage logs.

## Dependencies and Integration Points
Depends on SAL Driver/User/Bucket usage APIs, `rgw_usage_log_entry`, `rgw_user_bucket`, Formatter flusher, and RGW formats. Used by admin commands and usage APIs.

## Risks
`usage` map is not cleared inside the pagination loop, so stale entries could be reprocessed if backend appends rather than replaces. Category filtering affects totals and category display. The function assumes map ordering groups users for entry output.

## Test Signals
Cover all three scopes, pagination, `-ENOENT`, entries-only, summary-only, category filters, s3select counters, trim/clear delegation, and large result flushing.

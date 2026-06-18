# File Research: sources/block-storage/lvm2/libdm/libdm-targets.c

## Summary
Parses status strings returned by multiple device-mapper targets into structured libdm status objects. It covers snapshot, raid, cache, writecache, integrity, thin-pool, thin, and mirror targets.

## Main Responsibilities
- Converts target-specific status text into pool-allocated structs.
- Recognizes target error/fail states where status output is symbolic rather than fully numeric.
- Handles multiple kernel status-format versions for raid, cache, and thin-pool targets.
- Parses device health, sync progress, cache policy arguments, and thin provisioning status flags.

## Key APIs
- `dm_get_status_snapshot()`
- `dm_get_status_raid()`
- `dm_get_status_cache()`
- `dm_get_status_writecache()`
- `dm_get_status_integrity()`
- `parse_thin_pool_status()`
- `dm_get_status_thin_pool()`
- `dm_get_status_thin()`
- `dm_get_status_mirror()`

## Important Behavior
Snapshot status accepts numeric `used/total [metadata]` data plus symbolic states `Invalid`, `Merge failed`, and `Overflow`.

Raid parsing counts space-delimited fields to support old 4-field output, 1.5.0+ 6-field output, and 1.9.0+ 7-field output. It truncates reported device health to the usable device count and includes compatibility adjustments for misleading lowercase `a` raid leg states during resync/recover/idle transitions.

Cache parsing reads fixed numeric fields first, then scans feature flags such as `writethrough`, `writeback`, `passthrough`, `metadata2`, and `no_discard_passdown`. It stores core and policy arguments as argv-style arrays and detects `ro` and `needs_check`.

Thin-pool parsing handles `Error`, `Fail`, transaction ID, metadata/data usage, discard policy, out-of-data/read-only state, `error_if_no_space`, and `needs_check`. Thin device status supports `-`, `Fail`, or mapped/highest sector pairs.

Mirror parsing reads image devices, sync ratio, per-image health chars, log type, optional log devices, and log health. Health chars map to alive, flush/write/sync/read failed, or unclassified states.

## State and Lifetime
All status structs and nested strings/arrays are allocated from the caller's `dm_pool`. On parse failure, the function frees the top-level struct from that pool when possible and returns `0` with `*status = NULL`.

## Risks
The parsers assume single-space field delimiting in helper functions. Several optional-state detections use substring checks, so they depend on kernel status strings remaining unambiguous. Unknown cache features are logged but do not abort parsing.

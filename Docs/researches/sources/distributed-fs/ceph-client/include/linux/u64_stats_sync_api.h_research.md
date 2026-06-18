# sources/distributed-fs/ceph-client/include/linux/u64_stats_sync_api.h

## Purpose
Compatibility include wrapper for the u64 stats synchronization API.

## Important APIs, Types, And Functions
It only includes `linux/u64_stats_sync.h`; all exported types and functions come from that header.

## Control Flow
No control flow.

## State, Persistence, And Dependencies
No state beyond the included API. Dependency is exactly `u64_stats_sync.h`.

## Integration Points
Allows users that include the `_api` header name to receive the canonical u64 stats API.

## Risks And Test Signals
Risks are limited to include-path churn or accidental divergence. Test signals are compile coverage for files including `u64_stats_sync_api.h`.

# sources/cloud-native/moby/daemon/server/router/system/disk_usage_test.go

## Purpose
This test validates legacy `/system/df` image-list compatibility for `VirtualSize`.

## Important APIs, Types, And Functions
`TestDiskUsageVirtualSize` builds a `legacyDiskUsage`, wraps image summaries with `compat.Wrap`, marshals JSON, and checks `VirtualSize` presence/absence and empty-list behavior.

## Control Flow
Subtests verify API <1.44 wrapped responses include `VirtualSize`, API >=1.44 raw responses omit it, and an empty image slice remains an empty JSON array when wrapped.

## State And Persistence
No state is persisted.

## Dependencies And Integration Points
Protects `getDiskUsage` compatibility logic and depends on API image types plus `compat`.

## Risks
Legacy disk-usage clients may depend on `VirtualSize` and empty arrays instead of null/omitted values.

## Test Signals
Direct JSON assertions provide strong regression coverage for response shape.

# sources/cloud-native/moby/client/system_disk_usage_test.go

## Purpose
Tests disk-usage request errors, option query construction, current response decoding, legacy conversion, and image reclaimable calculations.

## APIs, Types, And Functions
The tests include `TestDiskUsageError`, `TestDiskUsage`, `TestDiskUsageWithOptions`, `TestLegacyDiskUsage`, and `TestImageDiskUsageFromLegacyAPI`. They use system, image, container, volume, and build-cache API fixtures.

## Control Flow, State, And Integration
Mock handlers validate `GET /system/df`, query type selections, and verbose flag behavior. Fixtures exercise current `system.DiskUsage` decoding and legacy response conversion for counts, totals, active objects, and reclaimable space.

## Risks And Test Signals
Signals are strong around version compatibility and accounting math. The tests catch regressions in legacy behavior that could otherwise silently skew CLI or API consumers' disk cleanup recommendations.

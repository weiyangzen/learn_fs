# sources/cloud-native/moby/daemon/server/router/system/disk_usage.go

## Purpose
`disk_usage.go` defines compatibility response structs for `/system/df`.

## Important APIs, Types, And Functions
`diskUsageCompat` embeds `legacyDiskUsage` and `system.DiskUsage` so API 1.52 can return both old and new shapes. `legacyDiskUsage` contains `LayersSize`, `Images`, `Containers`, `Volumes`, and `BuildCache`.

## Control Flow
`getDiskUsage` fills `legacyDiskUsage` from the new `backend.DiskUsage` model and conditionally wraps/returns it based on API version and `verbose`.

## State And Persistence
No state is stored; these are response DTOs.

## Dependencies And Integration Points
Depends on API build/container/image/system/volume types and is used by `system_routes.go`.

## Risks
JSON tags and embedded structs define public wire shape; changing them can break clients.

## Test Signals
`disk_usage_test.go` verifies legacy image `VirtualSize` injection.

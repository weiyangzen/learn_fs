# sources/cloud-native/moby/client/system_disk_usage.go

## Purpose
Implements `Client.DiskUsage`, normalizing daemon disk-usage responses into a richer client result across current and legacy API versions.

## APIs, Types, And Functions
Important types are `DiskUsageOptions`, `DiskUsageResult`, `ContainersDiskUsage`, `ImagesDiskUsage`, `VolumesDiskUsage`, `BuildCacheDiskUsage`, and `legacyDiskUsage`. Conversion helpers include `diskUsageResultFromLegacyAPI`, `imageDiskUsageFromLegacyAPI`, `containerDiskUsageFromLegacyAPI`, `buildCacheDiskUsageFromLegacyAPI`, and `volumeDiskUsageFromLegacyAPI`.

## Control Flow, State, And Integration
The method builds `type=` query entries for requested object classes and `verbose=1` when needed, calls `GET /system/df`, and selects decode behavior based on `cli.version < 1.52`. Current responses expose object-specific usage structs; legacy responses are converted by computing totals, active counts, and reclaimable bytes from item lists.

## Risks And Test Signals
Risks include API-version branching, reclaimable calculations, omitted verbose item clones, negative image container counts, shared build-cache sizing, and volume usage data being nil. Integration is with daemon system accounting, image/container/volume/build API types, and CLI disk-usage displays.

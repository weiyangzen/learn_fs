# sources/cloud-native/moby/daemon/disk_usage.go

## Purpose
Computes daemon disk usage summaries for containers, images, and local volumes, with singleflight de-duplication and parallel aggregation for API callers such as `docker system df`.

## Important APIs, Types, And Functions
- `containerDiskUsage` lists all containers with size and computes total, active, and reclaimable RW size.
- `imageDiskUsage` lists images with shared size, computes total layer usage through `imageService.ImageDiskUsage`, and derives reclaimable image bytes.
- `localVolumesSize` calls the volume service and computes total, active, and reclaimable local volume size.
- `SystemDiskUsage` runs requested categories in an `errgroup`.

## Control Flow
Each category uses a daemon-level `singleflight.Group` keyed by verbosity or unit key so concurrent identical calculations share one result. `SystemDiskUsage` starts goroutines for selected categories, waits for all, and returns the assembled `backend.DiskUsage` or the first error.

## State And Persistence
Does not persist new state. It reads container/image/volume metadata and size data. It strips image manifest descriptors from verbose container results before returning so they are not included in disk usage payloads.

## Dependencies And Integration Points
Uses daemon container listing, image backend list and layer disk usage, volume service `LocalVolumesSize`, filters, backend disk usage API structs, and `errgroup`.

## Risks And Edge Cases
Shared singleflight results must not be mutated by callers; the public comment warns against mutating returned fields. Images with unknown container counts are treated as active to avoid over-reporting reclaimable space. Volume sizes of `-1` are excluded from totals.

## Test Signals
No direct tests in this subset. Integration signals include correct `system df` totals, verbose item inclusion, reclaimable calculations, and no duplicate expensive size scans under concurrent requests.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/overlay/overlay_disk_quota.go -->
# sources/cloud-native/containers-storage/drivers/overlay/overlay_disk_quota.go

## Purpose
This Linux+cgo quota-enabled overlay companion implements writable-layer disk usage reporting when project quota support is available.

## Important APIs, Types, And Functions
`(*Driver).ReadWriteDiskUsage(id string)` returns `*directory.DiskUsage`. It uses `d.quotaCtl.GetDiskUsage(d.dir(id), usage)` when `quotaCtl` exists and otherwise falls back to `directory.Usage(<layer>/diff)`.

## Control Flow
The function creates an empty usage object, checks whether the driver initialized a quota controller, and either queries XFS project quota accounting or scans the `diff` directory.

## State And Persistence
No new state is written here. It reads quota state already assigned by `overlay.go`/`quota.Control`, or reads filesystem metadata under the layer `diff` directory.

## Dependencies And Integration Points
This file depends on `pkg/directory` and the quota controller field on `Driver`. It is selected only for `linux && cgo && !exclude_disk_quota`, complementing the unsupported build.

## Risks And Test Signals
Quota accounting can fail if backing block device nodes or project IDs are missing; in that case the error from `GetDiskUsage` is returned. Fallback scanning is slower and may differ from quota usage for sparse/reflinked files. Coverage is primarily through graphdriver disk-usage tests on quota-capable XFS systems.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/overlay/overlay_disk_quota.go -->

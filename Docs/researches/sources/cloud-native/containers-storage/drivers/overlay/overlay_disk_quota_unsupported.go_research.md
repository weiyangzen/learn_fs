<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/overlay/overlay_disk_quota_unsupported.go -->
# sources/cloud-native/containers-storage/drivers/overlay/overlay_disk_quota_unsupported.go

## Purpose
This alternate build implements overlay writable-layer usage reporting when cgo or disk quota support is unavailable.

## Important APIs, Types, And Functions
`(*Driver).ReadWriteDiskUsage(id string)` always returns `directory.Usage(path.Join(d.dir(id), "diff"))`.

## Control Flow
There is no branching except normal directory scanning error propagation.

## State And Persistence
It reads filesystem state only; it does not interact with project quota metadata.

## Dependencies And Integration Points
The build tag `linux && (!cgo || exclude_disk_quota)` prevents duplicate definitions with the quota-enabled file.

## Risks And Test Signals
Usage reflects recursive directory accounting rather than quota counters. It can be expensive on large writable layers and may not represent deduplicated/reflinked storage the same way as quota accounting.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/overlay/overlay_disk_quota_unsupported.go -->

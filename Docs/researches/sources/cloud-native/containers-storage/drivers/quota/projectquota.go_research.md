<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/quota/projectquota.go -->
# sources/cloud-native/containers-storage/drivers/quota/projectquota.go

## Purpose
This shared quota file defines the backing block device link name used by project quota support.

## Important APIs, Types, And Functions
`BackingFsBlockDeviceLink` is the filename `backingFsBlockDev`.

## Control Flow
There is no runtime control flow.

## State And Persistence
Quota-enabled builds create a block device node with this name under the driver home so `quotactl` can address the backing filesystem. Overlay `ListLayers` skips it as non-layer state.

## Dependencies And Integration Points
The constant is consumed by the quota implementation and overlay driver layer listing.

## Risks And Test Signals
Renaming the constant would break compatibility with existing driver home layouts and cleanup/listing logic.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/quota/projectquota.go -->

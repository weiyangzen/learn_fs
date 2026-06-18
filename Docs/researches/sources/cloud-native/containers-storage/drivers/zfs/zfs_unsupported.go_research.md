<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/zfs/zfs_unsupported.go -->
# sources/cloud-native/containers-storage/drivers/zfs/zfs_unsupported.go

## Purpose
This file provides an empty `zfs` package on platforms where the ZFS implementation is not built.

## Important APIs, Types, And Functions
There are no declarations beyond the package statement.

## Control Flow
No runtime behavior exists.

## State And Persistence
No state is read or written.

## Dependencies And Integration Points
The build tag `!linux && !freebsd` lets imports of the package compile without registering a usable driver.

## Risks And Test Signals
Consumers must rely on build tags/registration and driver lookup results rather than expecting a runtime unsupported error from this package.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/zfs/zfs_unsupported.go -->

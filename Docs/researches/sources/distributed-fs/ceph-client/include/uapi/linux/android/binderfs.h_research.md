<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/android/binderfs.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/android/binderfs.h

## Purpose
Defines the binderfs control ioctl for dynamically creating Binder device nodes inside a binderfs mount.

## Important APIs, Types, And Functions
`BINDERFS_MAX_NAME` bounds device names. `struct binderfs_device` carries requested device name and returned major/minor numbers. `BINDER_CTL_ADD` is the `_IOWR` ioctl used on the binder-control node.

## Control Flow
Userspace mounts binderfs, opens the control device, fills a `binderfs_device` name, calls `BINDER_CTL_ADD`, and receives the allocated device major/minor for the new binder node.

## State And Persistence
Created binder devices persist in the binderfs mount namespace until removed/unmounted. Major/minor values are kernel allocation state.

## Dependencies And Integration Points
Depends on Binder UAPI, Linux types, and ioctl definitions. Integrates with Android containerization, per-namespace Binder device provisioning, and service managers.

## Risks And Edge Cases
Name length and termination, duplicate names, permission checks, mount namespace isolation, and major/minor exhaustion should be validated.

## Test Signals
Mount binderfs, add devices with valid/invalid names, check returned device numbers, duplicate creation behavior, and Binder operation on the created nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/android/binderfs.h -->

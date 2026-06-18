# File Research: sources/block-storage/devicemapper-rs/src/core/dm_udev_sync.rs

## Purpose
Implements device-mapper udev synchronization using SysV semaphores on non-Android platforms, and a no-op implementation on Android.

## Key APIs
`UdevSyncAction::{begin,end,cancel,is_active}` and exported `UdevSync`.

## Non-Android Behavior
Checks SysV semaphore support through `SEM_INFO`, warns on low semaphore limits, and detects udev via `/run/udev/control`. For remove/rename/resume ioctls, when udev is running and not suspending, it creates a random nonzero cookie, allocates a one-semaphore set, encodes `DM_UDEV_PRIMARY_SOURCE_FLAG`, increments initial state, waits for udev completion at end, and removes the semaphore. If no uevent was generated, it decrements locally to clear state.

## Failure Handling
Semaphore creation retries on key collision. Allocation/setup failures destroy partially-created semaphores. `cancel` destroys without waiting after ioctl failure.

## Tests/Notes
Tests cover invalid semaphore args, create/destroy, active/inactive sync, cancel, no-uevent end, and no-udev behavior. Android module ignores arguments and always reports inactive sync.

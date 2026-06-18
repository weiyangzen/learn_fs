# sources/distributed-fs/ceph-client/kernel/power/user.c

## Purpose
Implements the `/dev/snapshot` misc device, the user-space ABI for software suspend/resume. It lets privileged user space freeze tasks, create/read a hibernation image, write/load an image, allocate/free swap pages, request atomic restore, and trigger platform poweroff.

## Important APIs, Types, and Functions
State is held in global `snapshot_state` of `struct snapshot_data`, containing a `snapshot_handle`, swap type, open mode, frozen/ready/platform flags, bitmap ownership, and selected resume device. `need_wait` delays writes/ioctls until device probing completes. `is_hibernate_resume_dev()` reports whether a device matches the active snapshot resume device.

File operations are `snapshot_open()`, `snapshot_release()`, `snapshot_read()`, `snapshot_write()`, `snapshot_ioctl()`, optional `snapshot_compat_ioctl()`, and misc registration `snapshot_device_init()`. `snapshot_set_swap_area()` handles native and compat `SNAPSHOT_SET_SWAP_AREA` payloads.

Supported ioctls include `SNAPSHOT_FREEZE`, `SNAPSHOT_UNFREEZE`, `SNAPSHOT_CREATE_IMAGE`, `SNAPSHOT_ATOMIC_RESTORE`, `SNAPSHOT_FREE`, `SNAPSHOT_PREF_IMAGE_SIZE`, `SNAPSHOT_GET_IMAGE_SIZE`, `SNAPSHOT_AVAIL_SWAP_SIZE`, `SNAPSHOT_ALLOC_SWAP_PAGE`, `SNAPSHOT_FREE_SWAP_PAGES`, `SNAPSHOT_S2RAM`, `SNAPSHOT_PLATFORM_SUPPORT`, `SNAPSHOT_POWER_OFF`, and `SNAPSHOT_SET_SWAP_AREA`.

## Control Flow
`snapshot_open()` rejects unavailable hibernation and read/write mode, serializes with `system_transition_mutex`, acquires the hibernation token, initializes state, calls hibernation or restore notifiers depending on open direction, and creates memory bitmaps for restore writers.

Read mode is image creation: user space calls `SNAPSHOT_FREEZE`, which syncs filesystems, freezes processes, and creates bitmaps; `SNAPSHOT_CREATE_IMAGE`, which calls `hibernation_snapshot()` and returns `in_suspend`; then reads from the device. `snapshot_read()` advances `snapshot_read_next()` on page boundaries and copies the current page to user space.

Write mode is image restore: user space writes pages to the device. `snapshot_write()` advances `snapshot_write_next()` on page boundaries and copies user data into the returned kernel buffer. `SNAPSHOT_ATOMIC_RESTORE` finalizes image loading, verifies the image is complete and tasks are frozen, then calls `hibernation_restore()`.

Swap ioctls let user space identify a swap area, query available swap, allocate individual swap-backed pages with `alloc_swapdev_block()`, and free them. `SNAPSHOT_S2RAM` allows entering suspend-to-RAM after tasks are frozen. `snapshot_release()` frees swsusp pages, swap pages, bitmaps, thaws processes if needed, posts notifiers, releases the hibernation token, and unlocks system sleep.

## State and Persistence Behavior
`snapshot_state` is singleton process-global state; only one opener is allowed through `hibernate_acquire()`. Image data is streamed but not persisted by this file unless user space uses swap allocation ioctls. `data->dev` persists only for the open lifetime to protect the active resume device.

## Dependencies and Integration Points
Depends on miscdevice, snapshot ioctls UAPI, user-copy helpers, freezer, PM notifiers, hibernation/suspend core, swap helpers, memory bitmaps, console/device hotplug serialization through downstream calls, compat syscall support, and CAP_SYS_ADMIN authorization for ioctls.

## Risks
Risks include singleton state corruption if open/release assumptions change, incomplete cleanup when user space exits mid-transition, CAP_SYS_ADMIN ioctl misuse, compat layout mistakes, writing image data out of order, missed `snapshot_write_finalize()`, deadlock around `system_transition_mutex` and device probe waits, and allowing swap pages to be freed while an image is still in use. The ABI is sensitive because external suspend tools may depend on exact ioctl semantics.

## Test Signals
Use user-space suspend tools against `/dev/snapshot` for create/read and write/restore flows; test compat ioctls, partial reads/writes, non-page-aligned offsets, open mode rejection, unprivileged ioctl rejection, freeze/unfreeze cleanup, swap-area setup, swap page allocation/freeing, `SNAPSHOT_S2RAM`, platform support/poweroff flags, and abrupt process termination during each phase.

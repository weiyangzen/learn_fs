# sources/distributed-fs/ceph-client/drivers/base/firmware_loader/sysfs.c

## Purpose
`sysfs.c` implements the firmware class and per-request sysfs device used by fallback downloads and firmware upload registration.

## Important APIs, Types, And Functions
Important APIs are `register_sysfs_loader()`, `unregister_sysfs_loader()`, `__fw_load_abort()`, `fw_create_instance()`, and device attributes `loading` plus binary `data`. With user-helper enabled it exposes class timeout and uevent generation. Internal helpers include `firmware_loading_store()`, `firmware_data_read()`, `firmware_data_write()`, `fw_realloc_pages()`, and paged/direct read-write helpers.

## Control Flow, State, And Persistence
Class registration creates `/sys/class/firmware` and optional fallback sysctls. `fw_create_instance()` initializes a firmware class device named after the firmware and parented to the requester. Userspace writes `1` to `loading` to start/reset, writes firmware bytes to `data`, then writes `0` to map pages, run post-load security checks, mark done, and potentially start a firmware upload worker. Writing `-1` aborts and resets upload state when needed.

## Dependencies, Integration Points, Risks, And Test Signals
Dependencies include sysfs class devices, binary attributes, firmware state, LSM post-load checks, highmem page copy helpers, fallback config, and upload hooks. Risks include holding `fw_lock` around user-visible state, racing writes after done/abort, page growth failure aborting loads, static variable misuse in visibility, and correct reset for upload reuse. Test signals include timeout show/store, uevent variables, loading 1/0/-1 state transitions, permission checks, paged buffer growth/map, preallocated buffer bounds, security rejection, and upload attribute visibility.

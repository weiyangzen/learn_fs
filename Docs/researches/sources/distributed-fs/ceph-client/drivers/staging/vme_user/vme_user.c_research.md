# sources/distributed-fs/ceph-client/drivers/staging/vme_user/vme_user.c

## Purpose
Implements the legacy `/dev/bus/vme/*` character-device access driver on top of the VME framework. It exposes four master devices, four slave devices, and one control device using major 221, allowing user space to configure windows, read/write mapped VME master space, access slave backing buffers, mmap master windows, and generate VME interrupts.

## Important APIs, Types, and Functions
Important state is `struct image_desc image[VME_DEVS]`, holding per-minor buffers, DMA addresses, mutexes, sysfs device pointers, VME resources, and mmap counts. File operations are `vme_user_read()`, `vme_user_write()`, `vme_user_llseek()`, `vme_user_unlocked_ioctl()`, and `vme_user_mmap_prepare()`. IOCTL helpers handle `VME_GET/SET_MASTER`, `VME_GET/SET_SLAVE`, and `VME_IRQ_GEN`. Driver lifecycle is `vme_user_match()`, `vme_user_probe()`, `vme_user_remove()`, `vme_user_init()`, and `vme_user_exit()`.

## Control Flow
Module load requires a `bus=` parameter and registers a VME driver for `VME_MAX_SLOTS`; matching admits the configured bus/slot only. Probe registers the fixed char region, adds a cdev, requests four slave resources and coherent 128 KiB buffers, requests four A32/SCT/D32 master resources and bounce buffers, registers a class, and creates device nodes. Reads/writes lock the image, clamp by current VME window size, then either delegate to VME master read/write through a bounce buffer or copy from/to the slave backing buffer. Master mmap delegates to `vme_master_mmap_prepare()` and tracks active mappings via VMA private refcounts.

## State and Persistence Behavior
State is global and supports only one probed VME user device at a time (`vme_user_bridge`). Master/slave image state persists from probe until remove. `mmap_count` blocks master window reconfiguration while mappings exist. Slave buffers are coherent allocations and are used as inbound VME storage.

## Dependencies and Integration Points
Depends on the VME framework, char devices, class/device sysfs, uaccess, mmap_prepare VMA hooks, and fixed device numbers documented for VME. It consumes ABI structs from `vme_user.h`.

## Risks and Test Signals
Probe error unwinds assume resources/buffers were initialized for every index in some paths; partial failures need careful testing. `vme_user_bridge` is not reset in remove. Reads/writes use `image_size - 1`, so a zero-size window can underflow. The ABI passes raw framework address/cycle/width flags to user space despite comments questioning this. Test signals include device-node creation, IOCTL get/set round trips, reconfiguration blocked during mmap, offset clamping, slave buffer DMA visibility, cleanup after partial probe failure, and unload/reload behavior.

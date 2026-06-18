# sources/distributed-fs/ceph-client/drivers/w1/w1_int.c

## Purpose
Internal master-device lifecycle implementation. It validates bus master callbacks, allocates `struct w1_master`, registers master devices, starts/stops search kthreads, and removes masters.

## Important APIs, Types, and Functions
Module parameters are `search_count` and `enable_pullup`. `w1_alloc_dev()` allocates a master plus embedded bus-master copy and initializes locks/lists/defaults. Exported APIs are `w1_add_master_device()` and `w1_remove_master_device()`. `__w1_remove_master_device()` performs full teardown.

## Control Flow
Adding a master validates that the supplied callbacks support either touch/reset, bit read/write, or byte read/write/reset. Under global master lock it allocates an ID, registers the device, creates master attributes, copies callbacks, starts `w1_process()` kthread, adds the master to the global list, and sends a netlink add message. Removal finds the master by `bus_master->data`, removes it from the list, stops the thread, detaches all slaves, removes attributes, waits for refcounts while processing callbacks, sends netlink remove, and unregisters the device.

## State and Persistence
State is in the allocated master object: IDs, counts, flags, lists, locks, copied bus-master callbacks, and kthread. No persistent storage.

## Dependencies and Integration Points
Depends on the main core globals from `w1.c`, `w1_internal.h`, netlink, Linux device model, kthreads, and callbacks supplied by master drivers such as GPIO and UART.

## Risks and Test Signals
`w1_remove_master_device()` iterates `w1_masters` without taking `w1_mlock`, which is a concurrency point to audit. Callback validation must reject incomplete masters. Test invalid callback sets, add/remove under active searches, slave detach during removal, refcount waits, netlink master events, and pullup defaults propagated to new masters.

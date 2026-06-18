<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dibs.h -->
# sources/distributed-fs/ceph-client/include/linux/dibs.h

## Purpose
Defines the Direct Internal Buffer Sharing abstraction, where clients exchange data through Direct Memory Buffers owned by local DIBS devices and writable by authorized remote DIBS devices on the same fabric.

## Important APIs, Types, And Functions
Core data structures are `struct dibs_dmb`, `struct dibs_event`, `struct dibs_client_ops`, `struct dibs_client`, `struct dibs_dev_ops`, and `struct dibs_dev`. Client entry points are `dibs_register_client()` and `dibs_unregister_client()`. Device-driver entry points are `dibs_dev_alloc()`, `dibs_dev_add()`, and `dibs_dev_del()`. Per-client device storage is accessed with `dibs_set_priv()` and `dibs_get_priv()`.

## Control Flow
DIBS clients register callbacks and are notified of existing and future devices via `add_dev()`. A client queries fabric reachability, registers a DMB for a remote GID, receives IRQ/event callbacks, and unregisters the DMB during teardown. Sending uses `move_data()` to write synchronously into a remote DMB and optionally signal a bit in the target mask. Optional flows support VLAN membership, software events, and memory-mapped remote DMB attach/detach.

## State And Persistence
Runtime state includes device GIDs, fabric ids, per-client subscriptions, DMB indices, DMB tokens, allocated CPU buffers, optional DMA addresses, and per-client private pointers. `struct dibs_dev` protects client/DMB arrays with a spinlock. There is no filesystem persistence; tokens and GIDs are stable only within the fabric lifetime described by the driver.

## Dependencies And Integration Points
Depends on `struct device`, UUIDs, DMA addresses, lists, spinlocks, and fabric-specific DIBS device drivers. Consumers integrate through the DIBS layer rather than calling hardware drivers directly.

## Risks And Edge Cases
The contract depends on strong access control by the fabric: each DMB has one owner and one authorized remote writer. IRQ callbacks run in IRQ context, so clients must not sleep. `add_dev()`/`del_dev()` ordering controls device usability, and clients must stop using a device after `del_dev()`. Optional mmap-style DMB support requires all three related ops to be present or absent. Deprecated VLAN fields must not be treated as security-critical on devices that ignore VLANs.

## Test Signals
Tests should cover client register/unregister with preexisting devices, device add/delete notifications, DMB register/unregister, token uniqueness, loopback fabric behavior, move-data bounds and zero-length writes, IRQ/event coalescing, per-client private storage, optional attach/detach support, and concurrent device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dibs.h -->

# sources/distributed-fs/ceph-client/drivers/scsi/fcoe/fcoe_sysfs.c

## Purpose

`fcoe_sysfs.c` implements the `fcoe` bus and sysfs object model for FCoE controllers and discovered FCFs. It exposes controller mode, enabled state, VLAN responder flag, FC timeouts, FCF dev-loss timeout, LESB counters, and FCF identity/state/selection/VLAN attributes.

## Important APIs, types, and functions

Exported functions are `fcoe_sysfs_setup()`, `fcoe_sysfs_teardown()`, `fcoe_ctlr_device_add()`, `fcoe_ctlr_device_delete()`, `fcoe_fcf_device_add()`, and `fcoe_fcf_device_delete()`. Store paths include `store_ctlr_mode()`, `store_ctlr_enabled()`, `store_ctlr_fip_resp()`, timeout stores, controller FCF dev-loss timeout propagation, and per-FCF dev-loss timeout update. Work helpers handle final FCF unregister and delayed dev-loss deletion.

## Control flow

Controller add allocates a controller object plus private tail memory, assigns an ID, initializes list/lock/defaults, creates ordered workqueues, and registers `ctlr_N` on the `fcoe` bus. Controller sysfs writes validate state and call LLD callbacks for mode and enabled changes. FCF add reconnects a matching disconnected device or registers a new `fcf_N` child. FCF delete marks it disconnected, clears private data, and queues delayed dev-loss work; reconnect cancels the delay, timeout removes the device.

## State and persistence behavior

Atomic counters generate IDs for the module lifetime. Controller objects own FCF lists, locks, workqueues, enabled/mode values, default dev-loss timeout, and LESB storage. FCF devices track connection state, identity fields, selected/VLAN values, dev-loss work, and LLD private pointers. State is runtime-only.

## Dependencies and integration points

The file depends on `<scsi/fcoe_sysfs.h>`, `<scsi/libfcoe.h>`, local libfcoe logging, and callbacks supplied by `struct fcoe_sysfs_function_template`. Bus create/destroy attributes delegate to `fcoe_transport.c`.

## Risks and edge cases

`store_ctlr_enabled()` changes the visible state before invoking the LLD callback and does not restore it on failure. Workqueue teardown ordering is critical. FCF add/delete callers must hold `ctlr->lock` as documented. Sysfs show callbacks may invoke LLD getters while FCF/controller deletion is active.

## Test signals

Test bus registration, controller add/delete, mode/enable/timeout parsing and rejection while enabled, FCF add/reconnect/delete/dev-loss expiry, selected/VLAN getter callbacks, LESB reads, failed LLD enable callback behavior, and sysfs stress during deletion under lockdep.

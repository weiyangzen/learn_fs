# sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/bus.c

## Purpose

This source implements the optional Surface Aggregator bus and client-device model. It lets non-enumerable SSAM devices be represented as kernel devices with SSAM UIDs, matched to SSAM device drivers, populated from firmware nodes, and removed before controller shutdown.

## Important APIs, Types, And Functions

Important exports include `ssam_device_type`, `ssam_device_alloc()`, `ssam_device_add()`, `ssam_device_remove()`, `ssam_device_id_match()`, `ssam_device_get_match()`, `ssam_device_get_match_data()`, `__ssam_device_driver_register()`, `ssam_device_driver_unregister()`, `__ssam_register_clients()`, and `ssam_remove_clients()`. Internal helpers implement modalias sysfs/uevent generation, UID parsing from `ssam:dd:cc:tt:ii:ff` firmware-node names, device matching by `SSAM_MATCH_TARGET`, `INSTANCE`, and `FUNCTION`, and bus register/unregister.

## Control Flow

The core registers the bus during aggregator init. Client providers allocate an `ssam_device`, attach the controller and optional firmware node, and call `ssam_device_add()`. Addition takes the controller state read lock and rejects devices unless the controller is `SSAM_CONTROLLER_STARTED`. Driver registration sets the bus and prefers asynchronous probing so SSAM I/O can occur during probe. Firmware-child registration scans each child node, ignores non-SSAM nodes, and rolls back already added clients on error.

## State And Persistence

Runtime state is represented by registered `struct device` objects, controller references held by devices, firmware-node references, and driver bindings. The bus stores no persistent registry of its own. Device existence lasts until explicit `ssam_device_remove()` or parent child-removal during controller teardown.

## Dependencies And Integration Points

The file depends on Linux driver core, device properties/fwnodes/OF, Surface Aggregator controller and device public headers, and local controller locking. It integrates with client registry/hub drivers and with `core.c` teardown through `ssam_remove_clients()`.

## Risks

Lifetime correctness depends on controller parentage or explicit removal before shutdown. `ssam_remove_clients()` only removes direct children. UID parsing depends on firmware node names with the `ssam:` prefix and exactly five hex bytes. Match tables must end in a zero entry. Async probe means client drivers must correctly handle request failures and ordering. `ssam_device_add()` protects state during `device_add()`, but callers that change parentage must ensure suspend/remove ordering themselves.

## Test Signals

Signals include bus registration, modalias strings and uevents, module autoload from SSAM IDs, client device creation from firmware nodes, match-data retrieval, async probe of client drivers that issue SSAM requests, rollback on child-add failure, and reverse-order removal before controller shutdown.

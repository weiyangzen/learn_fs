<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/auxiliary.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/auxiliary.rs

## Purpose
This file implements Rust abstractions for Linux auxiliary bus drivers and auxiliary device registration.

## Important APIs, Types, and Functions
`Adapter<T: Driver>` bridges Rust driver implementations to `driver::RegistrationOps` and `DriverLayout`. `module_auxiliary_driver!` declares a module exposing one auxiliary driver. `DeviceId` wraps `bindings::auxiliary_device_id`, builds `modname.name` IDs, and implements raw ID-table traits. `auxiliary_device_table!` creates a typed `IdArray` plus module alias. The `Driver` trait defines `IdInfo`, `ID_TABLE`, `probe`, and optional `unbind`. `Device<Ctx>` wraps `struct auxiliary_device`, exposes `id` and `parent`, implements bus-device and refcount traits, and is `Send`/`Sync`. `Registration` owns a registered auxiliary device and exposes `Registration::new` as a `Devres<Self>` initializer.

## Control Flow and State
Driver registration initializes `struct auxiliary_driver` fields (`name`, `probe`, `remove`, and `id_table`) before calling `__auxiliary_driver_register`; unregister delegates to `auxiliary_driver_unregister`. Probe casts the C device and matched ID into Rust wrappers, looks up ID info by `driver_data` index, invokes `T::probe`, and stores pinned driver data in device drvdata. Remove borrows that data and calls `T::unbind`. Device registration allocates a zeroed auxiliary device, fills parent/name/id/release, calls `auxiliary_device_init`, leaks the allocation to C lifetime management, calls `__auxiliary_device_add`, and rolls back with `auxiliary_device_uninit` on add failure.

## State and Persistence Behavior
Registered devices persist until `Registration::drop`, which calls `auxiliary_device_delete` and `auxiliary_device_uninit`. The leaked `KBox` is reclaimed in the device release callback when the final device reference drops. Driver private data is persisted in drvdata after successful probe and remains available for remove/unbind.

## Dependencies and Integration Points
The module integrates with kernel driver registration, device IDs, `Devres`, `device::Device`, `AlwaysRefCounted`, `KBox`, `PinInit`, and C auxiliary bus bindings. Parent device lifetime is tied to devres when `Registration::new` returns `Devres<Self>`.

## Risks
Safety depends on correct transparent casts between C and Rust wrappers, exact field offsets, and correct C callback sequencing. `DeviceId::new` copies C strings into a fixed-size C array without explicit runtime length checks, so callers must respect kernel ID size assumptions. Remove assumes probe succeeded and drvdata was set. Device memory is intentionally leaked until release; missing release or mismatched init/uninit would leak or double-free.

## Test Signals
No local KUnit tests are present. Test signals are compile-time type checking, macro expansion for driver/device tables, and runtime probe/remove behavior through auxiliary bus users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/auxiliary.rs -->

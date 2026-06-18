# sources/distributed-fs/ceph-client/rust/kernel/i2c.rs

## Purpose
`i2c.rs` implements Rust abstractions for I2C drivers, device IDs, adapters, clients, board info, and manual client registration. It connects Rust driver traits to the C I2C driver model.

## Important APIs, Types, and Functions
`DeviceId` wraps `i2c_device_id` and implements raw ID traits. `i2c_device_table!` emits an ID array and module alias. `Adapter<T>` implements `driver::DriverLayout`, `RegistrationOps`, and `driver::Adapter` for any Rust `Driver`. `module_i2c_driver!` declares a module driver. The `Driver` trait defines ID tables, `probe`, optional `shutdown`, and optional `unbind`. `I2cAdapter`, `I2cBoardInfo`, `I2cClient`, and `Registration` wrap C adapter, board-info, client, and manually registered client lifetimes.

## Control Flow
Driver registration statically requires at least one ACPI, OF, or legacy I2C ID table, fills `struct i2c_driver` callbacks and match tables, then calls `i2c_register_driver`. Probe casts the C client to `I2cClient<CoreInternal>`, obtains ID info from I2C or generic ACPI/OF matching, calls `T::probe`, and stores pinned driver data as device drvdata. Remove and shutdown borrow that drvdata and dispatch to `T::unbind` or `T::shutdown`. Manual client registration uses `i2c_new_client_device`, converts error pointers and null, and unregisters in `Drop`.

## State and Persistence
Registered drivers persist until unregistered by the driver core. Per-client Rust driver state is pinned in drvdata after successful probe. `I2cAdapter` and `I2cClient` are reference-counted through C device/I2C references. `Registration` owns one created client device and unregisters it on drop.

## Dependencies and Integration Points
This file integrates with the generic Rust driver framework, device context system, ACPI and OF ID tables, `module_device_table!`, `Devres`, `ARef`, device drvdata storage, and C I2C core APIs including `i2c_register_driver`, `i2c_match_id`, `i2c_get_adapter`, `i2c_verify_client`, and `i2c_new_client_device`.

## Risks
Callback casts rely on I2C core passing valid `struct i2c_client` pointers. Drvdata borrow in remove/shutdown assumes probe completed and stored the expected type. Compile-time ID string limits are 20 bytes including NUL. `I2cAdapter::get` must balance references through `AlwaysRefCounted`. Manual registration must handle both error pointers and null returns.

## Test Signals
Test driver registration with each ID table type, missing-table compile failure, probe/remove/shutdown callback order, ID info lookup priority, adapter get/put lifecycle, `Device` to `I2cClient` conversion success/failure, manual client devres cleanup, and ID string length assertions.

# sources/distributed-fs/ceph-client/rust/kernel/acpi.rs

## Purpose
Defines Rust ACPI device-id table support used by Rust drivers to advertise ACPI match data.

## APIs, Types, and Functions
`IdTable<T>` aliases a static dynamic `device_id::IdTable<DeviceId, T>`. `DeviceId` wraps `bindings::acpi_device_id` and implements `RawDeviceId` and `RawDeviceIdIndex`. Constructors include `DeviceId::new(id, info)` and `DeviceId::new_with_data(id, data)`. The exported `acpi_device_table!` macro emits a static ACPI id table with optional match data.

## Control Flow, State, and Persistence
There is no runtime mutable state in this file. Match tables are static data emitted into the driver/module image; driver core consumes them during ACPI device matching. Raw index access returns the integer driver-data field from the generated C-compatible table entry.

## Dependencies and Integration
Depends on generated ACPI bindings, `kernel::device_id` traits, and Rust macro support. It integrates with Rust driver declarations and Linux ACPI match-table conventions.

## Risks and Test Signals
Risks include ACPI id string length/termination constraints, incorrect `driver_data` casting, table lifetime assumptions, and mismatch between Rust type data and C `kernel_ulong_t`. Test signals are Rust ACPI driver registration tests, compile-time table generation, and matching devices with and without associated data.

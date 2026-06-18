# sources/distributed-fs/ceph-client/rust/kernel/driver.rs

## Purpose
`driver.rs` is the bus-independent driver registration and adapter framework for Rust kernel drivers. It documents how bus-specific driver traits should be shaped and provides common registration, post-unbind cleanup, module macro support, and OF/ACPI ID matching helpers.

## Important APIs, Types, and Functions
Unsafe `DriverLayout` describes a C driver structure embedding `struct device_driver` and its Rust private data type. Unsafe `RegistrationOps` supplies bus-specific `register` and `unregister`. `Registration<T>` owns a pinned C driver structure. `module_driver!` builds a one-driver module. `Adapter` supplies `IdInfo`, `acpi_id_table`, `of_id_table`, `acpi_id_info`, `of_id_info`, and `id_info`.

## Control Flow
`Registration::new` zero/default-initializes the bus driver structure, attaches a generic `post_unbind_rust` callback to the embedded `struct device_driver`, and calls the bus-specific registration function. On unregistration, `PinnedDrop` calls the matching unregister function. After a device is unbound and remove/devres callbacks are complete, `post_unbind_callback` obtains and drops the Rust driver private data from the device. Adapter ID lookup first checks ACPI, then OF.

## State and Persistence
State is the registered C driver structure plus any driver-private data stored on bound devices through `device.rs`. Registration persists until the Rust `Registration` is dropped. There is no durable storage.

## Dependencies and Integration Points
The module depends on ACPI, OF, `device`, `device_id`, `Opaque`, and `ThisModule`. Bus-specific wrappers such as platform, PCI, and auxiliary implement `RegistrationOps` and their own driver traits on top of this infrastructure.

## Risks
The unsafe layout contracts are central: wrong `DEVICE_DRIVER_OFFSET`, wrong `DriverData`, or non-`repr(C)` driver layouts can corrupt memory. Post-unbind cleanup assumes bus code stored driver data using the generic device helper. Registration/unregistration ordering must be exact; unregister is only valid after successful register.

## Test Signals
Build a minimal bus driver using `module_driver!`, validate successful and failing registration paths, bind/unbind repeatedly and confirm private data drops after devres cleanup, test ACPI/OF table matching and no-match behavior, and run KASAN/refcount checks.

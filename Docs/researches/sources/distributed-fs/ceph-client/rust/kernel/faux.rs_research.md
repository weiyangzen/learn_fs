# sources/distributed-fs/ceph-client/rust/kernel/faux.rs

## Purpose
`faux.rs` provides a Rust RAII wrapper for Linux faux devices, useful for kernel modules that need a device-core object without a physical bus device.

## Important APIs, Types, and Functions
`Registration` owns a non-null `struct faux_device`. `Registration::new(name, parent)` calls `faux_device_create`, optionally parenting the device under a `device::Device`. `AsRef<device::Device>` exposes the embedded `dev` field. `Drop` calls `faux_device_destroy`. `Send` and `Sync` are implemented because the device core handles synchronization and the Rust type prevents duplicate destruction.

## Control Flow
Creation passes a copied C string name, optional parent raw pointer, and null ops pointer to the C API. A null return maps to `ENODEV`; otherwise the pointer is stored as the type invariant. Use sites borrow the embedded `struct device` through `AsRef`. Drop unconditionally unregisters/destroys the faux device once.

## State and Persistence
The only durable state is the registered kernel device object. Its lifetime is exactly tied to the `Registration` value. Parent device references are handled by the C device core during registration.

## Dependencies and Integration Points
The file depends on `include/linux/device/faux.h`, `crate::device`, `CStr`, `NonNull`, and standard Rust drop semantics. It is an integration helper for drivers or tests that need a device for devres, firmware, sysfs, or other device-scoped APIs.

## Risks
The wrapper assumes `faux_device_create` returns only valid devices or null and that `faux_device_destroy` is the correct inverse. Exposing the device reference is safe only while `Registration` is alive. No custom faux operations are supported because ops are always null.

## Test Signals
Test creation with and without a parent, null/failure path propagation as `ENODEV`, use of `as_ref()` with device-scoped APIs, and drop/unregister ordering under normal module teardown.

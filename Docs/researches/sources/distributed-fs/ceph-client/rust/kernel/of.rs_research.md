# sources/distributed-fs/ceph-client/rust/kernel/of.rs

## Purpose
Provides Rust wrappers for Open Firmware / Device Tree match identifiers and a macro for exporting OF device-id tables to the kernel module infrastructure.

## APIs, Types, and Functions
`DeviceId` is a transparent wrapper over `bindings::of_device_id`. `DeviceId::new` builds a const-compatible ID from a static compatible string by zero-initializing the C struct and copying bytes into `compatible`. `IdTable<T>` aliases the shared `device_id::IdTable` abstraction. `of_device_table!` builds an `IdArray` and emits `MODULE_DEVICE_TABLE(of, ...)` metadata through `module_device_table!`.

## Control Flow, State, and Persistence
There is no dynamic control flow beyond const construction. Match table entries persist as static data in the module image. `RawDeviceIdIndex::index` reads the C `data` field and treats it as an index into the Rust sidecar info table.

## Dependencies and Integration
Depends on generated `bindings::of_device_id`, `device_id::{RawDeviceId, RawDeviceIdIndex}`, `CStr`, and module alias generation. It is consumed by platform drivers through `platform::Driver::OF_ID_TABLE`.

## Risks and Test Signals
Risks include overlong compatible strings overflowing the fixed C array at compile time, incorrect `data` offset breaking sidecar info lookup, and modpost alias regressions if the macro layout changes. Test signals include compile tests for generated OF tables, modinfo alias inspection, and platform probe tests that verify matched `IdInfo` is delivered.

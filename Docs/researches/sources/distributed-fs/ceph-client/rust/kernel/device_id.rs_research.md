# sources/distributed-fs/ceph-client/rust/kernel/device_id.rs

## Purpose
`device_id.rs` provides generic Rust infrastructure for bus-specific device ID tables. It builds zero-terminated C-compatible ID arrays and keeps Rust driver metadata aligned with each raw ID entry.

## Important APIs, Types, and Functions
`RawDeviceId` marks Rust ID wrappers as layout-compatible with a C raw ID type. `RawDeviceIdIndex` adds a `DRIVER_DATA_OFFSET` and `index()` contract for ID types that store table indexes in a raw `driver_data` field. `RawIdArray<T, N>` stores raw IDs plus a zeroed sentinel. `IdArray<T, U, N>` stores raw IDs and parallel `id_infos`. `IdTable<T, U>` type-erases the const length. `module_device_table!` emits a modpost-visible device table alias.

## Control Flow
`IdArray::build` runs in const context, transmute-copies each Rust ID into the raw ID array, optionally writes the table index into the raw driver's data field, moves the associated info into the parallel array, and appends a zero sentinel. Bus adapters pass `raw_ids().as_ptr()` to kernel match helpers and use the index to recover `id_infos`.

## State and Persistence
ID arrays are static data compiled into the driver module. They are not mutated after construction except for const-time initialization. The generated module device table static is also build-time metadata for module alias generation.

## Dependencies and Integration Points
This module is consumed by ACPI, OF, PCI, platform, auxiliary, and other bus abstractions that need C-compatible match tables while preserving Rust-side `IdInfo`. It integrates with `driver::Adapter` lookup helpers.

## Risks
Safety depends on exact layout compatibility between Rust ID wrappers and C ID structs, and on correct byte offsets for `driver_data`. An incorrect offset corrupts raw IDs at compile time and can make match callbacks return the wrong metadata. The `as_ptr` provenance trick must keep the sentinel addressable for C scans.

## Test Signals
Build tests should inspect generated table size, sentinel zeroing, index storage, and modpost aliases. Runtime bus-match tests should confirm matched IDs recover the correct `IdInfo`, including multi-entry tables and no-match behavior.

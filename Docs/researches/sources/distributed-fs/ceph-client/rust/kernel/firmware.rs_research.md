# sources/distributed-fs/ceph-client/rust/kernel/firmware.rs

## Purpose
`firmware.rs` wraps Linux firmware loading and module firmware metadata generation. It gives Rust drivers RAII access to requested firmware blobs and a const builder for `.modinfo` firmware entries.

## Important APIs, Types, and Functions
`FwFunc` stores one of the firmware request function pointers. `Firmware` owns a `struct firmware` pointer and provides `request`, `request_nowarn`, `size`, and `data`. `Drop` releases firmware. The exported `module_firmware!` macro emits a used static byte array in `.modinfo`. `ModInfoBuilder<N>` provides const `new`, `new_entry`, `push`, `build`, and `build_length`.

## Control Flow
`Firmware::request_internal` initializes a null firmware pointer, calls the selected C request function with the device and name, converts nonzero returns to `Error`, and stores a non-null pointer on success. Data access builds a byte slice from `firmware::data` and `firmware::size`. The metadata macro runs the builder twice: once with `N=0` to compute length and once with the computed length to build the final byte array.

## State and Persistence
Loaded firmware is kernel-managed memory held until `Firmware` drops. The byte slice is immutable for the wrapper lifetime. `.modinfo` entries are compile-time static metadata, not runtime mutable state.

## Dependencies and Integration Points
The runtime API depends on `request_firmware`, `firmware_request_nowarn`, and `release_firmware`, plus `Device` and `CStr`. The macro integrates with module metadata, `LocalModule`, `ModuleMetadata`, link sections, and compile-time string building. Drivers may use the macro when firmware names depend on module name or generated lists.

## Risks
The wrapper trusts successful C firmware requests to return a valid non-null pointer. `data()` assumes the firmware backing buffer remains valid and immutable until release. The builder has strict sequencing: `new_entry()` must precede `push()` for nonzero buffers, and `build_length()` and `build()` must agree exactly or trigger compile-time errors.

## Test Signals
Exercise successful and missing firmware requests, optional firmware no-warn behavior, zero-length and nonzero blobs, drop releasing firmware once, and compile-time `.modinfo` generation for single and multiple entries, including built-in versus loadable module prefixes.

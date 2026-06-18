# sources/distributed-fs/ceph-client/samples/rust/rust_debugfs.rs

## Purpose

This Rust platform driver sample demonstrates debugfs file creation for scalar, structured, and binary state attached to a firmware-described platform device.

## Important APIs, Types, and Functions

It uses `kernel::module_platform_driver!`, ACPI matching, `debugfs::Dir`, typed `debugfs::File`, `Atomic<usize>`, `Mutex<Inner>`, `CString`, `KVec`, and firmware node property access. `Inner` implements `FromStr` so debugfs can parse writes to the pair file.

## Control Flow

The ACPI table matches `LNUXBEEF`. Probe calls `RustDebugFs::new()`, which creates `sample_debugfs`, reads the device `compatible` property into a read-only file, and creates read/write files for `counter`, `pair`, `array_blob`, and `vector_blob`. A `pin_chain` post-initialization step sets counter to 91 and mutates the `Inner` pair.

## State and Persistence Behavior

State is held in the driver instance: an `ARef` to the platform device, the debugfs directory RAII object, file handles, an atomic counter, mutex-protected pair, fixed array blob, and vector blob. Debugfs entries are removed when the instance is dropped.

## Dependencies and Integration Points

It depends on `DEBUG_FS`, platform bus, ACPI firmware nodes, and Rust debugfs wrappers. User space uses debugfs files to inspect and modify state.

## Risks and Edge Cases

Probe requires a firmware node and `compatible` property; missing properties fail via `required_by(dev)`. `Inner::from_str` rejects malformed or extra tokens. Debugfs is for diagnostics and should not be treated as stable ABI.

## Test Signals

Boot with a matching ACPI SSDT, load the module, inspect debugfs files, write valid and invalid `pair` values, and verify counter/blob read/write behavior.

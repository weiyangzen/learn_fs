# sources/distributed-fs/ceph-client/rust/kernel/pci/id.rs

## Purpose
Centralizes typed PCI class-code and vendor-ID wrappers plus generated constants and formatting for use by PCI match tables and device logging.

## APIs, Types, and Functions
`Class` stores a 24-bit class code, with `from_raw`, `as_raw`, `Debug`, and generated `Display` names. `ClassMask` supports full 24-bit or class/subclass matching and implements `TryFrom<u32>`. `Vendor` stores a 16-bit vendor ID, exposes `from_raw` and `as_raw`, and has generated constants plus `Debug`/`Display`.

## Control Flow, State, and Persistence
The file is mostly static constant generation through macros. `Class::to_24bit_class` normalizes 16-bit class constants by shifting them into the upper 16 bits while leaving full 24-bit constants unchanged. Formatting matches known constants by value and falls back to hex debug output. There is no runtime state.

## Dependencies and Integration
Depends on generated PCI class/vendor bindings and kernel formatting/error aliases. It is re-exported by `pci.rs` and used by `DeviceId` constructors and `Device::pci_class`/`vendor_id`.

## Risks and Test Signals
Risks include stale generated constants relative to C headers, ambiguous display names for duplicate numeric constants, incorrect 16-bit-to-24-bit normalization, and incomplete class-mask support. Test signals include compile-time constant equality checks against bindings, formatting tests for known and unknown IDs, `ClassMask::try_from` boundary tests, and generated table smoke tests using class/vendor match constructors.

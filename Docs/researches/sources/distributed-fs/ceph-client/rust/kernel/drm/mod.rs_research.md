# sources/distributed-fs/ceph-client/rust/kernel/drm/mod.rs

## Purpose
`drm/mod.rs` is the public module facade for Rust DRM abstractions. It organizes the DRM device, driver, file, GEM, and ioctl submodules and re-exports the primary types used by drivers.

## Important APIs, Types, and Functions
The module declares `device`, `driver`, `file`, `gem`, and `ioctl`. It re-exports `Device`, `Driver`, `DriverInfo`, `Registration`, and `File`. The private `Sealed` trait prevents external implementations of internal DRM extension traits.

## Control Flow
This file has no runtime control flow. Its compile-time role is to expose the expected public API surface and keep internal sealing available to submodules.

## State and Persistence
The module owns no state. State lives in the device, registration, file, and GEM object modules.

## Dependencies and Integration Points
It is the import point for Rust DRM drivers and for other kernel modules that need DRM types. Submodules use `drm::private::Sealed` to restrict traits such as GEM object conversion and allocation implementations to crate-controlled types.

## Risks
Risks are API-organization issues rather than runtime bugs. Re-exporting a type makes it part of the intended public Rust kernel API surface, while sealing controls which traits downstream drivers can implement. Feature gating for submodules such as shmem must remain consistent with their internal `cfg` use.

## Test Signals
Build drivers importing only `kernel::drm::*`, verify rustdoc links and cfg-gated modules, ensure sealed traits cannot be implemented externally, and compile with DRM and DRM shmem helper configurations enabled and disabled.

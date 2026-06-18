# sources/control-plane/mayastor/io-engine/src/lvm/error.rs

## Purpose
This file defines the LVM backend error taxonomy and maps errors to errno values used by higher io-engine APIs.

## Important APIs, types, and functions
`Error` is a `snafu` enum covering command/report failures, VG/LV lookup and validation errors, unsupported features, reactor bridge failures, SPDK bdev import/export/share failures, metadata/tag update failures, and operation-specific states like `NoSpace`, `Exists`, `SnapshotNotSup`, and `GrowNotSup`. `fail<T>` supports `snafu::ensure!` style returns. `impl ToErrno` maps each variant to a stable `nix::errno::Errno`.

## Control flow
Errors are created by LVM command wrappers, pool/replica logic, and bdev integration paths. Conversion into pool/backend errors happens in `lvm/mod.rs` through `Into` implementations outside this file.

## State and persistence behavior
No runtime state is stored. The persistent behavioral contract is the user-facing display text and errno mapping.

## Dependencies and integration points
It depends on `snafu`, `nix`, `crate::core::ToErrno`, `crate::bdev_api::BdevError`, and `crate::core::CoreError`. It integrates with gRPC and backend error conversion paths that turn storage failures into API status/error codes.

## Risks and test signals
Errno mapping directly affects API behavior; changing it can break control-plane retries or user-visible semantics. Some command failures are mapped broadly to `EIO`, while higher layers recover specific cases by matching stderr strings. Tests should assert mappings for not found, exists, no space, unsupported features, and bdev errors.

# sources/control-plane/mayastor/io-engine/src/lvs/lvs_error.rs

## Purpose
This file defines the error model for the SPDK logical volume store backend and maps SPDK/blobstore/core failures to errno values.

## Important APIs, types, and functions
`ImportErrorReason` adds import context such as not found/corrupt metadata, I/O inspection failure, name mismatch, name clash, and uuid mismatch. `BsError` normalizes low-level blobstore errno values into named errors such as invalid argument, lvol not found, already exists, busy, cannot import, no space, out of metadata, capacity overflow, crypto vbdev failure, and LVS removing. It provides `from_errno`, `from_i32`, and `ToErrno`.

`LvsError` covers pool import/create/export/destroy/grow, invalid bdev/input, replica create/destroy/resize, share/unshare/property errors, snapshot/clone errors, wipe failures, resource locking, metadata expansion parse errors, bdev rescan/grow failures, and crypto resize lag. `impl ToErrno` maps all high-level variants to API errno semantics.

## Control flow
SPDK callbacks and FFI return codes are converted into `BsError`, then wrapped into operation-specific `LvsError` variants at call sites. Higher layers use `ToErrno` for gRPC/API error mapping.

## State and persistence behavior
The file stores no mutable state. Its display strings and errno mappings are persistent API behavior. Import reason text is appended to import errors for diagnostics.

## Dependencies and integration points
It depends on `snafu`, `nix::errno`, `BdevError`, `CoreError`, `ToErrno`, and `PropName`. It is used throughout `lvs_store`, `lvs_lvol`, and `lvol_snapshot`.

## Risks and test signals
Correct errno mapping is critical for control-plane retry and idempotency behavior. `BsError::from_i32` accepts both positive and negative values and warns for negative input, reducing but not eliminating callback convention mistakes. Import with `InvalidArgument` is remapped by reason, so adding reasons requires mapping updates. Tests should cover every important errno conversion, especially import reasons, no space, exists, busy, unsupported grow, and crypto resize failures.

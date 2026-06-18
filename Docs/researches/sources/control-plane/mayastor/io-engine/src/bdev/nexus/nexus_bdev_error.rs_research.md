<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_bdev_error.rs -->
# sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_bdev_error.rs

Purpose: centralizes nexus operation errors and maps them to gRPC `tonic::Status` and Unix errno values. It gives higher layers stable failure categories for create, share, child, rebuild, snapshot, resize, and persistence operations.

Important APIs/types/functions: `Error` with SNAFU contexts under `nexus_err`, `impl From<NvmfError> for Error`, `impl From<Error> for tonic::Status`, and `impl ToErrno for Error`.

Control flow: nexus and child modules construct typed variants with contextual fields. Conversion to `tonic::Status` first computes errno, then selects a gRPC status class such as `invalid_argument`, `failed_precondition`, `not_found`, `already_exists`, `out_of_range`, `data_loss`, or `internal`, and stores errno in response metadata. `ToErrno` delegates to nested `CoreError`, `BdevError`, `ChildError`, or direct `Errno` where available, and uses fixed errno for semantic nexus failures.

State and persistence: this file has no mutable state or persistence, but it influences persistent workflows by classifying `SaveStateFailed` as `data_loss` and `ENODATA`, and by deciding whether retrying callers see precondition, not-found, or internal failures.

Dependencies/integration: depends on `ChildError`, `NbdError`, `BdevError`, `CoreError`, `RebuildError`, `StoreError`, `NvmfError`, SNAFU, tonic, and Mayastor's `ToErrno`/`VerboseError`. All nexus RPC surfaces use these conversions directly or indirectly.

Risks: mappings are policy, so incorrect status classes can change control-plane retry behavior. Some errors with potentially recoverable causes map to `internal`, while `CreateRebuild` maps to `already_exists` regardless of underlying rebuild error. `FailedCreateSnapshot` maps to `internal` even for user/topology validation failures. The errno metadata insertion assumes conversion to metadata value from `i32` remains accepted.

Test signals: unit-test each major variant's gRPC code and errno, nested errno propagation for share/open/close/update errors, metadata presence, snapshot validation mapping, reservation and geometry invalid-argument cases, and backwards compatibility for clients expecting specific status codes.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_bdev_error.rs -->

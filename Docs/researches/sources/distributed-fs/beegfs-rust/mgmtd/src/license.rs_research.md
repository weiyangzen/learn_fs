<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/license.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/license.rs

Purpose: wraps the external BeeGFS license verification shared library and exposes Rust APIs for certificate loading, feature checks, machine limits, and certificate data retrieval.

Important APIs/types/functions: `LicensedFeature` maps feature enum variants to C-string DNS names. `ExternalBuf` owns C buffers returned by the library and frees them on drop. `LoadedLibrary` dynamically loads expected symbols and provides safe-ish wrappers. `LicenseVerifier` exposes `with_lib()`, `with_no_lib()`, `load_and_verify_license_cert()`, `get_license_cert_data()`, `get_licensed_machines()`, and `verify_licensed_feature()`.

Control flow: startup loads function pointers from the configured library path, initializes the cert store, reads PEM asynchronously, verifies it via FFI, decodes prost protobuf results, rejects reusing a different trial serial, and logs success. Feature verification calls the library per requested feature and maps result enums to `anyhow` errors.

State and persistence: no local persistence; the external library caches the last verified cert. Trial serial persistence is handled by `lib.rs` through DB config.

Dependencies and integration points: used by startup and gRPC/license/feature gates. Depends on `libloading`, prost-generated license protobufs, C ABI function signatures, and configured certificate/library files.

Risks: loading arbitrary dynamic libraries and calling assumed signatures is unsafe; comments document the contract. Missing library makes all licensed features unavailable. External buffer pointers must be valid NUL-terminated strings and freed by the matching function.

Test signals: no direct tests. Useful coverage would use a fake dynamic library or abstraction to validate valid/invalid/error results, trial serial mismatch, machine-limit DNS parsing, and no-library behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/license.rs -->

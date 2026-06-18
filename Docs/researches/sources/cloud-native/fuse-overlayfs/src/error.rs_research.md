<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/error.rs -->
# sources/cloud-native/fuse-overlayfs/src/error.rs

Purpose: small errno-based error type for filesystem operations.

Important APIs: `FsError` wraps a `libc::c_int`, provides `last`, implements `Display` through `io::Error::from_raw_os_error`, implements `std::error::Error`, converts from `rustix::io::Errno` and `std::io::Error`, and defines `FsResult<T>`. `cstr` and `cstr_bytes` convert paths to `CString`, returning `EINVAL` on embedded nulls.

State and integration: stateless error glue used throughout sys, direct, copy-up, and overlay layers. Risks include losing richer IO context, defaulting unknown IO errors to `EIO`, and callers comparing raw errno values. Test signal is indirect through error paths in unit/integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/error.rs -->

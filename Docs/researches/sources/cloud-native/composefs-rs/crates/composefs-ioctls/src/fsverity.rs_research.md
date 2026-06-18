## sources/cloud-native/composefs-rs/crates/composefs-ioctls/src/fsverity.rs

Purpose: this module contains the low-level Linux fs-verity ioctl wrappers. It converts raw `FS_IOC_ENABLE_VERITY` and `FS_IOC_MEASURE_VERITY` calls into safe Rust functions and typed errors.

Important APIs and types: `EnableVerityError` classifies enable failures as I/O, unsupported filesystem, already enabled, writable-open conflict, or signature verification failure. `MeasureVerityError` classifies measure failures as I/O, verity missing, unsupported filesystem, invalid digest algorithm, or invalid digest size. `FsVerityEnableArg` mirrors `struct fsverity_enable_arg`, including signature pointer fields and reserved padding. `FsVerityDigest<const N>` mirrors `struct fsverity_digest` with a const generic digest byte array. Public functions are `fs_ioc_enable_verity`, `fs_ioc_enable_verity_with_sig`, and `fs_ioc_measure_verity<const N>`.

Control flow: `fs_ioc_enable_verity` delegates to the signature-aware function with `None`. `fs_ioc_enable_verity_with_sig` converts an optional byte slice into kernel size/pointer fields, builds version 1 enable args with no salt, and invokes `rustix::ioctl::Setter`. It maps specific `Errno` values (`NOTTY`, `OPNOTSUPP`, `EXIST`, `TXTBSY`, `KEYREJECTED`) into semantic errors. `fs_ioc_measure_verity` initializes the digest request with the expected algorithm and size, invokes `rustix::ioctl::Updater`, then validates the kernel-filled algorithm and size before returning the digest array.

State and persistence: enabling fs-verity changes persistent file metadata in the underlying filesystem and requires a read-only fd with no writable opens. Measuring does not mutate state but depends on existing fs-verity metadata. The wrapper does not cache anything and passes borrowed fds through `AsFd`.

Dependencies and integration: the module uses `rustix` for ioctl opcodes and errno, `std::io::Error` for fallback conversion, and `thiserror` for public error display. Higher-level repository code can use this crate while keeping unsafe code isolated here.

Risks: correctness depends on the C layout of the repr(C) structs and hard-coded ioctl numbers matching kernel headers. Signature and salt support is minimal: signatures can be supplied, but salt fields are always zero. The signature pointer is only valid for the duration of the syscall, which is appropriate for ioctl but must not become async. `OVERFLOW` during measure is converted into `InvalidDigestSize` with the kernel-reported size as `expected`, which is useful diagnostically but easy to misread.

Test signals: tests create temp files, reopen via `/proc/self/fd` read-only, and assert `VerityMissing` for regular files without fs-verity. `/dev/shm` gated tests assert unsupported filesystem behavior for both measure and enable. These tests exercise kernel error mapping but do not enable successful fs-verity on a supporting filesystem.

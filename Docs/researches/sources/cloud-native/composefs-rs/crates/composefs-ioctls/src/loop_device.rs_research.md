## sources/cloud-native/composefs-rs/crates/composefs-ioctls/src/loop_device.rs

Purpose: this feature-gated module wraps Linux loop-device ioctls for creating a loop device backed by an existing file, mainly for mounting composefs images on kernels that need loop indirection.

Important APIs and types: `flags` exposes `LO_FLAGS_READ_ONLY`, `LO_FLAGS_AUTOCLEAR`, `LO_FLAGS_PARTSCAN`, and `LO_FLAGS_DIRECT_IO`. `LoopConfig` and `LoopInfo64` mirror kernel loop configuration structs. `LoopCtlGetFree` is a custom `rustix::ioctl::Ioctl` implementation because `LOOP_CTL_GET_FREE` returns the loop number in the syscall return value rather than through an argument pointer. Public functions are `loopify` and `loopify_with_flags`.

Control flow: `loopify` calls `loopify_with_flags` with read-only, autoclear, and direct-I/O defaults. `loopify_with_flags` opens `/dev/loop-control`, invokes `LOOP_CTL_GET_FREE`, rejects negative results, opens `/dev/loopN`, builds a `LoopConfig` with the backing fd raw number, 4096-byte block size, and requested flags, then invokes `LOOP_CONFIGURE`. The returned `OwnedFd` owns the opened loop device; autoclear means the kernel detaches when the last fd closes if that flag is used.

State and persistence: this mutates kernel loop-device state by binding a backing file to a free loop device. Persistence is kernel-managed and normally bounded by the lifetime of open fds when autoclear is set. The function does not write repository state and does not maintain user-space bookkeeping.

Dependencies and integration: uses `std::fs::OpenOptions`, fd traits, and `rustix::ioctl`. It is exported only behind the crate's `loop-device` feature, keeping the default ioctl surface limited to fs-verity.

Risks: struct layout and ioctl constants are hard-coded and must match Linux headers. The code assumes `/dev/loop-control` and `/dev/loopN` naming. `fd.as_raw_fd() as u32` would be problematic only for extremely large fd numbers. Direct-I/O default may not work for all backing files or filesystems. This operation usually needs privileges or device access; tests account for permission failure.

Test signals: `test_loopify_not_root` creates a 4 KiB temp file and calls `loopify`, asserting non-root users get an error rather than a panic. It is a smoke test for code path safety, not a privileged success test.

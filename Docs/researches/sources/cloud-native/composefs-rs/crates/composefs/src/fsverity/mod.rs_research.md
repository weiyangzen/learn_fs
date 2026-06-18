# sources/cloud-native/composefs-rs/crates/composefs/src/fsverity/mod.rs

## Purpose
This is the public fs-verity facade. It exports hash value types and userspace hashing, wraps kernel enable/measure ioctls, handles transient enable failures, provides copy-on-enable fallback, offers optional/software-fallback measurement, and compares measured digests to expected values.

## Important APIs, Types, and Functions
Public exports include `FsVerityHasher`, `Algorithm`, `AlgorithmParseError`, `DEFAULT_LG_BLOCKSIZE`, `FsVerityHashValue`, `Sha256HashValue`, `Sha512HashValue`, `EnableVerityError`, and `MeasureVerityError`. `CompareVerityError` distinguishes measurement failures from digest mismatches. Main functions are `compute_verity()`, `enable_verity_raw()`, `enable_verity_with_retry()`, `enable_verity_maybe_copy()`, `measure_verity()`, `measure_verity_opt()`, `measure_verity_with_fallback()`, `has_verity()`, and `ensure_verity_equal()`.

## Control Flow
`compute_verity()` delegates to the userspace hasher. `enable_verity_raw()` calls the ioctl wrapper. `enable_verity_with_retry()` retries `FileOpenedForWrite` up to three attempts with 1 ms sleeps, covering inherited write fds during concurrent forks. `enable_verity_maybe_copy()` first tries the original fd and, on persistent `FileOpenedForWrite`, calls `enable_verity_on_copy()`. That helper clones and rewinds the source, creates an `O_TMPFILE` in the supplied directory, copies bytes, opens a read-only fd through `/proc/self/fd`, drops the writable fd, and loops until enabling verity succeeds on the copy.

Measurement flows are layered. `measure_verity()` calls the raw ioctl. `measure_verity_opt()` converts missing or unsupported verity into `Ok(None)`. `measure_verity_with_fallback()` first tries kernel measurement and then streams the file through `FsVerityHasher` when the kernel cannot provide a digest. `ensure_verity_equal()` measures and compares, returning a structured mismatch with expected/found hex strings.

## State and Persistence Behavior
Enabling verity mutates file metadata and makes the file immutable under kernel fs-verity semantics. The copy path creates an anonymous tmpfile and returns it to the caller, who must link or otherwise persist it if needed. Measurement and fallback hashing do not persist state. Retry behavior is time-dependent but bounded.

## Dependencies and Integration Points
This module integrates the local `digest`, `hashvalue`, and `ioctl` submodules with `rustix` open/openat, standard file I/O, and `proc_self_fd()`. It is used by repository object storage, flat digest storage, filesystem scanning, and verification/mount logic. The private `has_verity()` dispatches based on runtime `Algorithm`.

## Risks and Edge Cases
`enable_verity_on_copy()` loops until enable succeeds; if a filesystem repeatedly creates problematic tmpfiles or environmental conditions persist, that can spin. The copy path intentionally does not sync copied contents, leaving durability to callers. `measure_verity_with_fallback()` accepts `impl AsFd + Read`, so callers must pass a readable object positioned at the beginning or otherwise understand the current read position. Optional measurement hides unsupported filesystems as `None`, which is correct for fallback paths but not for strict security checks.

## Test Signals
Tests cover missing verity, simple enable/measure/compare, digest mismatch reporting, concurrent fork retry behavior, unsupported filesystems, wrong hash algorithm and digest size errors, kernel/userspace cross-checks over many size edge cases, direct enable without copy, and forced copy when the fd is read-write.

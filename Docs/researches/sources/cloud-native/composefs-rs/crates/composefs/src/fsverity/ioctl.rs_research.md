# sources/cloud-native/composefs-rs/crates/composefs/src/fsverity/ioctl.rs

## Purpose
This module is the low-level adapter between composefs-rs generic hash types and the `composefs-ioctls` fs-verity API. It hides kernel ioctl details behind typed enable and measure functions.

## Important APIs, Types, and Functions
It re-exports `EnableVerityError` and `MeasureVerityError`. `fs_ioc_enable_verity<H>()` calls the underlying enable ioctl using `H::ALGORITHM.kernel_id()` and a 4096 byte block size. `fs_ioc_measure_verity<H>()` dispatches on the kernel hash ID, requests either a 32-byte or 64-byte digest, and converts the returned byte array into the caller's `FsVerityHashValue` type.

## Control Flow
Enable flow is direct: convert `impl AsFd` to a borrowed fd and call `composefs_ioctls::fsverity::fs_ioc_enable_verity`. Measurement matches the algorithm ID. ID 1 reads `[u8; 32]`, ID 2 reads `[u8; 64]`, and any other ID is considered unreachable because the local `Algorithm` type only exposes SHA-256 and SHA-512.

## State and Persistence Behavior
`fs_ioc_enable_verity()` changes kernel filesystem state by enabling fs-verity on the target file. `fs_ioc_measure_verity()` is read-only but relies on kernel state and validates digest size/algorithm through the lower crate. The module stores no state of its own.

## Dependencies and Integration Points
This file depends on `composefs-ioctls`, `std::os::fd::AsFd`, and `FsVerityHashValue`. It is private to the `fsverity` module, whose public functions add retry, copy, optional, fallback, and comparison semantics around these raw calls.

## Risks and Edge Cases
The hardcoded 4096 block size must match `DEFAULT_LG_BLOCKSIZE` and userspace digest construction. `H::read_from_bytes(...).expect("size mismatch")` is safe for current concrete hash sizes but would panic if a future `FsVerityHashValue` had inconsistent size and kernel ID. Tests requiring `/dev/shm` are environment-sensitive and gated by `test_with`.

## Test Signals
Tests cover missing verity on a temporary file, unsupported filesystem behavior on `/dev/shm`, and enabling on unsupported filesystems. Deeper bad-fd behavior is delegated to the lower `composefs-ioctls` crate because this crate forbids unsafe code.

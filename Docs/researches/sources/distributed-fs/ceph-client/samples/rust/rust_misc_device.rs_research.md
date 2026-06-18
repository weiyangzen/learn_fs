# sources/distributed-fs/ceph-client/samples/rust/rust_misc_device.rs

## Purpose

This Rust module demonstrates a misc character device with per-open state, read/write iterators, and ioctl handling.

## Important APIs, Types, and Functions

It uses `MiscDeviceRegistration`, the `MiscDevice` trait, `File`, `Kiocb`, `IovIterDest`, `IovIterSource`, `UserSliceReader`, `UserSliceWriter`, ioctl helpers `_IO`, `_IOR`, `_IOW`, `Mutex<Inner>`, `KVVec<u8>`, and `PinnedDrop`. IOCTLs are `HELLO`, `GET_VALUE`, and `SET_VALUE`.

## Control Flow

Module init registers `/dev/rust-misc-device`. Each open allocates a pinned `RustMiscDevice` with value `0` and empty buffer. `write_iter()` replaces the buffer with user data and resets file position; `read_iter()` copies buffer contents respecting file position. `ioctl()` dispatches by command to set/get the integer value or log hello; unknown commands return `ENOTTY`.

## State and Persistence Behavior

State is per-open, not global: each file instance has its own mutex-protected `value` and `buffer`, plus a device reference. Data persists only for that open file handle. Drop logs when the per-open object exits.

## Dependencies and Integration Points

It integrates with miscdevice registration, VFS read/write/ioctl paths, user access APIs, and kernel Rust synchronization/allocation.

## Risks and Edge Cases

Large writes allocate into a `KVVec` and can fail. IOCTL argument size comes from command encoding; malformed user pointers return access errors. Per-open state may surprise users expecting global device state.

## Test Signals

Use the C example in comments: open the device, call hello, get/set/get value, perform read/write, and verify unknown ioctl fails.

# sources/distributed-fs/ceph-client/rust/helpers/bitmap.c

## Purpose
Exports bitmap copy-and-extend behavior to Rust.

## APIs, Types, and Functions
`rust_helper_bitmap_copy_and_extend()` wraps `bitmap_copy_and_extend()`.

## Control Flow, State, and Persistence
The helper writes the destination bitmap from a source bitmap, extending/truncating according to bit counts; no local state is kept.

## Dependencies and Integration
Depends on `linux/bitmap.h` and Rust bitset/cpumask-style abstractions.

## Risks and Test Signals
Risks are caller buffer sizing and count/size confusion. Test signals include boundary bit counts, non-word-aligned sizes, and Rust-side buffer length checks.

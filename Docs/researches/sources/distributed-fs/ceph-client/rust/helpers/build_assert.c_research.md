# sources/distributed-fs/ceph-client/rust/helpers/build_assert.c

## Purpose
Performs C-side static assertions required by Rust allocation and binding assumptions.

## APIs, Types, and Functions
Contains a `static_assert()` requiring C `size_t` to match `uintptr_t` in size and alignment, matching Rust `usize` expectations from bindgen.

## Control Flow, State, and Persistence
There is no runtime control flow or state; failure is a compile-time build break.

## Dependencies and Integration
Depends on `linux/build_bug.h` and the bindgen assumption that `size_t` maps to Rust `usize`.

## Risks and Test Signals
Risks are porting Rust support to unusual ABIs where object-size and pointer-size types diverge. Test signals are cross-architecture allmodconfig-style builds and early compile failure on unsupported ABIs.

# sources/distributed-fs/ceph-client/samples/rust/rust_debugfs_scoped.rs

## Purpose

This Rust module demonstrates scoped debugfs lifetimes. It creates a control directory with write-only callbacks that dynamically create and remove per-device debugfs subdirectories.

## Important APIs, Types, and Functions

It uses `debugfs::Dir`, `debugfs::Scope`, callback files, `KBox::pin_init`, `KVec`, `Atomic<usize>`, `Mutex`, `CString`, and `UserSliceReader`. `ModuleData` stores the base dynamic directory and a vector of pinned device scopes. `DeviceData` stores a name, atomic numeric files, and a binary blob.

## Control Flow

Module init creates `rust_scoped_debugfs`, a `dynamic` subdir, and a `control` scope. Writing `control/create` parses a name plus numeric values, creates a scoped directory under `dynamic`, adds one read/write file per numeric value plus a `blob`, and stores the scope in `devices`. Writing `control/remove` reads a name and retains only devices whose name differs.

## State and Persistence Behavior

Dynamic state is the `devices` vector under a mutex. Each element owns a scope; removing it from the vector drops the scope and removes that subtree. Numeric files hold atomic values, and the blob is a pinned mutex-protected 4 KiB array.

## Dependencies and Integration Points

It depends on Rust debugfs scope APIs, allocation, mutexes, and debugfs being enabled.

## Risks and Edge Cases

Input parsing caps names at 127 bytes and rejects invalid UTF-8 or numeric tokens. A failure while creating per-index filenames silently returns from the scope builder, so partial directories may be possible. Debugfs callbacks run in kernel context and must avoid unbounded allocation from hostile input.

## Test Signals

Load the module, write commands such as `dev0 1 2 3` to `control/create`, inspect `dynamic/dev0/`, mutate numeric files/blob, then remove by writing `dev0` to `control/remove`.

# sources/cloud-native/nydus/clib/src/fs.rs

## Purpose
This module implements the filesystem-level C ABI for opening and closing RAFS instances from Rust. It parses C strings into Rust strings, constructs RAFS with either caller-supplied or default localfs configuration, imports bootstrap metadata, and returns opaque handles.

## Important APIs, Types, and Functions
Exports are `nydus_open_rafs`, `nydus_open_rafs_default`, and `nydus_close_rafs`. `FileSystemState` stores a magic number, root inode, and `Rafs` instance. Helper methods `from_handle` and `try_from_handle` convert raw handles back into mutable references. `default_localfs_rafs_config`, `do_nydus_open_rafs`, and `fs_error_einval` implement shared behavior.

## Control Flow
Open functions reject null pointers, convert C strings via `cstr_to_str!`, construct `ConfigV2`, call `Rafs::new`, import the reader, capture the root inode, box `FileSystemState`, and return the pointer as `NydusFsHandle`. The default open path resolves a relative bootstrap under the supplied directory and synthesizes a TOML localfs config. Close converts the handle back to a `Box`, asserts the magic, mutates it, and calls `rafs.destroy().unwrap()`.

## State, Persistence, and Dependencies
State is heap-owned by the returned handle and includes RAFS runtime state. Dependencies include `nydus_api::ConfigV2`, `nydus_rafs::fs::Rafs`, `Arc`, and path/C string utilities.

## Integration Points
This is the root of the C ABI object graph: file handles store a `NydusFsHandle` and call back into this state. It integrates with storage backend config parsing and RAFS metadata import.

## Risks and Test Signals
Unsafe handle conversion returns `'static mut` references from raw pointers, so aliasing and lifetime correctness rely entirely on the caller. Invalid non-null handles and double close panic. `rafs.destroy().unwrap()` can panic across FFI. Tests cover null open errors, explicit config open, and default localfs open against fixtures.

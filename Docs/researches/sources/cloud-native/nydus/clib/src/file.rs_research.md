# sources/cloud-native/nydus/clib/src/file.rs

## Purpose
This Rust FFI module defines C-facing RAFS file handle operations. It currently provides handle allocation and close/forget behavior, with actual path lookup and read/seek operations still absent.

## Important APIs, Types, and Functions
Exports are `nydus_fopen` and `nydus_fclose`. `FileState` stores a magic value, inode, current position, and owning filesystem handle. Public constants are `NYDUS_FILE_HANDLE_MAGIC`, `NYDUS_INVALID_FILE_HANDLE`, and type alias `NydusFileHandle`.

## Control Flow
`nydus_fopen` validates the C path pointer, converts the filesystem handle through `FileSystemState::try_from_handle`, then currently creates a `FileState` pointing to the filesystem root inode and returns its boxed raw pointer. `nydus_fclose` converts the handle back to `Box<FileState>`, asserts the magic value, obtains the filesystem from `fs_handle`, calls RAFS `forget` for one lookup on the stored inode, mutates the magic, and drops the box.

## State, Persistence, and Dependencies
State is heap-allocated per file handle. It depends on `fuse_backend_rs::api::filesystem::{Context, FileSystem}` for the `forget` call and on crate-level `set_errno`, `FileSystemState`, `Inode`, and `NydusFsHandle`.

## Integration Points
It integrates with `fs.rs` handles and RAFS inode lifecycle accounting. The header advertises this as file-open/close API for C callers, but the actual open implementation is marked TODO and does not use the requested path.

## Risks and Test Signals
Major risks are unsafe raw pointer ownership, null or stale handle misuse, double close causing undefined behavior, and `assert_eq!` panics across FFI boundaries. `nydus_fopen` ignores the path and opens root, so consumers cannot rely on true file access yet. There are no visible direct tests for file handles in this file.

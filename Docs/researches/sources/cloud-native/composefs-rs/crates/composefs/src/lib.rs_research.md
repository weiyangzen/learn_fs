# sources/cloud-native/composefs-rs/crates/composefs/src/lib.rs

## Purpose
This is the crate root for composefs library bindings and utilities. It declares the public module surface, enforces safety/lint policy, and defines format-level constants shared by scanners, parsers, image writers, and streaming code.

## Important APIs, Types, and Functions
The crate exposes modules including `dumpfile`, `dumpfile_parse`, `erofs`, `filesystem_ops`, `fs`, `fsverity`, `mount`, `mountcompat`, `progress`, `repository`, `splitstream`, `tree`, `util`, and `generic_tree`. It re-exports `repository::ImageNotFound` and conditionally exposes `test`. Public constants are `INLINE_CONTENT_MAX_V0`, `MAX_INLINE_CONTENT`, and `SYMLINK_MAX`. The hidden `shared_internals::IO_BUF_CAPACITY` sets a 64 KiB streaming buffer size.

## Control Flow
There is no runtime control flow in this file beyond module loading. Its most important behavior is compile-time: `#![forbid(unsafe_code)]` applies crate-wide, and non-test builds deny direct stdout/stderr printing through Clippy except where locally allowed.

## State and Persistence Behavior
The constants define persistent format behavior. `INLINE_CONTENT_MAX_V0` controls whether files are embedded inline or stored externally with fs-verity-backed object references; changing it is explicitly a format break. `MAX_INLINE_CONTENT` is a parsing safety bound for untrusted input and intentionally exceeds the current writer threshold. `SYMLINK_MAX` enforces an XFS-compatible symlink target limit.

## Dependencies and Integration Points
Every other public module is rooted here. `fs.rs` uses `INLINE_CONTENT_MAX_V0` and `shared_internals::IO_BUF_CAPACITY`; parsers use `MAX_INLINE_CONTENT`; symlink validators use `SYMLINK_MAX`; repository users rely on the `ImageNotFound` re-export.

## Risks and Edge Cases
Changing exported module names or constants can break downstream APIs or image compatibility. The crate-level print lint has a documented exception in `mount::FsHandle::drop()` where kernel diagnostics are only available during drop. Hidden internals are not stable API, but cross-crate workspace users may still come to depend on them.

## Test Signals
This file has no direct tests. Its guarantees are exercised by compilation of the whole crate and by downstream module tests that depend on constants and module visibility.

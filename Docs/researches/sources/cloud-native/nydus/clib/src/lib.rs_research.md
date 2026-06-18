# sources/cloud-native/nydus/clib/src/lib.rs

## Purpose
This crate root documents the C wrapper library, declares public FFI modules, and provides small shared helpers for errno and C string conversion.

## Important APIs, Types, and Functions
It re-exports `file::*` and `fs::*`, defines `Inode = u64`, imports `file` and `fs` modules, and defines the `set_errno` helper plus `cstr_to_str!` macro. The macro converts `*const c_char` into UTF-8 `&str`, sets `EINVAL`, and returns a caller-supplied value on invalid C string or invalid UTF-8.

## Control Flow
FFI functions call `cstr_to_str!` after null checks to normalize C string handling. `set_errno` writes to platform errno through `libc::__errno_location` on Linux or `libc::__error` on macOS.

## State, Persistence, and Dependencies
The module mutates thread-local process errno. It depends on `libc`, `std::ffi::CStr`, and exported modules. There is no durable persistence.

## Integration Points
This file is the shared support layer for `fs.rs` and potentially future FFI modules. Its cbindgen command in the docs drives `include/nydus.h` generation.

## Risks and Test Signals
The errno helper is platform-gated to Linux and macOS. Returning from the macro requires each call site to supply a valid return expression. Invalid UTF-8 is treated as `EINVAL`. Tests are indirect through the filesystem module’s null pointer and open cases.

# sources/distributed-fs/ceph-client/rust/helpers/fs.c

## Purpose
Exposes file reference acquisition to Rust.

## APIs, Types, and Functions
`rust_helper_get_file()` wraps `get_file()`.

## Control Flow, State, and Persistence
The helper increments the file refcount and returns the same file pointer; persistent state is the caller-owned reference.

## Dependencies and Integration
Depends on `linux/fs.h` and Rust file abstractions.

## Risks and Test Signals
Risks are leaked references and use-after-fput in wrappers. Test signals are file refcount tests and open/close stress.

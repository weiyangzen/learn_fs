# sources/distributed-fs/ceph-client/rust/helpers/build_bug.c

## Purpose
Exposes kernel error-name formatting to Rust.

## APIs, Types, and Functions
`rust_helper_errname()` wraps `errname()` and returns a static string for an errno value when known.

## Control Flow, State, and Persistence
The helper has no local state and returns pointers owned by kernel error-name tables.

## Dependencies and Integration
Depends on `linux/errname.h` and Rust error/debug formatting paths.

## Risks and Test Signals
Risks are caller assumptions that every errno has a non-null stable name and lifetime misuse. Test signals include formatting common and unknown errno values.

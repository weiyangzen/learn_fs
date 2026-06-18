# sources/distributed-fs/ceph-client/rust/helpers/uaccess.c

## Purpose
Exposes user-memory copy helpers to Rust.

## APIs, Types, and Functions
Exports `copy_from_user` and `copy_to_user`; when inline copy helpers are configured, also exports `_copy_from_user` and `_copy_to_user` wrappers.

## Control Flow, State, and Persistence
State is user and kernel memory contents; helpers return uncopied byte counts and keep no local state.

## Dependencies and Integration
Depends on `linux/uaccess.h`, architecture user access rules, and Rust user-slice abstractions.

## Risks and Test Signals
Risks include partial copies, fault handling, missing access validation in callers, and sleeping/pagefault context constraints. Test signals are usercopy KUnit tests, fault injection, hardened usercopy, and Rust user-slice tests.

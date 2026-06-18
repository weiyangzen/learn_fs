# sources/distributed-fs/ceph-client/rust/helpers/kunit.c

## Purpose
Exposes current KUnit test lookup to Rust test code.

## APIs, Types, and Functions
`rust_helper_kunit_get_current_test()` wraps `kunit_get_current_test()`.

## Control Flow, State, and Persistence
No local state; returns the current task's KUnit test context when present.

## Dependencies and Integration
Depends on `kunit/test-bug.h` and Rust KUnit macro infrastructure.

## Risks and Test Signals
Risks are null handling outside KUnit context and task-local assumptions. Test signals are Rust KUnit tests and non-test builds.

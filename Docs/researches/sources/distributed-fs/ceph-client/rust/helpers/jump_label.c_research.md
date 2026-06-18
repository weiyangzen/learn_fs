# sources/distributed-fs/ceph-client/rust/helpers/jump_label.c

## Purpose
Provides a Rust helper for static key count fallback when jump labels are disabled.

## APIs, Types, and Functions
Under `!CONFIG_JUMP_LABEL`, exports `rust_helper_static_key_count()` wrapping `static_key_count()`.

## Control Flow, State, and Persistence
No local state; reads static-key state maintained by jump-label/static-key core.

## Dependencies and Integration
Depends on `linux/jump_label.h` and Rust static-branch abstractions.

## Risks and Test Signals
Risks are config-dependent behavior and stale assumptions about enabled/disabled static branches. Test signals are builds with and without `CONFIG_JUMP_LABEL` and Rust static-key tests.

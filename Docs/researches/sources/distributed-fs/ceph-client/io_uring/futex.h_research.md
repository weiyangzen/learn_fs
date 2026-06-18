# sources/distributed-fs/ceph-client/io_uring/futex.h

## Purpose
The header declares io_uring futex operation, cancellation, and cache functions with disabled-feature stubs.

## Important APIs, Types, And Functions
- Operation handlers: `io_futex_prep`, `io_futexv_prep`, `io_futex_wait`, `io_futexv_wait`, and `io_futex_wake`.
- Enabled `CONFIG_FUTEX` APIs for cancellation and cache lifecycle.
- Disabled stubs return no-op/false success for cancellation and cache lifecycle.

## Control Flow
Only disabled-feature stubs have local control flow, returning neutral values for callers.

## State And Persistence
No state is defined here. Functions operate on ring futex cache/list and request async data.

## Dependencies And Integration Points
It includes `cancel.h` and is used by opcode dispatch and generic cancellation code.

## Risks And Edge Cases
When futex support is disabled, callers must not dispatch futex operations but generic cancellation can safely call no-op stubs. Prototype correctness is important because futex cancellation is part of ring teardown.

## Test Signals
Builds with `CONFIG_FUTEX=y/n` and futex operation/cancellation tests validate behavior.

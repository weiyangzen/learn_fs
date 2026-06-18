# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/signals.S

## Purpose

This assembly helper fabricates an `rt_sigreturn` using caller-provided sigframe bytes, optionally misaligning the stack, so negative signal-frame validation tests can ask the kernel to restore malformed frames.

## Important APIs, Types, and Functions

It exports `fake_sigreturn(sigframe, sigframe_size, misalign_bytes)`. It calls `printf()` and `memcpy()`, stores the final fake frame address into `current->token`, then invokes syscall `__NR_rt_sigreturn`.

## Control Flow and Data Flow

The routine saves frame pointer/link register, computes aligned stack space for the fake frame plus optional misalignment, copies the supplied frame to the new stack location, records the token for sanity checks, moves SP to the fake frame, and executes `svc #0` for `rt_sigreturn`. If the syscall unexpectedly returns, it loops forever to force timeout failure.

## State and Persistence Behavior

It mutates the thread stack and `current->token`. There is no persistent storage.

## Dependencies and Integration Points

It depends on the C global `current`, `struct tdescr` layout with `token` first, libc `printf`/`memcpy`, and the arm64 `rt_sigreturn` syscall number.

## Risks and Edge Cases

The helper assumes stack alignment rules, `current->token` offset zero, and that malformed frames fail before unsafe control flow resumes. Misuse can corrupt the stack permanently within the test process.

## Test Signals

Expected negative tests terminate with the configured SIGSEGV; returning to the infinite loop indicates the kernel accepted a frame it should reject.

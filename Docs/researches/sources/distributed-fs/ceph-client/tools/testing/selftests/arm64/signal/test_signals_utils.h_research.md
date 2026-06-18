# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/test_signals_utils.h

## Purpose

This header declares the signal framework entry points and provides inline helpers for GCS state control, GCS pointer reads, feature checks, live context capture, and `fake_sigreturn()`.

## Important APIs, Types, and Functions

It declares `test_init()`, `test_setup()`, `test_cleanup()`, `test_run()`, and `test_result()`. It defines `gcs_set_state()` as a raw `prctl` syscall wrapper with zeroed unused args, `get_gcspr_el0()`, `feats_ok()`, and `get_current_context()`.

## Control Flow and Data Flow

`get_current_context()` prepares destination storage, points the descriptor at it, triggers `SIGTRAP` with `brk #666`, waits for the signal handler to copy the kernel-provided context, exits SME streaming/ZA state with `SMSTOP` if needed, and detects accidental returns into a previously restored context.

## State and Persistence Behavior

It mutates descriptor live-context fields and uses a static `seen_already` flag inside `get_current_context()` to detect unexpected successful sigreturn reuse. Raw GCS and SME instructions mutate process architectural state.

## Dependencies and Integration Points

It depends on `testcases.h` validation macros, arm64 syscall numbers, GCS PRCTL constants, inline assembly, and the default signal handler in `test_signals_utils.c`.

## Risks and Edge Cases

The context capture path deliberately avoids normal syscalls for signal delivery because they may discard SVE state. Destination size must be large enough for extra contexts. The raw GCS syscall wrapper is used because libc wrappers may not expose the newest ABI.

## Test Signals

Successful context capture returns true with `td->live_uc_valid` set; malformed contexts abort through validation diagnostics.

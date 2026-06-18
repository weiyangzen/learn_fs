# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/test_signals.c

## Purpose

This is the common `main()` wrapper for all arm64 signal testcases. Each testcase links a global `struct tdescr tde`; this file runs setup, initialization, execution, cleanup, and result reporting around it.

## Important APIs, Types, and Functions

It defines `struct tdescr *current = &tde` and `main()`. It calls `gcs_set_state()`, `test_setup()`, `test_init()`, `test_run()`, `test_cleanup()`, and `test_result()`.

## Control Flow and Data Flow

At startup it enables GCS if hardware advertises it, prints the testcase name/description, runs framework setup and testcase initialization, triggers or directly runs the testcase, cleans up, reports the result, and exits with the kselftest result code.

## State and Persistence Behavior

`current` points at the testcase descriptor. Enabling GCS changes process shadow-stack state for the process lifetime; the program exits instead of returning to avoid GCS return complications.

## Dependencies and Integration Points

It depends on auxv HWCAPs, GCS PRCTL wrapper from `test_signals_utils.h`, and the descriptor supplied by each testcase.

## Risks and Edge Cases

If libc locked GCS state, enabling can fail and tests continue. Missing or malformed `tde` fields are asserted later in setup. Returning from `main()` is intentionally avoided.

## Test Signals

Every testcase executable starts here; pass/fail/skip behavior is centralized in `test_result()`.

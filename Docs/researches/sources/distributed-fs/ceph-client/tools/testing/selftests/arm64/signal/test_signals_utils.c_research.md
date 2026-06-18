# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/signal/test_signals_utils.c

## Purpose

This file implements the arm64 signal selftest framework: feature probing, default signal handlers, live `ucontext_t` capture, trigger routing, timeout handling, and default result reporting.

## Important APIs, Types, and Functions

Important internal helpers are `feats_to_string()`, `unblock_signal()`, `default_result()`, `handle_signal_unsupported()`, `handle_signal_trigger()`, `handle_signal_ok()`, `handle_signal_copyctx()`, `default_handler()`, `default_setup()`, and `default_trigger()`. Exported functions are `test_init()`, `test_setup()`, `test_run()`, `test_result()`, and `test_cleanup()`.

## Control Flow and Data Flow

`default_setup()` installs one SA_SIGINFO handler for most regular and RT signals, unblocks expected signals, and arms an alarm. `test_init()` reads auxv feature bits, handles required/incompatible features, runs testcase init, and marks initialization. The default handler dispatches unsupported-feature signals, trigger signals, expected success signals, and `SIGTRAP` copy-context service signals. Copy-context handling validates the kernel-provided sigframe, copies ordinary and extra context data into testcase storage, and adjusts PC past the breakpoint.

## State and Persistence Behavior

It mutates `current` descriptor fields including `triggered`, `pass`, `result`, `feats_supported`, `live_uc`, `live_uc_valid`, and `minsigstksz`. It installs process-wide signal handlers and alarms.

## Dependencies and Integration Points

It integrates with `testcases/testcases.c` validation, `fake_sigreturn()` assembly, auxv HWCAPs, arm64 signal frame layout, and kselftest result codes.

## Risks and Edge Cases

The SIGTRAP context capture intentionally uses inline `brk #666` and must avoid compiler/libc behavior incompatible with SME streaming mode. The handler copies extra contexts only after validation and fixes extra-context sizes for local use. Signal-wide handlers can turn unrelated faults into test failures, which is intended but makes diagnostics dependent on descriptor setup.

## Test Signals

Framework success is visible as descriptors receiving correct skip/pass/fail outcomes, `ASSERT_GOOD_CONTEXT()` validations succeeding, timeouts failing cleanly, and fake-sigreturn tests seeing expected SIGSEGV.

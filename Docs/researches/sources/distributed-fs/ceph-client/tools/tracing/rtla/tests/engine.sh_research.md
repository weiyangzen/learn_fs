# sources/distributed-fs/ceph-client/tools/tracing/rtla/tests/engine.sh

## Purpose

`engine.sh` is the shared shell harness for rtla tests. It provides TAP-style counting/output, rtla command execution, osnoise/timerlat tracefs reset, timeout configuration, and locale normalization.

## Important APIs, Types, and Functions

Functions are `test_begin()`, `reset_osnoise()`, `check()`, `check_with_osnoise_options()`, `set_timeout()`, `unset_timeout()`, `set_no_reset_osnoise()`, `unset_no_reset_osnoise()`, and `test_end()`. It uses environment variables `RTLA`, `TEST_COUNT`, `TIMEOUT`, and `NO_RESET_OSNOISE`.

## Control Flow and Data Flow

On first invocation, tests call `test_begin()` and emit checks without `TEST_COUNT`, which only increments a counter. `test_end()` re-execs the script with `TEST_COUNT` set so the second pass emits TAP plan and actually runs commands. `check()` resets tracefs unless disabled, runs `$RTLA` under optional timeout via `eval stdbuf -oL`, captures output and exit code, then validates expected/unexpected regexes.

## State and Persistence Behavior

`reset_osnoise()` mutates `/sys/kernel/tracing` by removing known rtla instances and restoring osnoise defaults. Harness state is shell variables. Test output is TAP-style stdout.

## Dependencies and Integration Points

It depends on bash, tracefs mounted at `/sys/kernel/tracing`, `timeout`, `stdbuf`, `grep`, `col`, and the rtla binary. It is sourced by rtla shell tests.

## Risks and Edge Cases

Use of `eval` means quoted test commands must be constructed carefully. Reset requires tracefs permissions. The two-pass counting model can hide side effects during count-only pass if tests do work outside `check()`. Regex validation uses grep extended regexes.

## Test Signals

Harness tests should confirm correct TAP count, command exit-code handling, output matching and nonmatching, osnoise reset side effects, timeout kill behavior, and `NO_RESET_OSNOISE` preservation for option-reset tests.

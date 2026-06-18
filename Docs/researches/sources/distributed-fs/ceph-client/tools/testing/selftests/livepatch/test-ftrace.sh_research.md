# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test-ftrace.sh

## Purpose

`test-ftrace.sh` checks livepatch interaction with the global `kernel.ftrace_enabled` sysctl and with function tracing on original and patched functions.

## Important APIs, Types, and Functions

It uses `set_ftrace_enabled()`, `load_lp()`, `load_failing_mod()`, `trace_function()`, `check_traced_functions()`, `/proc/cmdline`, and module `test_klp_livepatch`.

## Control Flow and State

The first scenario disables ftrace, expects livepatch load failure, reenables ftrace, verifies a patch affects `/proc/cmdline`, and expects attempts to disable ftrace while patched to fail. Later scenarios trace the patched replacement function and the original target function while confirming livepatch behavior remains active.

## Dependencies and Integration Points

It depends on ftrace, tracefs/debugfs, livepatch ftrace registration, sysctl writes, and dmesg checking.

## Risks and Test Signals

Risks are allowing livepatch registration when ftrace is disabled, allowing ftrace to be disabled under active livepatches, or tracing breaking patch dispatch. Signals are expected `-EBUSY`-style load/sysctl failures, `/proc/cmdline` showing patched text, and traced functions appearing in the trace buffer.

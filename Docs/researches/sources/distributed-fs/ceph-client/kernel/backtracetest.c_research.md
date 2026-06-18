# sources/distributed-fs/ceph-client/kernel/backtracetest.c

Purpose: a small loadable module regression test that deliberately emits stack traces from process context, BH workqueue context, and, when available, saved stack-trace APIs.

Important APIs/types/functions: `backtrace_test_normal` calls `dump_stack`; `backtrace_test_bh` queues `backtrace_test_bh_workfn` on `system_bh_wq` and waits with `flush_work`; `backtrace_test_saved` uses `stack_trace_save` and `stack_trace_print` under `CONFIG_STACKTRACE`; `backtrace_regression_test` is the `module_init` entry point.

Control flow: module initialization prints a banner, emits a direct stack dump, schedules and flushes BH-context work that dumps another stack, optionally captures and prints an array of saved return addresses, then prints an end banner. Module exit is intentionally empty.

State and persistence: uses one static `DECLARE_WORK` item and a stack-local `entries[8]` buffer for saved traces. It does not persist data beyond kernel logs.

Dependencies and integration: integrates with module loading, kernel workqueues, `dump_stack`, and optional `CONFIG_STACKTRACE`. Its output appears in the kernel log and is expected to look alarming while being a self-test.

Risks: false-positive bug reports are expected if users miss the banner. Test value depends on architecture stack unwinding quality and workqueue availability. The module does not assert results, so regressions are detected manually or by log inspection.

Test signals: successful load should show three self-test phases where saved trace is either printed or explicitly skipped. Oopses, missing workqueue trace, or stacktrace API build failures indicate regressions.

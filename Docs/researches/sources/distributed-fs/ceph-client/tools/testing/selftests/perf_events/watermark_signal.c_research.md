# sources/distributed-fs/ceph-client/tools/testing/selftests/perf_events/watermark_signal.c

Purpose: verifies a perf event configured with watermark wakeup can deliver asynchronous `SIGIO` to the owning process while waiting on a stopped child.

Important APIs/functions: `handle_sigio()` increments `sigio_count`; `do_child()` raises `SIGSTOP`, sleeps in a loop, raises `SIGSTOP` again, then exits. The test uses `PERF_TYPE_SOFTWARE` / `PERF_COUNT_SW_DUMMY`, `context_switch`, `watermark`, `wakeup_watermark=1`, `FASYNC`, `F_SETOWN`, and `F_SETSIG`.

Control flow: install SIGIO handler, fork child and wait for initial stop, open a perf event targeted at the child, configure async notification, mmap the perf buffer, enable the event, continue child, then expects `waitpid(..., WSTOPPED)` to be interrupted by SIGIO and `sigio_count >= 1`. Cleanup unmaps, closes, kills child, waits, and restores handler.

State and persistence: transient child, perf fd, mmaped ring buffer, and process signal handler. No persistent files.

Dependencies/integration: requires perf_event_open permission for child monitoring and signal delivery. Uses kselftest harness.

Risks: `mmap()` failure check compares against `NULL` rather than `MAP_FAILED`, so one failure mode may not be caught precisely. Timing depends on context-switch event generation and signal delivery.

Test signals: kselftest `EXPECT_*` assertions and stderr diagnostics; success requires at least one SIGIO.

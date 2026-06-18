# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/timer_crash.c

## Purpose
Regression test for BPF timer crash scenarios against array and hash maps.

## APIs, Types, and Functions
Defines `MODE_ARRAY`, `MODE_HASH`, `test_timer_crash_mode()`, and public `test_timer_crash()`.

## Control Flow, State, and Persistence
For each subtest, the skeleton is opened and loaded, `pid` and `crash_map` are written into BSS, the program is attached, and the test sleeps briefly to allow the timer path to execute. There is no persistent user-space state beyond skeleton BSS and the temporary attachment.

## Dependencies and Integration
Depends on `timer_crash.skel.h` and the test harness. The actual crash-provoking timer/map behavior lives in the generated BPF program.

## Risks and Test Signals
The main signal is absence of kernel crash plus successful load/attach; skip happens when timers are unsupported. Risks are that a one-microsecond sleep may not always trigger the intended path, and failures may manifest as kernel diagnostics rather than user-space assertions.

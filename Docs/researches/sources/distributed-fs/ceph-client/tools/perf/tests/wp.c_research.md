# sources/distributed-fs/ceph-client/tools/perf/tests/wp.c

## Purpose
This perf test suite validates hardware watchpoint events for read-only, write-only, read/write, and attribute modification scenarios using `perf_event_open()`.

## Important APIs, Types, And Functions
Important helpers are `wp_read()`, `get__perf_event_attr()`, `__event()`, `test__wp_ro()`, `test__wp_wo()`, `test__wp_rw()`, and `test__wp_modify()`. It uses `struct perf_event_attr`, `PERF_TYPE_BREAKPOINT`, `HW_BREAKPOINT_R/W`, `PERF_SAMPLE_IP`, `sys_perf_event_open()`, `perf_event_open_cloexec_flag()`, `read()`, `ioctl(PERF_EVENT_IOC_MODIFY_ATTRIBUTES)`, and `PERF_EVENT_IOC_ENABLE`.

## Control Flow
Each subtest opens a breakpoint event on volatile globals `data1` or `data2`, performs reads and/or writes, reads the event counter, and asserts expected counts. `test__wp_modify()` opens a write watchpoint on `data1`, modifies it to watch two bytes of `data2` while disabled, verifies writes are not counted until enabling the event, then verifies only writes inside the watched range count.

## State, Dependencies, And Integration
State is process-local volatile watched memory and kernel perf event file descriptors. The suite is declared manually as `suite__wp` with four `TEST_CASE_REASON` entries. Architecture guards skip s390x broadly, x86/i386 for read-only watchpoints, and i386 uses a 32-bit watched word due to hardware length limits.

## Risks And Test Signals
Hardware support, kernel breakpoint constraints, and `PERF_EVENT_IOC_MODIFY_ATTRIBUTES` availability drive skips and failures. `-ENODEV` maps to missing hardware support. Passing counts signal correct watchpoint triggering, disabled-state handling, and modified address/length semantics.

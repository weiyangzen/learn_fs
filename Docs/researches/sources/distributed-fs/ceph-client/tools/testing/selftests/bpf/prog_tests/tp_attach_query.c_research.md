# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tp_attach_query.c

## Purpose
Tests tracepoint attachment querying through `PERF_EVENT_IOC_QUERY_BPF` after attaching multiple BPF tracepoint programs through perf events.

## APIs, Types, and Functions
Entry point is `serial_test_tp_attach_query()`. It uses `bpf_prog_test_load()`, `bpf_prog_get_info_by_fd()`, `perf_event_open`, `PERF_EVENT_IOC_SET_BPF`, `PERF_EVENT_IOC_QUERY_BPF`, and perf enable/disable ioctls.

## Control Flow, State, and Persistence
The test reads the sched_switch tracepoint id from tracingfs/debugfs, configures a perf tracepoint attr, allocates a query buffer, and loops three times loading the same tracepoint BPF object, recording each program id, opening/enabling a perf event, attaching the program, and querying attached ids. It also checks null-id-array query, count-only query, bad pointer `EFAULT`, and undersized buffer `ENOSPC`. Cleanup unwinds perf fds and BPF objects.

## Dependencies and Integration
Depends on tracingfs/debugfs availability, perf event tracepoint support, `test_tracepoint.bpf.o`, BPF prog info APIs, and the legacy test harness `CHECK` macros.

## Risks and Test Signals
Risks include tracing filesystem path differences, perf permissions, CPU 0 availability, and cleanup labels using loop index state. Signals are queried program counts matching attachment order, returned ids matching saved prog ids, and expected negative ioctl errors.

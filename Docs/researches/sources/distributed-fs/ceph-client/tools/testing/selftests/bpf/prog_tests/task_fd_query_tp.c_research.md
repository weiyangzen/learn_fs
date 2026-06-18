# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/task_fd_query_tp.c

Purpose: validates `bpf_task_fd_query` for perf-event tracepoint attachments. It tests `sched/sched_switch` and `syscalls/sys_enter_read`.

Control flow loads `test_tracepoint.bpf.o`, resolves tracepoint id from tracing/debugfs, opens perf event, enables it, attaches BPF with `PERF_EVENT_IOC_SET_BPF`, then queries current process and perf fd. State includes tracepoint id buffer, perf event fd, BPF object, and query output fields. Dependencies are tracing filesystem path, perf event tracepoint support, syscall constants, and `bpf_task_fd_query`. Risks include apparent check using `err` rather than `pmu_fd` after `perf_event_open`, path differences across kernels, and cleanup if open/read fails. Test signals are returned `BPF_FD_TYPE_TRACEPOINT` and tracepoint names `sched_switch` and `sys_enter_read`.

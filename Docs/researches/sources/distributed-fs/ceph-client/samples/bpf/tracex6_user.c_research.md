<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tracex6_user.c -->
# sources/distributed-fs/ceph-client/samples/bpf/tracex6_user.c

## Purpose
`tracex6_user.c` tests BPF perf-event-array reads by opening perf counters on each CPU, inserting them into a BPF map, triggering the companion kprobes, and checking stored counter values.

## Important APIs, Types, And Functions
Important functions are `check_on_cpu()`, `test_perf_event_array()`, `test_bpf_perf_event()`, and `main()`. It uses `sys_perf_event_open()`, `sched_setaffinity()`, `bpf_map_update_elem()`, `ioctl(PERF_EVENT_IOC_ENABLE/DISABLE)`, `bpf_map_get_next_key()`, `bpf_map_lookup_elem()`, fork/wait, and libbpf attach APIs.

## Control Flow
`main()` loads and attaches all BPF programs, resolves three maps, and calls `test_bpf_perf_event()`. Each test forks one child per configured CPU. The child pins itself to the CPU, opens a perf event for that CPU, writes the fd to the perf event array, triggers kprobes through map operations, verifies both result maps, cleans up map entries and fd, and exits with status.

## State And Persistence
State includes per-child perf event fds, perf event array entries, result map entries, CPU affinity, and libbpf links. Entries are removed after each child check.

## Dependencies And Integration Points
It depends on perf event permissions and hardware support for cycles, software clock, raw instruction-retired, L1D load, LLC miss, and MSR TSC events. Some tests may fail in QEMU as noted.

## Risks And Edge Cases
The program forks based on `_SC_NPROCESSORS_CONF`, including offline CPUs where perf open or affinity can fail. It uses many `assert()` calls, causing abrupt abort on errors. Raw and dynamic PMU type constants are platform-specific.

## Test Signals
For each event type and CPU, output should show `CPU N: <counter>` and `CPU N: counter: ..., enabled: ..., running: ...`; a nonzero child status reports test failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tracex6_user.c -->

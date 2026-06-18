<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tracex6.bpf.c -->
# sources/distributed-fs/ceph-client/samples/bpf/tracex6.bpf.c

## Purpose
`tracex6.bpf.c` demonstrates reading perf event counters from BPF through both `bpf_perf_event_read()` and `bpf_perf_event_read_value()`.

## Important APIs, Types, And Functions
Maps are `counters` (`BPF_MAP_TYPE_PERF_EVENT_ARRAY`), `values` (hash of counter values), and `values2` (hash of `struct bpf_perf_event_value`). Programs are `bpf_prog1()` on `kprobe/htab_map_get_next_key` and `bpf_prog2()` on `kprobe/bpf_map_copy_value`.

## Control Flow
`bpf_prog1()` reads the current CPU's perf event counter from `counters` and stores it in `values`, ignoring common error ranges. `bpf_prog2()` filters to hash maps by CO-RE-reading `map_type`, reads the full counter/enabled/running value, and stores it in `values2`.

## State And Persistence
Perf event fds are supplied by userspace through `counters`. Read values persist in `values` and `values2` until userspace deletes them.

## Dependencies And Integration Points
It depends on kprobe attachment to BPF map functions, perf event arrays, CO-RE map type reads, and the userspace test that binds events per CPU and triggers map operations.

## Risks And Edge Cases
Probing BPF map internals is sensitive to instrumentation recursion; the sample comments avoid `*_map_lookup_elem` and probe `bpf_map_copy_value` instead. Counter availability depends on CPU/VM support. Error values from `bpf_perf_event_read()` need filtering.

## Test Signals
The companion should populate `values` and `values2` for each CPU with non-missing counter data and print counter/enabled/running values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tracex6.bpf.c -->

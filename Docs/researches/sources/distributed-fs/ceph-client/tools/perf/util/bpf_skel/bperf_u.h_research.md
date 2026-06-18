# sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/bperf_u.h

## sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/bperf_u.h

Purpose: this shared header defines the filter contract between user-space bperf and the follower BPF program.

Important types: `enum bperf_filter_type` enumerates global, CPU, PID, and TGID filtering. `struct bperf_filter_value` stores the accumulator row and an exit marker for filter-map entries.

Control flow and state: there is no executable logic; user space writes `bperf_filter_value` rows into the follower `filter` map, and BPF reads/mutates the `exited` byte.

Dependencies and integration: included by `bpf_counter.c` and `bperf_follower.bpf.c`; enum values are part of the ABI between them.

Risks: changing enum values or struct layout breaks map interpretation. The `exited` flag is only one byte and must remain compatible with BPF C layout assumptions.

Test signals: compile both user-space and BPF sides after layout changes and run PID/TGID exit/inheritance cases.

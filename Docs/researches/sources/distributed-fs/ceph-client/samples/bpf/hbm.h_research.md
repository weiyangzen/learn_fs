# sources/distributed-fs/ceph-client/samples/bpf/hbm.h

Purpose: shared Host Bandwidth Manager data structures used by userspace and BPF programs.

Important APIs/types/functions: `struct hbm_vqueue` contains `bpf_spin_lock`, credit, rate, and last timestamp; `struct hbm_queue_stats` contains rate/config flags, packet/byte counters, marks/drops/ECN counters, timing, congestion window/RTT sums, credit sum, and return-value counters.

Control flow: no executable flow; structures define the ABI between `hbm.c` and BPF map values.

State and persistence: values are persisted in BPF cgroup storage and array maps while programs are attached.

Dependencies and integration: included by `hbm.c` and `hbm_kern.h`. Layout must be valid for both userspace C and BPF C, including `bpf_spin_lock` constraints.

Risks: struct layout changes are ABI changes for map values. Spin locks in BPF map values impose verifier and map-type restrictions. Counter widths must be sufficient for high-throughput tests.

Test signals: BPF verifier accepts map value types, userspace can update/read `queue_stats`, and stats fields match BPF-side updates.

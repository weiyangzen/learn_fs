# sources/distributed-fs/ceph-client/samples/bpf/do_hbm_test.sh

Purpose: shell test harness for the Host Bandwidth Manager samples.

Important APIs/types/functions: orchestrates HBM BPF loader invocations, cgroup setup through the loader, traffic generation, iperf/netperf-style checks depending on environment, stats file collection, and cleanup of pinned links/cgroups.

Control flow: parses test options, starts HBM programs with rate/duration/stats flags, runs traffic workloads through the limited cgroup, waits for completion, collects `hbm.*.out` statistics and trace logs, and removes temporary state on exit.

State and persistence: creates temporary cgroups, pinned BPF links under bpffs, generated stats/log files, and background workload processes. Cleanup is required to avoid leaking cgroup or bpffs state.

Dependencies and integration: integrates with `hbm`, `hbm_out_kern.o`, `hbm_edt_kern.o`, the cgroup filesystem, bpffs, traffic tools, loopback or network interfaces, and privileged shell execution.

Risks: network and cgroup tests are environment-sensitive. Failure paths can leave pinned links or cgroups if traps do not run. Throughput expectations are hardware/NIC dependent, and work-conserving mode assumes `eth0` in the C loader.

Test signals: successful script completion, generated HBM stats files with expected rate/drop/mark fields, no leftover `/sys/fs/bpf/hbm*` pins, and no leaked test cgroups.

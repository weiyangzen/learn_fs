# sources/distributed-fs/ceph-client/samples/bpf/hbm.c

Purpose: userspace loader/controller for Host Bandwidth Management cgroup-skb BPF programs.

Important APIs/types/functions: global flags for rate, duration, stats, loopback, debug, work-conserving, no-CN, and EDT mode; `prog_load`, `run_bpf_prog`, `read_trace_pipe2`, `do_error`, `Usage`, and `main`. Uses libbpf object loading, cgroup helper APIs, `bpf_program__attach_cgroup`, `bpf_link__pin`, `queue_stats` map updates/lookups, tracefs, and `/sys/class/net/eth0/statistics/tx_bytes`.

Control flow: parses options, selects `hbm_out_kern.o` or `hbm_edt_kern.o`, loads the BPF object, finds the egress program and stats map, creates/joins `/hbmN` cgroup, initializes `queue_stats`, attaches and pins the cgroup link, sleeps or dynamically adjusts rate in work-conserving mode, writes final stats to `hbm.N.out`, optionally reads trace pipe, then destroys link/object and closes the cgroup FD.

State and persistence: creates cgroup state, pinned bpffs link `/sys/fs/bpf/hbmN`, and stats/log files. Queue state and stats live in BPF maps while loaded. Cgroup environment cleanup occurs only on error; successful runs intentionally leave pinned link state for the script or user to clean.

Dependencies and integration: pairs with `hbm_out_kern.c`, `hbm_edt_kern.c`, `hbm.h`, `hbm_kern.h`, and selftest cgroup helpers. Requires cgroup v2/BPF cgroup support, bpffs, tracefs for debug, libbpf, root privileges, and often `do_hbm_test.sh`.

Risks: work-conserving mode hardcodes `eth0`. Successful path pins links and may leave persistent state. Rate conversion multiplies by 1.024 and then by 128 in the BPF side, so units need careful interpretation. Debug trace reader loops forever after stats.

Test signals: run with `-s -t N` and verify `hbm.N.out`, check cgroup link pin existence, run `--edt` variant, validate cleanup through harness, and compare measured throughput/drop/mark rates.

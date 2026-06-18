
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/l4lb_all.c

## Purpose

`l4lb_all.c` validates three L4 load-balancer BPF object variants: inline, noinline, and noinline dynptr.

## Important APIs, Types, and Functions

The harness uses `bpf_prog_test_load()` for sched_cls programs, `bpf_find_map()`, `bpf_map_update_elem()`, `bpf_map_lookup_elem()`, `bpf_prog_test_run_opts()`, packet fixtures `pkt_v4`/`pkt_v6`, and per-CPU stats sized by `bpf_num_possible_cpus()`.

## Control Flow and Data Flow

For each object file, it configures `vip_map`, `ch_rings`, and `reals`, runs IPv4 and IPv6 packets for `NUM_ITER`, checks `TC_ACT_REDIRECT`, output sizes, and magic marker, then sums per-CPU `stats` bytes/packets and checks totals for both packet families.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is BPF maps for VIPs, consistent-hash rings, real servers, output packet buffer, and stats. Dependencies include the three BPF object files and sched_cls test-run support. Integration is packet rewriting/load-balancer logic and dynptr parity. Risks are object/map name drift and per-CPU stats aggregation mistakes. Test signals are redirect retval 7, IPv4 output size 54, IPv6 output size 74, expected magic value, and aggregate bytes/packets equal to `MAGIC_BYTES * NUM_ITER * 2` and `NUM_ITER * 2`.

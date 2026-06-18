<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/test_lwt_bpf.sh -->
# sources/distributed-fs/ceph-client/samples/bpf/test_lwt_bpf.sh

## Purpose
`test_lwt_bpf.sh` is the integration harness for lwt BPF route programs. It creates namespaces and veth devices, compiles `test_lwt_bpf.c` with topology-specific constants, installs programs on `xmit`, `out`, and `in` route hooks, and validates packet behavior and trace output.

## Important APIs, Types, And Functions
Important functions are `lookup_mac()`, `cleanup()`, `setup_one_veth()`, `install_test()`, `remove_prog()`, `get_trace()`, `match_trace()`, and test cases such as `test_ctx_xmit()`, `test_data_in()`, `test_drop_all()`, `test_rewrite()`, `test_netperf_nop()`, and `test_netperf_redirect()`.

## Control Flow
The script cleans stale state, creates two namespaces/veth pairs, starts `netserver`, enables tracing, discovers MACs and ifindex, compiles the BPF object with clang, then sequentially installs route encap BPF programs and runs pings or netperf. Each test clears trace, installs a section, validates connectivity and exact trace text, then removes the route program. Cleanup restores tracing options and deletes topology.

## State And Persistence
State includes namespaces, veth devices, routes, generated `test_lwt_bpf.o`, trace buffer contents, trace options, and a `netserver` process in `NS1`. Cleanup removes most state and restores the saved trace context option.

## Dependencies And Integration Points
It depends on root privileges, `clang --target=bpf`, iproute2 lwt BPF support, `/sys/kernel/tracing`, ping, netperf/netserver, and the companion C source.

## Risks And Edge Cases
The script uses `set -ex` after setup but no global trap, so early failures can leave topology or tracing changed. Exact trace matching is brittle across kernel formatting changes. `killall netserver` in a namespace assumes process name availability. Netperf is optional on many systems.

## Test Signals
All named tests must complete, trace output must match expected lines, ping failures must occur only in drop/corrupt cases, netperf must succeed for nop and redirect, and final exit status must be zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/test_lwt_bpf.sh -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_nf.c

## Purpose
This selftest validates BPF netfilter connection-tracking kfunc behavior for XDP and TC/SKB programs, including successful allocation, insertion, lookup, NAT/status/timeout mutation, zone handling, and expected verifier failures for invalid kfunc usage.

## Important APIs, Types, And Functions
Important elements include `test_bpf_nf_fail_tests`, `connect_to_server()`, `test_bpf_nf_ct()`, `test_bpf_nf_ct_fail()`, and `test_bpf_nf()`. It uses `iptables-legacy` to enable conntrack, `start_server()`, `connect_fd_to_fd()`, `accept()`, `bpf_prog_test_run_opts()`, verifier log buffers via `bpf_object_open_opts`, `bpf_object__find_program_by_name()`, and skeletons `test_bpf_nf` and `test_bpf_nf_fail`.

## Control Flow
`test_bpf_nf()` runs two positive subtests, one with the XDP program and one with the TC/SKB program. `test_bpf_nf_ct()` checks for `iptables-legacy`, loads the skeleton, adds a raw-table CONNMARK rule to enable conntrack, creates a loopback TCP connection, stores tuple fields in BSS, runs the selected program with `pkt_v4`, and verifies BSS/data results. It then removes the iptables rule and destroys resources. Negative subtests autoload one invalid program at a time and assert load failure plus an expected verifier-log substring.

## State And Persistence Behavior
The test temporarily mutates the system's iptables raw PREROUTING chain, opens TCP sockets, and uses skeleton BSS/data to hold tuple fields and result codes. The iptables rule is removed on exit from the positive test path. Verifier log state is held in a static 1 MiB buffer.

## Dependencies And Integration Points
It depends on `iptables-legacy`, conntrack support, IPv4 TCP sockets, BPF kfunc support for netfilter conntrack, XDP and SCHED_CLS program execution through test-run APIs, and selftest packet fixtures such as `pkt_v4`.

## Risks And Edge Cases
The test is environment-sensitive because missing `iptables-legacy` causes skip and rule cleanup relies on command execution. Timeout and ct timeout assertions allow a narrow range, so slow systems can be noisy. Negative tests depend on exact verifier diagnostic substrings.

## Test Signals
Positive pass signals include expected errno results for invalid options, successful new and existing conntrack lookups, timeout/status changes, mark values, NAT operations, and zone-specific lookup behavior. Negative pass signals are load failure and matching verifier messages for each invalid kfunc pattern.

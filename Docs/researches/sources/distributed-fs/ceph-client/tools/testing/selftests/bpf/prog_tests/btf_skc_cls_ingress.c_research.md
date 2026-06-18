# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_skc_cls_ingress.c

## Purpose
This network integration test validates BTF-enabled access to socket/kernel TCP state from a TC ingress classifier, including regular connection paths and SYN cookie generation/receipt paths for IPv4, IPv6, and dual-stack listeners.

## APIs, Types, and Functions
It uses `test_btf_skc_cls_ingress.skel.h`, libbpf TC APIs (`bpf_tc_hook_create`, `bpf_tc_attach`), netns helpers, socket helpers (`start_server`, `connect_to_fd`, `v6only_true`, `v6only_false`), and sysctl writes for TCP options. Key helpers are `prepare_netns`, `reset_test`, `print_err_line`, `run_test`, and small wrappers for six subcases.

## Control Flow
The test opens and loads the skeleton, creates a dedicated network namespace, attaches the classifier to loopback ingress, enables TCP options required for syncookie helper behavior, and then iterates through connection and syncookie subtests. `run_test` sets syncookie mode, starts a server with the requested address family, copies server addresses into BPF BSS, connects a client, accepts it, and validates BSS observations: listen socket port, request socket port, generated/received cookie equality, and MSS bounds.

## State, Dependencies, and Integration
State spans a temporary network namespace, TC qdisc/filter on loopback, sysctls inside the namespace, sockets, and skeleton BSS. Cleanup is via netns destruction and skeleton destruction. It depends on CAP_NET_ADMIN-like privileges, syncookie support, IPv6, loopback, and BTF field compatibility with the BPF program.

## Risks and Test Signals
Signals are BSS counters and socket observations. Risks include namespace/sysctl setup failures, kernel TCP behavior changes, missing helper support, and asynchronous network behavior that can obscure BPF-side field access errors.

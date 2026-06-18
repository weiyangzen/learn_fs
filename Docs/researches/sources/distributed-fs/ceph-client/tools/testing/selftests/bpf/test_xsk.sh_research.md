<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_xsk.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_xsk.sh

## Purpose
`test_xsk.sh` orchestrates AF_XDP selftests using `xskxceiver` over either generated veth pairs or a user-provided physical interface. It validates prerequisites, creates topology, runs softirq and busy-poll test suites, and reports aggregate status.

## Important APIs, Types, And Functions
- It sources `xsk_prereqs.sh`, which supplies `validate_root_exec`, `validate_veth_support`, `validate_ip_utility`, `exec_xskxceiver`, `cleanup_exit`, `cleanup_iface`, and `test_status`.
- Options support verbose mode, physical interface (`-i`), debug topology-only mode (`-d`), mode selection (`-m skb|drv|zc`), list tests (`-l`), selected test (`-t`), and help (`-h`).
- `setup_vethPairs()` creates randomized veth names, disables IPv6 if present, optionally configures busy-poll sysctls, sets MTU, and brings both links up.
- `ctrl_c()` cleanup handles interrupts.

## Control Flow
The script validates `/dev/urandom`, generates veth names, handles list/help early exits, validates privileges and veth/ip support unless a physical interface is supplied, builds `ARGS`, reports prerequisite status, optionally exits after printing debug interface arguments, runs `exec_xskxceiver` for a softirq pass, cleans up or resets the physical interface, enables busy-poll mode, recreates veths if needed, runs `exec_xskxceiver` again, cleans up, and prints a summary from `statusList`.

## State And Persistence
External state includes veth pairs, physical interface MTU/config changes, busy-poll sysfs knobs, AF_XDP sockets and UMEM created by `xskxceiver`, and arrays populated by prerequisite helpers. Cleanup is split between generated veth and physical interface paths.

## Dependencies And Integration Points
It depends on `xsk_prereqs.sh`, `xskxceiver`, root/CAP_NET_ADMIN, veth or physical NIC support, `/dev/urandom`, `ip`, sysfs network knobs, and kernel AF_XDP support.

## Risks And Edge Cases
Random veth suffix generation can produce collisions, though unlikely. The script assumes helper variables like `busy_poll`, `statusList`, `nameList`, and `XSKOBJ` are defined by the sourced prereq file. Physical-interface mode can disturb a real NIC and needs robust cleanup. The initial `retval=$?` before status reporting reflects the previous setup path, so helper behavior matters.

## Test Signals
Success prints `All tests successful!`; failures are collected in `statusList` and reported through `test_status`, with final nonzero exit when any suite failed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_xsk.sh -->

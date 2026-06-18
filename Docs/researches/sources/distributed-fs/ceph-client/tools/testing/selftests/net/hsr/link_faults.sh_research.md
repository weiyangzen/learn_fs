# sources/distributed-fs/ceph-client/tools/testing/selftests/net/hsr/link_faults.sh

## Purpose

This selftest validates HSRv0, HSRv1, and PRP resilience under clean operation, a live link cut, packet loss, high packet loss, and packet reordering. It uses rapid pings to verify zero packet loss and bounded duplicate delivery during fault recovery.

## Important APIs, Types, and Functions

The script sources `../lib.sh` and defines `setup_hsr_topo`, `setup_prp_topo`, `wait_for_hsr_node_table`, `setup_topo`, `check_ping`, `test_clean`, `test_cut_link`, `test_packet_loss`, `test_reordering`, protocol-specific wrappers, and `cleanup`. It uses `ip link add type hsr`, veth, `tc netem`, debugfs HSR node tables, and `tests_run`.

## Control Flow

`tests_run` executes all protocol/fault combinations in `ALL_TESTS`. Each test creates a fresh topology, waits for HSR node table merge when needed, injects the fault if any, runs `check_ping` from node1 to node2 with 400 pings at 10 ms intervals, parses duplicate and loss counts, and logs the result. Cleanup removes namespaces between tests through the exit trap and `pre_cleanup` behavior in the harness.

## State and Persistence Behavior

State is temporary namespaces, veth links, HSR/PRP devices, IPv4 addresses, debugfs observations, and netem qdiscs on selected links. Fault tests add delay/loss/reorder qdiscs or bring one link down during ping.

## Dependencies and Integration Points

It depends on HSR, PRP mode through `proto 1`, veth, `tc netem`, debugfs HSR node table, and kselftest logging. It integrates with kernel duplicate discard, supervision table merging, and redundant path failover.

## Risks and Edge Cases

`check_ping` parses human ping output for duplicates and packet loss. The accepted duplicate threshold is 40 for impairment tests and 0 for clean/cut-link tests. Timing is important: the fault is injected two seconds into a five-second ping run, and netem delay must create a queue for reordering.

## Test Signals

Passing signals are zero packet loss for all tests, duplicates not exceeding the configured threshold, and successful node table merge before HSR tests proceed.

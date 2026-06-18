# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/hw_stats_l3_gre.sh

Purpose: Tests L3 hardware stats over GRE tunnel traffic.

Important APIs/functions: `setup_prepare()`, `cleanup()`, `ping_ipv4()`, `send_packets_ipv4()`, `test_stats()`, `test_stats_tx()`, `test_stats_rx()`, GRE tunnel setup, and forwarding helper assertions.

Control flow: It prepares a GRE-capable topology, verifies IPv4 reachability, sends GRE-encapsulated packets, and checks L3 hardware stat counters for TX and RX directions.

State and persistence: Creates GRE tunnel interfaces/routes/stat config and removes them in cleanup.

Dependencies and integration points: Requires GRE, hardware L3 stats support, forwarding libs, and IPv4 connectivity.

Risks and test signals: Failures indicate stats accounting issues for tunneled packets or GRE offload/stat integration problems.

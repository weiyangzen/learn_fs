<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/vxlan_ipv6.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/vxlan_ipv6.sh

Purpose: IPv6 wrapper and override layer for the general mlxsw VXLAN sanitization/offload suite.

Important functions/APIs: sets IPv6 address family, local IPs, prefix length, UDP zero-checksum flags, multicast IP, and `IP_FLAG=-6`; overrides `sanitization_single_dev_learning_enabled_ipv6_test` and `sanitization_single_dev_udp_checksum_ipv6_test`; sources `vxlan.sh`.

Control flow: base suite runs with IPv6 parameters. The wrapper changes learning-enabled behavior to expected failure and tests both missing RX and missing TX zero-checksum flags.

State/dependencies: inherited from `vxlan.sh`, with IPv6 route/FDB semantics. Risks are source-order coupling and differing IPv6 offload constraints. Test signals are base VXLAN logs plus IPv6-specific sanitization failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/vxlan_ipv6.sh -->

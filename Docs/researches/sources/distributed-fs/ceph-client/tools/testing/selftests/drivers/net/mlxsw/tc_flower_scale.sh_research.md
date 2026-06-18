<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/tc_flower_scale.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/tc_flower_scale.sh

Purpose: generic mlxsw scale-test module for offloaded flower rules. It is intended to be sourced by architecture-specific resource-scale runners that provide target counts.

Important functions/APIs: `TC_FLOWER_NUM_NETIFS`, setup/cleanup hooks `tc_flower_setup_prepare`, `tc_flower_cleanup`, address generator `tc_flower_addr`, batch writer `tc_flower_rules_create`, internal `__tc_flower_test`, public `tc_flower_test`, and `tc_flower_traffic_test`.

Control flow: setup initializes two interfaces with clsact qdiscs. The test writes a temporary tc batch with one IPv6 destination flower drop rule per count, runs `tc -b`, verifies insertion outcome based on `should_fail`, counts `in_hw` entries from JSON, and optionally sends traffic to logarithmically sampled rule indices.

State/dependencies: temporary batch file, clsact qdiscs, flower filters, and VRF state. Risks include temp file cleanup only if variable exists, address/priority count limit 65536, parsing `in_hw`, and offload check dependency. Test signals are batch insertion status, offloaded rule count, and traffic counter hits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/tc_flower_scale.sh -->

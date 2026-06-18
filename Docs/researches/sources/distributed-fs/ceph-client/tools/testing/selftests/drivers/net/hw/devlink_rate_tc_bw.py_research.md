# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/devlink_rate_tc_bw.py

Purpose: Hardware test for devlink rate traffic-class bandwidth distribution through a switchdev/SR-IOV VF, VLAN priorities, and optional mqprio TC mapping.

Important APIs/functions: `BandwidthValidator`, `setup_vf()`, `setup_vlans_on_vf()`, `get_vf_info()`, `setup_bridge()`, `setup_devlink_rate()`, `setup_remote_vlans()`, `setup_test_environment()`, `measure_bandwidth()`, `run_bandwidth_test()`, `calculate_bandwidth_percentages()`, `verify_total_bandwidth()`, `run_bandwidth_distribution_test()`, `test_no_tc_mapping_bandwidth()`, `test_tc_mapping_bandwidth()`, `DevlinkFamily`, and `Iperf3Runner`.

Control flow: `main()` discovers the PCI device for the test NIC, initializes validators for total 1 Gbps and 20/80 TC split, then runs no-mapping and mapping cases. Setup enables switchdev, creates one VF, optionally adds mqprio, creates VLAN 101/102 mapped to TC3/TC4, locates the representor, bridges uplink and representor, configures devlink rate `tx_max` and `rate-tc-bws`, mirrors VLANs on the remote endpoint, then runs two parallel iperf3 measurements and validates distribution.

State and persistence: Disruptively changes eswitch mode, `sriov_numvfs`, bridge membership, VLAN devices, mqprio, and devlink rate state. Cleanup is via `defer()`.

Dependencies and integration points: Requires PCI NIC with switchdev/SR-IOV/devlink-rate support, remote endpoint, iperf3, VLAN, bridge, mqprio, and devlink Netlink family.

Risks and test signals: Highly hardware-specific. The mlx5 no-mapping behavior is expected-fail aware. Failures show rate API, representor discovery, TC mapping, bandwidth enforcement, or measurement regressions.

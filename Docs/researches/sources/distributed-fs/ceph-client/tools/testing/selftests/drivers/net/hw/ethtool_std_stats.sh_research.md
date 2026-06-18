# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/ethtool_std_stats.sh

Purpose: Tests standard ethtool counter groups for Ethernet control, MAC, and pause statistics.

Important APIs/functions: `traffic_test()`, `test_eth_ctrl_stats()`, `test_eth_mac_stats()`, `test_pause_stats()`, `setup_prepare()`, `check_ethtool_counter_group_support`, ethtool stats group queries, and forwarding traffic helpers.

Control flow: After setup, the script checks counter group support, sends traffic, reads relevant ethtool standard stat groups, and verifies expected counters increase or remain sane for control/MAC/pause categories.

State and persistence: Uses live interface counters and temporary forwarding topology. No persistent file state.

Dependencies and integration points: Requires ethtool standard statistics groups and two connected test interfaces.

Risks and test signals: Failures identify missing or incorrect standard stat reporting, pause frame accounting, or traffic counter regressions.

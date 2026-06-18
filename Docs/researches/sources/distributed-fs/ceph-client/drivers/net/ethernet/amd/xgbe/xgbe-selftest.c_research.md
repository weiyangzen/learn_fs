# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-selftest.c

## Purpose
`xgbe-selftest.c` implements ethtool offline self-tests for MAC loopback, PHY loopback, split-header operation, and jumbo frame loopback. It sends synthetic packets through the netdev and validates they return with expected headers and payload markers.

## Important APIs, Types, And Functions
- `struct xgbe_test` describes each test name, loopback mode requirement, and callback.
- `xgbe_test_loopback_validate` is a packet handler that validates Ethernet/IP/TCP/UDP fields and `NET_TEST_PKT_MAGIC`.
- `__xgbe_test_loopback` registers a temporary packet handler, creates a test SKB with `net_test_get_skb`, transmits via `dev_direct_xmit`, and waits for completion.
- `xgbe_test_mac_loopback`, `xgbe_test_phy_loopback`, `xgbe_test_sph`, and `xgbe_test_jumbo` implement individual tests.
- `xgbe_selftest_run` is the ethtool self-test entry point.
- `xgbe_selftest_get_strings` and `xgbe_selftest_get_count` supply ethtool test metadata.

## Control Flow
ethtool calls `xgbe_selftest_run` through `xgbe-ethtool.c`. The function requires offline mode and link carrier. It waits briefly for queues to drain, then for each test enables PHY loopback or MAC loopback as required, runs the test callback, stores the result in the ethtool buffer, marks overall failure for real failures, and disables loopback. Loopback validation completes a per-test completion when the expected packet is observed.

## State And Persistence
The file uses a static `xgbe_test_id` incremented per generated packet during a test run. Each loopback has temporary `net_test_priv` state, a completion, and a temporary packet handler. It observes driver state such as `pdata->sph`, `rx_split_header_packets`, `rx_buf_size`, netdev address, and optional `phydev`.

## Dependencies And Integration Points
This file depends on Linux networking selftest helpers, packet handlers, PHYLIB loopback APIs, MAC loopback helpers from elsewhere in the driver, and ethtool test plumbing in `xgbe-ethtool.c`.

## Risks
Tests are intrusive and only support offline mode. They require carrier and may fail if external PHY loopback is unsupported. Temporary packet handlers must be removed on all paths. `dev_direct_xmit` return semantics and packet ownership are important; the code cleans local test state but relies on networking helpers for SKB lifecycle after transmit. Split-header and jumbo tests depend on current driver feature/configuration state.

## Test Signals
Run `ethtool --test <dev> offline` with link up. Confirm expected `-EOPNOTSUPP` behavior for unsupported PHY loopback, split-header test behavior with SPH enabled/disabled, jumbo behavior with large RX buffers, and no leaked packet handlers or loopback state after failure.

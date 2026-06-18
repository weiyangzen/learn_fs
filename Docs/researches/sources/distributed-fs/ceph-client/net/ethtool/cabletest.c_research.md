# sources/distributed-fs/ceph-client/net/ethtool/cabletest.c

## Purpose
This file implements ethtool netlink actions and notification helpers for PHY cable tests and time-domain reflectometry cable tests. It lets userspace start tests and lets PHY drivers stream structured results back through multicast notifications.

## Important APIs, Types, And Functions
Request policies are `ethnl_cable_test_act_policy` and `ethnl_cable_test_tdr_act_policy`. Action handlers are `ethnl_act_cable_test()` and `ethnl_act_cable_test_tdr()`. Exported driver helpers include `ethnl_cable_test_alloc()`, `ethnl_cable_test_free()`, `ethnl_cable_test_finished()`, `ethnl_cable_test_result_with_src()`, `ethnl_cable_test_fault_length_with_src()`, `ethnl_cable_test_amplitude()`, `ethnl_cable_test_pulse()`, and `ethnl_cable_test_step()`.

## Control Flow
The start handlers parse a PHY-aware ethtool header, take `rtnl_lock()` and per-netdev ops locking, resolve the PHY, verify `ethtool_phy_ops` support, call the driver start callback inside `ethnl_ops_begin()`/`ethnl_ops_complete()`, then multicast a started notification. TDR requests additionally parse optional first/last/step/pair config with defaults and bounds. During a running test, driver callbacks allocate a notification skb, append result nests, and finally close and multicast the completed notification.

## State, Persistence, And Dependencies
Transient notification state is stored on `phydev->skb`, `phydev->ehdr`, and `phydev->nest` between allocation and finish/free. There is no durable persistence. Dependencies include PHY core types, `ethtool_phy_ops`, generic netlink multicast helpers, netdevice locking, and `phy_tdr_config`.

## Integration Points
PHY drivers call the exported helpers while implementing `start_cable_test` or `start_cable_test_tdr`. Netlink command registration in `netlink.c` wires userspace actions to these handlers. Results are consumed asynchronously by ethtool userspace through `ETHTOOL_MSG_CABLE_TEST_NTF` and `ETHTOOL_MSG_CABLE_TEST_TDR_NTF`.

## Risks
The asynchronous result buffer is finite (`SZ_16K`), so dense TDR samples can hit `-EMSGSIZE`. Drivers must balance allocation, finish, and free paths or leak/drop notification skb state. TDR validation must prevent invalid distances, zero step, unsupported pairs, and requests beyond the 150 m limit. Lock ordering with RTNL and netdev ops lock must stay consistent with other ethtool paths.

## Test Signals
Useful tests include unsupported PHY callbacks, malformed TDR config, boundary distances, all-pair and single-pair tests, notification allocation failure, oversized result streams, and driver paths that report result, fault length, pulse, amplitude, and step nests.

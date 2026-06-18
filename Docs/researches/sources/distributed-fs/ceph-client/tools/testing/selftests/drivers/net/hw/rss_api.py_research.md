
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/rss_api.py`

## Purpose
Exercises ethtool netlink RSS APIs against legacy ioctl/CLI behavior. It validates indirection table setting, hash key setting, flow-hash field configuration, input transforms, context creation/deletion, and notification delivery.

## Important APIs, Types, And Functions
- `_require_2qs()` checks at least two RX queues via sysfs.
- `_ethtool_create()` parses ethtool-created RSS context or rule IDs.
- `_ethtool_get_cfg()` converts `ethtool -n ... rx-flow-hash` text into either ioctl flag letters or netlink names.
- `test_rxfh_nl_set_*`, `test_rxfh_indir*_ntf`, `test_rxfh_fields*`, `test_rss_ctx_*` cover the public cases.

## Control Flow
`main()` creates a hardware `NetDrvEnv`, attaches `EthtoolFamily`, and runs all global `test_` functions. Tests compare netlink reads to CLI/ioctl views, intentionally trigger netlink errors, subscribe to ethtool monitor notifications, and create/delete additional RSS contexts via both netlink and CLI.

## State And Persistence
Mutates RSS indirection tables, RSS keys, flow-hash fields, input transforms, and additional RSS contexts. Most changes are paired with `defer()` resets or delete actions. Some notification tests use `--disable-netlink` CLI calls to force ioctl-originated events.

## Dependencies And Integration Points
Depends on `EthtoolFamily.rss_get()`, `rss_set()`, `rss_create_act()`, `rss_delete_act()`, notification polling, ethtool CLI, and device support for RSS contexts and flow-hash field programming. Error validation inspects `NlError` extack data.

## Risks
The flow-hash parser relies on exact ethtool text labels. Input-transform changes are config-order-sensitive, so tests explicitly restore flow-hash and transform state in a chosen order. Notification timing uses short polling windows, which can be sensitive on slow systems.

## Test Signals
Pass signals include expected netlink errors with no notification, exact RSS table/key readback, consistent netlink vs ioctl flow-hash fields, expected notification names (`rss-ntf`, `rss-create-ntf`, `rss-delete-ntf`), and EBUSY when requesting a duplicate context ID.

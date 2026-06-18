# sources/distributed-fs/ceph-client/net/ethtool/ioctl.c

## Purpose
This file implements the legacy `SIOCETHTOOL` ioctl entry point for network devices. It adapts user-space `ETHTOOL_*` command structs to `struct ethtool_ops`, PHY helpers, SFP helpers, RSS context tracking, feature toggles, devlink compatibility fallbacks, and netlink notifications.

## Important APIs, Types, And Functions
The public exports include `ethtool_op_get_link()`, `ethtool_op_get_ts_info()`, `__ethtool_get_link_ksettings()`, link-mode conversion helpers, `ethtool_virtdev_set_link_ksettings()`, `netdev_rss_key_fill()`, `ethtool_sprintf()`, `ethtool_puts()`, `dev_ethtool()`, `ethtool_rx_flow_rule_create()`, and `ethtool_rx_flow_rule_destroy()`. The main internal dispatcher is `__dev_ethtool()`, which switches on `ETHTOOL_*` commands after capability checks and driver begin/complete bracketing.

Major command families cover features, flags, link settings, driver info, string sets, RX NFC and RSS hash configuration, registers, WOL, EEE, EEPROM/module EEPROM, coalesce/ring/channel/pause parameters, self tests, stats, PHY stats/tunables, FEC, dumps, firmware flash fallback, and packet classification rule conversion.

## Control Flow
`dev_ethtool()` copies the command word, preloads flash-specific state, takes RTNL, calls `__dev_ethtool()`, then performs post-RTNL devlink fallbacks for flash updates and firmware version filling. `__dev_ethtool()` resolves the interface name, gates privileged commands with `CAP_NET_ADMIN`, locks netdev ops, performs runtime PM, checks device presence, calls optional `begin()`, dispatches to the command helper, calls `complete()`, reports feature changes, and releases locks.

Variable-length ioctl protocols are two-phase: handlers first exchange sizes/counts, allocate `kcalloc()` or `vzalloc()` buffers, call driver hooks, then copy results back. RSS handlers additionally hold `dev->ethtool->rss_lock` while validating indirection tables, hash keys, input transforms, and context xarray entries.

## State And Persistence
Most state changes are stored in the device or driver through `ethtool_ops`; ioctl state itself is transient. The file updates `dev->wanted_features`, `dev->ethtool->wol_enabled`, `dev->ethtool->rss_indir_user_size`, and `dev->ethtool->rss_ctx`. RSS contexts persist in the device ethtool xarray until removed. Module firmware flashing state is consulted through `dev->ethtool->module_fw_flash_in_progress` to block resets, module EEPROM reads, and some settings.

## Dependencies And Integration Points
The file depends on netdevice core locking, runtime PM, `ethtool_ops`, `ethtool_phy_ops`, PHY drivers, SFP buses, devlink compatibility helpers, flow dissector/offload APIs, RSS context helpers, and netlink notifications through `ethtool_notify()` and `ethtool_rss_notify()`. It is the legacy peer of `net/ethtool/netlink.c`: many successful ioctl mutations emit the same `ETHTOOL_MSG_*_NTF` notifications used by the generic netlink interface.

## Risks And Edge Cases
The ioctl ABI has many size handshakes and compatibility paths; malformed userspace buffers can return `-EFAULT`, `-EINVAL`, `-ETOOSMALL`, or silent zero-length replies depending on legacy convention. `ethtool_phys_id()` drops RTNL while blinking and uses a static `busy` flag, so only one physical identification operation can run globally. RSS context creation must unwind xarray entries on driver failure and avoid deleting busy contexts. Several legacy conversions lose high link-mode bits and warn rather than failing. `ethtool_get_dump_data()` allocates the full driver dump length even for partial user reads.

## Test Signals
Useful validation signals are ioctl ABI tests in ethtool/kselftest coverage, driver-specific ethtool selftests, RSS context create/modify/delete tests, syzkaller coverage for variable-length copy paths, and netlink monitor checks confirming ioctl mutations emit matching notifications. Focused tests should exercise compat `ethtool_rxnfc`, RSS transform validation, busy queue rejection in channel downsizing, module flashing blockers, and devlink fallback paths.

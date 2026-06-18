# sources/distributed-fs/ceph-client/net/ethtool/linkstate.c

## Purpose
This file implements netlink `LINKSTATE_GET`, reporting carrier state, PHY signal quality indicator values, extended link state/substate, and optional link-down statistics.

## Important APIs, Types, And Functions
`struct linkstate_reply_data` stores link state, SQI/SQI max, `struct ethtool_link_ext_stats`, and `struct ethtool_link_ext_state_info`. Key helpers are `linkstate_get_sqi()`, `linkstate_get_sqi_max()`, `linkstate_sqi_critical_error()`, `linkstate_sqi_valid()`, `linkstate_get_link_ext_state()`, `linkstate_prepare_data()`, `linkstate_reply_size()`, and `linkstate_fill_reply()`. `ethnl_linkstate_request_ops` registers GET handling.

## Control Flow
Preparation resolves an optional target PHY with `ethnl_req_get_phydev()`, enters driver ops, reads link with `__ethtool_get_link()`, queries SQI and SQI max while holding `phydev->lock`, and suppresses non-critical `-EOPNOTSUPP`/`-ENETDOWN` SQI failures. If the netdevice is up, it queries driver extended link state and accepts lack of data. Optional stats are initialized to `ETHTOOL_STAT_NOT_SET` and filled from PHY and netdevice hooks when `ETHTOOL_FLAG_STATS` is present.

## State And Persistence
The file is read-only. It snapshots current carrier, PHY quality, extended state, and counters into reply data without persisting anything.

## Dependencies And Integration Points
It depends on PHY driver `get_sqi`/`get_sqi_max`, device `get_link_ext_state` and `get_link_ext_stats`, `phy_ethtool_get_link_ext_stats()`, the shared netlink header policies with stats support, and link-state ioctl helper `__ethtool_get_link()`.

## Risks And Edge Cases
SQI is emitted only if both values are nonnegative and `sqi <= sqi_max`; invalid pairs are silently omitted. Critical SQI driver errors abort the whole request, while unsupported/down states are tolerated. Extended link state is queried only when `IFF_UP` is set, so down devices can report carrier false without richer reason data.

## Test Signals
Tests should cover absent PHY, valid and invalid SQI pairs, `-ENETDOWN` handling, extended state with and without substate, stats flag behavior, and interaction with explicit `phy_index` requests.

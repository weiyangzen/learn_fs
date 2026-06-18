# sources/distributed-fs/ceph-client/net/ethtool/features.c

## Purpose
This file implements ethtool netlink GET and custom SET behavior for netdevice feature bits. It reports hardware-supported, wanted, active, and never-change features and lets userspace request changes to ethtool-controllable wanted features.

## Important APIs, Types, And Functions
Important local types are `features_req_info` and `features_reply_data`. Public objects/functions are `ethnl_features_get_policy`, `ethnl_features_request_ops`, `ethnl_features_set_policy`, and `ethnl_set_features()`. Internal helpers convert between `netdev_features_t`, `u32` arrays, and `unsigned long` bitmaps, and `features_send_reply()` sends detailed SET feedback.

## Control Flow
GET snapshots `dev->hw_features`, `wanted_features`, `features`, `NETIF_F_NEVER_CHANGE`, and an all-features mask, then emits them as named bitsets. SET requires a wanted bitset, resolves the device, locks RTNL and netdev ops, snapshots active/wanted bits, parses requested value/mask, rejects attempts to change non-ethtool feature bits, merges unchanged wanted bits from the old state, updates `dev->wanted_features` constrained by `hw_features`, calls `__netdev_update_features()`, optionally replies with wanted-vs-active and active-diff bitsets, and calls `netdev_features_change()` when active features changed.

## State, Persistence, And Dependencies
Persistent state is `dev->wanted_features` and resulting `dev->features`. Dependencies include shared bitset helpers, `netdev_features_strings`, netdevice feature update internals, RTNL and netdev ops locking, and generic netlink reply helpers.

## Integration Points
The GET request uses generic `ethnl_request_ops`, while SET has a bespoke handler because it must return detailed change feedback. Legacy ioctl feature handling shares the same netdevice feature model.

## Risks
Feature bit conversions must not drop high bits when `NETDEV_FEATURE_COUNT` approaches the width of `netdev_features_t`. SET must reject non-ethtool bits or userspace could alter immutable/internal flags. The reply distinguishes requested wanted differences from actual active changes; errors there can mislead userspace about driver acceptance.

## Test Signals
Tests should cover GET compact/verbose bitsets, SET with missing wanted attr, unknown feature bits, non-ethtool bit rejection, no-op updates, wanted bits unsupported by hardware, active feature changes, omit-reply flag, and notification on active changes.

# sources/distributed-fs/ceph-client/net/ethtool/linkmodes.c

## Purpose
This file implements netlink `LINKMODES_GET` and `LINKMODES_SET`, covering autonegotiation, advertised and peer link mode bitsets, speed, duplex, lane count, master/slave configuration and state, and rate matching.

## Important APIs, Types, And Functions
`struct linkmodes_reply_data` carries `ethtool_link_ksettings`, the base link settings pointer, and a `peer_empty` flag. Important callbacks are `linkmodes_prepare_data()`, `linkmodes_reply_size()`, `linkmodes_fill_reply()`, `ethnl_auto_linkmodes()`, `ethnl_check_linkmodes()`, `ethnl_update_linkmodes()`, `ethnl_set_linkmodes_validate()`, and `ethnl_set_linkmodes()`. `ethnl_linkmodes_request_ops` registers the handlers.

## Control Flow
GET fetches ksettings under `ethnl_ops_begin()`, masks `lanes` to zero for drivers without lane support, records whether link-partner advertising is empty, computes bitset sizes with compact-bitset awareness, and emits our/peer bitsets plus scalar fields.

SET first validates master/slave values and lane power-of-two/range rules. It fetches current ksettings, applies requested autoneg, advertising bitset, speed, lanes, duplex, and master/slave configuration. If autonegotiation is enabled and userspace requested speed, lanes, or duplex without explicit advertising, `ethnl_auto_linkmodes()` rebuilds advertising from supported modes matching those constraints. Modified settings are committed through `set_link_ksettings()`.

## State And Persistence
No state is held in this file. Persistent behavior is delegated to the driver and PHY/link management. Notifications use `ETHTOOL_MSG_LINKMODES_NTF` through the generic set wrapper.

## Dependencies And Integration Points
The file depends on `bitset.h` helpers for named netlink bitsets, global `link_mode_names` and `link_mode_params`, ksettings helpers from `ioctl.c`, and driver `ethtool_ops`. It complements `linkinfo.c`: both operate on the same kernel ksettings snapshot.

## Risks And Edge Cases
Lane handling is subtle: lane configuration is allowed only as powers of two from 1 to 8 and can be rejected if autoneg is off and the driver lacks `cap_link_lanes_supported`. When autoneg is off and lanes were previously set but omitted in a new request, the code clears lanes to zero. The auto-advertising behavior intentionally emulates ioctl userspace behavior in kernel; mismatches in `link_mode_params` can select unexpected advertising masks.

## Test Signals
Tests should cover compact and verbose bitset encodings, peer bitset omission, invalid master/slave and lane values, auto-advertising when autoneg is enabled, lane clearing when autoneg is disabled, no-op SET, and notification emission.

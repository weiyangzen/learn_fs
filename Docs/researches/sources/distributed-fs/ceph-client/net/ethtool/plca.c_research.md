# sources/distributed-fs/ceph-client/net/ethtool/plca.c

## Purpose
This file implements netlink PLCA configuration and status operations for multidrop PHYs: `PLCA_GET_CFG`, `PLCA_SET_CFG`, and `PLCA_GET_STATUS`.

## Important APIs, Types, And Functions
`struct plca_reply_data` stores `struct phy_plca_cfg` and `struct phy_plca_status`. Important helpers are `plca_update_sint()`, `plca_get_cfg_prepare_data()`, `plca_get_cfg_fill_reply()`, `ethnl_set_plca()`, `plca_get_status_prepare_data()`, and `plca_get_status_fill_reply()`. `ethnl_plca_cfg_request_ops` and `ethnl_plca_status_request_ops` register the operations.

## Control Flow
GET config resolves a PHY, checks global `ethtool_phy_ops->get_plca_cfg`, enters ops, initializes all config fields to `0xff` so signed fields become `-1`, calls the PHY op, and emits only nonnegative fields. SET resolves the PHY, checks `set_plca_cfg`, initializes a config to all `-1`, updates only supplied fields with `plca_update_sint()`, returns no-op if nothing changed, otherwise calls the PHY op. GET status similarly resolves PHY, calls `get_plca_status`, and emits the boolean status.

## State And Persistence
The file holds no persistent state. SET persists through the PHY driver's PLCA configuration; GET snapshots current PHY state.

## Dependencies And Integration Points
It depends on global `ethtool_phy_ops`, PHY device resolution with optional `phy_index`, and the per-PHY dump framework. The operation is integrated into default SET and per-PHY GET dispatch in `netlink.c`.

## Risks And Edge Cases
The code uses all-ones initialization as a sentinel for unsupported fields, which relies on signed integer layout in `phy_plca_cfg`. `plca_update_sint()` uses the set policy table type at runtime; policy/table drift can trigger warnings or wrong extraction. GET status emits `!!pst` without checking a sentinel, so an uninitialized all-ones status would appear true if a driver returned success without filling it.

## Test Signals
Tests should cover field omission for `-1`, range policy enforcement, no-op SET, partial SET of individual fields, missing `ethtool_phy_ops`, explicit PHY selection, and status driver behavior on unfilled output.

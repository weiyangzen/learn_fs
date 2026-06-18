# sources/distributed-fs/ceph-client/net/ethtool/mse.c

## Purpose
This file implements netlink `MSE_GET` for PHY mean-square error diagnostics, reporting capability limits and current snapshots for supported channels.

## Important APIs, Types, And Functions
`struct mse_reply_data` stores PHY MSE capability, a dynamically allocated snapshot array, and count. Helpers include `get_snapshot_if_supported()`, `mse_get_channels()`, `mse_prepare_data()`, `mse_cleanup_data()`, `mse_reply_size()`, `mse_channel_to_attr()`, and `mse_fill_reply()`. `ethnl_mse_request_ops` registers a PHY-aware GET operation.

## Control Flow
Preparation resolves the target PHY, enters ethtool ops, locks `phydev->lock`, validates driver callbacks and link-up state, reads capabilities, and calls `mse_get_channels()`. Channel selection prefers individual A-D snapshots, then worst-channel, then link-wide snapshot. Reply filling emits a capabilities nest and one nest per selected channel with average, peak, and worst-peak values gated by capability bits.

## State And Persistence
The file is read-only. Snapshot memory is allocated per request and freed by `mse_cleanup_data()` or immediately on prepare failure.

## Dependencies And Integration Points
It depends on PHY driver callbacks `get_mse_capability()` and `get_mse_snapshot()`, PHY channel/capability enums, `ethnl_req_get_phydev()`, and the per-PHY dump machinery in `netlink.c`.

## Risks And Edge Cases
`mse_get_channels()` allocates space for four entries but can request worst or link-wide only when no individual channels were added, so the array remains bounded. If a snapshot callback fails after allocation, cleanup is split between prepare failure handling and normal cleanup. Requests fail with `-ENETDOWN` when the PHY link is down, unlike linkstate SQI which tolerates down state.

## Test Signals
Tests should cover no PHY, missing callbacks, link down, each capability priority path, mixed metric capability bits, allocation failure, invalid channel mapping, and per-PHY dump with explicit `phy_index`.

# sources/distributed-fs/ceph-client/net/ethtool/phc_vclocks.c

## Purpose
This file implements netlink `PHC_VCLOCKS_GET`, returning PTP hardware clock virtual clock indexes associated with a netdevice.

## Important APIs, Types, And Functions
`struct phc_vclocks_reply_data` stores the count and dynamically allocated index array. The callbacks are `phc_vclocks_prepare_data()`, `phc_vclocks_reply_size()`, `phc_vclocks_fill_reply()`, and `phc_vclocks_cleanup_data()`. `ethnl_phc_vclocks_request_ops` registers GET handling.

## Control Flow
Preparation enters ethtool ops, calls `ethtool_get_phc_vclocks(dev, &index)`, stores the returned count and pointer, and completes ops. Reply sizing and filling emit nothing when the count is non-positive; otherwise they emit count and the signed index array. Cleanup frees the array.

## State And Persistence
The file is read-only. The index array is per-request heap state freed after reply generation.

## Dependencies And Integration Points
It depends on the time-stamping/PTP helper `ethtool_get_phc_vclocks()` and the common netlink request framework. It is adjacent to, but separate from, timestamp information handlers.

## Risks And Edge Cases
Negative returns from `ethtool_get_phc_vclocks()` are stored in `num` and cause an empty successful reply because `phc_vclocks_prepare_data()` returns the earlier `ethnl_ops_begin()` status rather than propagating `num`. If the helper uses negative errno to signal failure, this file masks it.

## Test Signals
Tests should cover devices with zero, one, and multiple virtual clocks, allocation failure in the helper, negative helper returns, and cleanup after partial reply failure.

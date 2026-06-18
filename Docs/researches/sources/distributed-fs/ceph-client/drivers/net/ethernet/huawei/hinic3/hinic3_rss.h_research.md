
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_rss.h

## Purpose
`hinic3_rss.h` exposes the RSS lifecycle API for the hinic3 NIC driver.

## Important APIs, Types, And Functions
- `hinic3_rss_init()` enables/programs RSS for an active netdev.
- `hinic3_rss_uninit()` disables RSS on teardown.
- `hinic3_try_to_enable_rss()` performs capability/resource setup and queue-count selection.
- `hinic3_clear_rss_config()` frees RSS key and indirection arrays.

## Control Flow
Higher-level probe/configuration code calls `hinic3_try_to_enable_rss()` before queue allocation so `q_params.num_qps` is set. Interface open calls `hinic3_rss_init()` to enable hardware RSS; close/unload calls `hinic3_rss_uninit()` and eventually `hinic3_clear_rss_config()`.

## State And Persistence Behavior
The header has no state. It declares functions that mutate `struct hinic3_nic_dev` fields via `netdev_priv()`.

## Dependencies And Integration Points
It includes `linux/netdevice.h` and integrates with hinic3 netdev setup code.

## Risks And Edge Cases
The API ordering matters: clearing RSS config before uninit/init users finish would leave null key/indir pointers. Queue allocation should consume the post-RSS `num_qps` value.

## Test Signals
Build coverage for all call sites and runtime open/close with RSS enabled/disabled are the main signals.

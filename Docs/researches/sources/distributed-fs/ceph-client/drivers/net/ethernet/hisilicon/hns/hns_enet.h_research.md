# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_enet.h

## Purpose

`hns_enet.h` declares the shared netdev-private structures, state bits, per-ring NAPI wrapper, version-specific descriptor operation hooks, and exported helper prototypes for the HNS Ethernet driver.

## Important APIs, Types, And Functions

`enum hns_nic_state` defines serialized driver state and service flags: testing, resetting, reinitializing, down, disabled, removing, service initialized/scheduled, and reset requested. `struct hns_nic_ring_data` binds one `hnae_ring` to a NAPI object, IRQ affinity mask, queue index, poll callback, optional packet post-processing callback, and completion callback. `struct hns_nic_ops` abstracts descriptor fill, TX stop checks, and RX buffer-count parsing across hardware versions. `struct hns_nic_priv` is the netdev private state, carrying firmware node, version, port/PHY data, netdev/device, AE handle, ops, ring-data array, link cache, timeout count, state bits, service timer/work, and HNAE notifier.

Macros `tx_ring_data` and `rx_ring_data` index the split ring-data array. Exported prototypes include ethtool setup, reset/reinit, PHY init, and raw TX submission used by loopback tests.

## Control Flow

The header has no executable control flow, but it defines the object model used by `hns_enet.c` and `hns_ethtool.c`. TX rings occupy the first half of `ring_data`; RX rings occupy the second half. Version-specific callbacks are installed during AE handle acquisition and then used by the TX/RX data path.

## State And Persistence

All persistent netdev instance state is represented by `hns_nic_priv`. The `state` bitmap gates lifecycle concurrency, self-tests, resets, and service scheduling. `phy_led_val` stores LED state during identify operations. `link` caches most recent link state for ethtool and service polling.

## Dependencies And Integration Points

The header includes netdevice, firmware-node network helpers, MDIO/PHY, timer, workqueue, and `hnae.h`. It is shared by the netdev implementation and ethtool implementation, so structure fields must remain consistent across both files.

## Risks And Test Signals

Risks include incorrect ring-data indexing, state-bit misuse that blocks open/close/reset, and mismatched callback signatures between versions. Test signals include successful compile, correct TX/RX queue counts, ethtool self-test access to `hns_nic_net_xmit_hw`, and clean reset/service behavior under concurrent timeout, close, and remove paths.

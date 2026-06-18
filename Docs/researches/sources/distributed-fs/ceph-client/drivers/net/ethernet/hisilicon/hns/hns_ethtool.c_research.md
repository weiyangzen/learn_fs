# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_ethtool.c

## Purpose

`hns_ethtool.c` implements the ethtool interface for the HNS netdev driver. It exposes link settings, driver info, ring and pause parameters, interrupt coalescing, channels, self-tests, stats, strings, LED identification, register dumps, autoneg restart, RSS get/set, and RX ring count.

## Important APIs, Types, And Functions

The only exported function is `hns_ethtool_set_ops`, which assigns a static `struct ethtool_ops`. Important helpers include `hns_nic_get_link`, `hns_get_mdix_mode`, get/set link ksettings, loopback setup/up/run/down helpers, `hns_nic_self_test`, driver info, ringparam, pause get/set, coalesce get/set, channels, ethtool stats and strings, string-set count, PHY LED state handling, register dump accessors, nway reset, RSS key/indir sizing, RSS get/set, and RX ring count.

## Control Flow

Link queries combine cached driver link, PHY status, and AE `get_status`. Link setting validates interface mode: XGMII only allows fixed 10G full duplex without autoneg, SGMII delegates to PHY when present or validates 10/100/1000 speeds otherwise, then calls AE `adjust_link` if available.

Offline self-test sets the testing state, closes the device if running, iterates supported MAC/SerDes/PHY loopback modes, resets hardware, enables loopback, starts hardware, adjusts link, transmits a crafted skb through ring 0, polls RX/TX rings manually, records failures, disables loopback, resets, clears testing, and reopens if needed. Online tests are not actively run.

Stats flow updates AE stats, copies standard rtnl stats plus timeout count, then appends AE-specific stats. String flow mirrors that layout: standard netdev names first, then AE strings. Coalescing requires equal TX/RX usecs, optionally toggles adaptive coalescing, and delegates usec/frame programming to AE ops. RSS is rejected on v1 and delegated to AE ops on newer hardware, with only no-change or Toeplitz hash function accepted.

## State And Persistence

This file mutates netdev private state only for testing flags, adaptive coalesce enable, and stored PHY LED value. Most persistent settings are delegated to PHY or AE hardware ops: link mode, pause, coalesce, RSS, LED state, and loopback. It reads counters from netdev, rings, PPE/RCB/MAC via AE callbacks.

## Dependencies And Integration Points

It depends on Linux ethtool, PHY/MDIO, netdev stats, and the HNS private structures from `hns_enet.h`. It is a user-facing facade over `hnae_ae_ops`, `hns_nic_net_reset`, `hns_nic_net_xmit_hw`, and PHY helpers.

## Risks And Test Signals

Risks include PHY page not restored after MDIX/LED operations on errors, self-test interactions with live close/open and reset, RSS operation calls without validating optional AE ops, stale or mismatched stat/string counts, and strict coalesce validation rejecting useful asymmetric settings. Test signals include `ethtool -i`, `-k`, `-S`, `-d`, `-c/-C`, `-a/-A`, `-l`, `-t offline`, `-x/-X`, physical identify LED behavior, link setting validation, and no test-state leakage after failed loopback.

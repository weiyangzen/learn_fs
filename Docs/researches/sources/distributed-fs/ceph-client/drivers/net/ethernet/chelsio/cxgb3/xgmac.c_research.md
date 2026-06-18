# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/xgmac.c

## Purpose
This file implements cxgb3 XGMAC control for Chelsio T3 adapters: MAC/SERDES reset, exact and hash address filters, MTU and flow-control programming, Tx/Rx enable/disable, watchdog recovery, and RMON statistics accumulation.

## Important APIs, Types, And Functions
- `t3_mac_reset()` and `t3b2_mac_reset()` reset MAC/PCS/RGMII/XAUI/XG2G blocks, initialize receive config, and apply revision-specific workarounds.
- `t3_mac_set_address()`, `t3_mac_set_num_ucast()`, `t3_mac_set_rx_mode()`, and exact-filter enable/disable helpers program unicast/multicast reception.
- `t3_mac_set_mtu()` updates frame size, drains Rx FIFO when needed, recalculates pause watermarks, and adjusts Tx FIFO thresholds.
- `t3_mac_set_speed_duplex_fc()` programs port speed and pause-frame behavior.
- `t3_mac_enable()`, `t3_mac_disable()`, `t3b2_mac_watchdog_task()`, and `t3_mac_update_stats()` control data path activation, hang recovery, and counter rollup.

## Control Flow
Reset begins with register clears and FIFO/SERDES setup, then selects the appropriate reset bits based on 10G, XAUI, or RGMII mode. The B2 reset path temporarily disables MPS traffic, drains hardware, changes drop config, resets, and restores state. Rx mode first toggles promiscuous copy-all, then reserves exact filters for multicast entries and hashes overflow entries. MTU changes program max frame size directly unless Rx is active on newer revisions, where filters are disabled and FIFO drain is required before updating. The watchdog compares software and hardware Tx progress counters, toggles Tx on short stalls, and escalates to `t3b2_mac_reset()` after repeated failures.

## State And Persistence
State is in hardware registers plus cached fields in `struct cmac`: `nucast`, `txen`, watchdog counters (`tx_mcnt`, `tx_tcnt`, `tx_xcnt`, `rx_mcnt`, `rx_pause`, `rx_xcnt`, `rx_ocnt`, `toggle_cnt`), and accumulated `mac_stats`. RMON hardware counters are clear-on-read or limited width, so periodic accumulation is required.

## Dependencies And Integration Points
The implementation depends on `common.h`, `regs.h`, adapter revision/capability helpers (`uses_xaui`, `is_10G`), register access helpers, netdevice multicast lists, and Linux netdev flags. It integrates with cxgb3 port setup, ethtool statistics, multicast configuration, MTU changes, and watchdog scheduling.

## Risks
Incorrect reset sequencing can leave XAUI/PCS/RGMII blocks wedged. Active-Rx MTU changes depend on FIFO-empty polling and temporary filter changes, creating risk of dropped frames or stale filter state on errors. The B2 watchdog/reset path touches global MPS and TP drop registers and must preserve/restore them correctly. RMON counters can overflow if `t3_mac_update_stats()` is not called frequently enough.

## Test Signals
Test MTU changes with Rx enabled/disabled, promiscuous/all-multicast transitions, multicast lists beyond exact-filter capacity, speed/flow-control programming, traffic after reset on XAUI and non-XAUI adapters, and watchdog recovery under induced Tx stalls. Statistics tests should validate monotonic accumulation across 32-bit counter rollover windows.

# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hw.c

## Purpose

`hw.c` is the Wi-Fi 7 hardware-variant registry and mac80211 ops binding for ath12k. It maps hardware revisions to firmware directories, CE/MHI/WMI/HAL capabilities, ring masks, feature flags, MLO limits, interface modes, and hardware operation callbacks. It also supplies the Wi-Fi 7 `ieee80211_ops` table and TX entry point.

## Important APIs, Types, And Data

Important local callbacks translate MAC/PDEV/SRNG IDs for QCN9274 and WCN7850-style devices, choose TX rings (`smp_processor_id()` for QCN9274 and skb queue mapping for WCN7850), identify TX completion rings, and decide whether management frames are link-agnostic for MLO. The WCN7850 link-agnostic decision checks peer presence and MLO state under DP locks and excludes selected station/AP management frames such as probe/auth/deauth/association and ADDBA response.

Static ring masks describe IRQ/service masks for TX, RX, RX monitor, RX error, WBM release, REO status, host-to-RXDMA, and TX monitor rings. `ath12k_wifi7_hw_params[]` contains entries for QCN9274 hw1.0/hw2.0, WCN7850 hw2.0, QCC2072 hw1.0, IPQ5332 hw1.0, and IPQ5424 hw1.0. `ath12k_wifi7_mac_op_tx()` is the custom TX path installed in `ath12k_ops_wifi7`. `ath12k_wifi7_hw_init()` selects the matching params, assigns `ab->ath12k_ops`, initializes HAL, and logs the hardware name.

## Control Flow

Probe code in PCI/AHB sets `ab->hw_rev`, then calls `ath12k_wifi7_hw_init()`. Hardware init scans `ath12k_wifi7_hw_params[]`, fails with `-EINVAL` on an unsupported revision, stores the selected params, installs Wi-Fi 7 mac80211 ops, and calls `ath12k_wifi7_hal_init()`. TX flow enters `ath12k_wifi7_mac_op_tx()`, rejects monitor vdev TX, chooses an MLO link, handles management frames through `ath12k_mac_mgmt_tx()`, applies P2P NoA when needed, and sends normal unicast or special cases to `ath12k_wifi7_dp_tx()`. MLO multicast is copied per active link, link addresses are updated, multicast keys are looked up, protected bit is set when needed, and each copy is queued with a shared multicast GSN.

## State And Persistence Behavior

Hardware params are immutable global tables. Runtime state is stored in `ab->hw_params`, `ab->ath12k_ops`, per-vif link maps, skb control blocks, per-vif multicast sequence (`mcbc_gsn`), peer/key state, and DP locks. TX does not persist packet data beyond queued skbs, but multicast fanout creates per-link skb copies and may update frame protection bits.

## Dependencies And Integration

The file integrates mac80211/cfg80211 ops, ath12k core/CE/HAL/MHI/WMI/DP/peer/debugfs/testmode/wow layers, Wi-Fi 7 DP RX/TX helpers, and hardware-specific CE maps. Hardware params reference MHI configs from `mhi.c`, WMI init functions from `wmi.c`, ring selection functions from DP RX config files, and HAL init from local `hal.c`.

## Risks And Edge Cases

`ath12k_wifi7_mac_op_tx()` is high-risk because it runs in the TX hot path under RCU constraints. MLO link selection failure drops skbs; multicast fanout can partially fail if `skb_copy()` or per-link peer lookup fails. Lock ordering around `dp_lock` and `dp_hw.peer_lock` must remain stable. The WCN7850 link-agnostic check depends on peer lookup correctness and excludes some management frames to avoid sending them over the wrong link. Hardware parameter mismatches can manifest as wrong firmware path, CE count, MHI config, ring masks, or feature flags.

## Test Signals

Probe each supported revision and verify selected `hw_params->name`, firmware directory, CE/MHI/WMI config, and HAL register mapping. Runtime tests should cover station/AP/P2P modes, MLO unicast and multicast, encrypted multicast, probe/auth/assoc/ADDBA management frames, suspend/resume on WCN7850/QCC2072, monitor support on capable devices, and unsupported `hw_rev` failure handling.

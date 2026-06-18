# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/mac.h

## Purpose

`mac.h` is the public contract for ath12k's mac80211 integration layer. It does not implement behavior itself; it centralizes constants, small data structures, and declarations used by the driver to expose radios, links, virtual interfaces, peers, scan state, management TX, regulatory TPC, MLO, and mac80211 callbacks.

## Important APIs, Types, And Constants

- `struct ath12k_generic_iter` and `struct ath12k_mac_get_any_chanctx_conf_arg` are iterator payloads used when walking mac80211 objects.
- `enum ath12k_supported_bw`, `enum ath12k_gi`, and `enum ath12k_ltf` translate firmware rate concepts into cfg80211/mac80211 rate reporting.
- `struct ath12k_chan_power_info` and `struct ath12k_reg_tpc_power_info` model 6 GHz transmit power/TPE data that regulatory and MAC code later converts into firmware commands.
- Constants such as `ATH12K_KEEPALIVE_*`, `ATH12K_KICKOUT_THRESHOLD`, `ATH12K_SCAN_LINKS_MASK`, `ATH12K_NUM_MAX_ACTIVE_LINKS_PER_DEVICE`, and OBSS PD thresholds encode policy shared across interface, station, scan, and power code.
- Declarations cover the whole mac80211 operations surface: start/stop, add/remove interface, channel context operations, key install, STA state and link changes, AMPDU, survey, flush, remain-on-channel, TX power, management TX, and MLO multicast address handling.

## Control Flow And Integration

The file sits above lower layers. mac80211 invokes `ath12k_mac_op_*` callbacks registered by the MAC implementation; those functions call WMI, DP, peer, regulatory, PCI/HIF, and firmware-stat helpers. Driver-internal users call lookup helpers such as `ath12k_mac_get_arvif_by_vdev_id()`, `ath12k_mac_get_ar_by_vdev_id()`, and `ath12k_get_ar_by_vif()` to bind firmware vdev or link identifiers back to host objects. Regulatory code uses `ath12k_mac_update_freq_range()` and `ath12k_mac_fill_reg_tpc_info()`. P2P code exposes `ath12k_mac_add_p2p_noa_ie()` for beacon/probe-response updates.

## State And Persistence

No storage is allocated here, but the header defines shared state shapes and invariants. Link IDs distinguish default, invalid, and scan-only links. TPC structures retain per-channel power calculations in memory for later firmware programming. Many declared callbacks assume caller-held mac80211 wiphy locks, per-radio locks, or ath12k data locks in their implementations.

## Dependencies

It depends on `net/mac80211.h`, `net/cfg80211.h`, and ath12k `wmi.h`. The declarations reference core driver types (`ath12k`, `ath12k_base`, `ath12k_hw`, `ath12k_hw_group`), Linux networking types (`ieee80211_hw`, `ieee80211_vif`, `ieee80211_sta`, channel contexts), and firmware/WMI types.

## Risks And Test Signals

This is a high-blast-radius header: signature drift breaks many compilation units. Link/MLO constants must stay aligned with mac80211 limits and firmware assumptions. TPC array sizing assumes at most sixteen 20 MHz chunks for 320 MHz channels. Test signals are mainly build coverage plus runtime mac80211 smoke tests for interface creation, scanning, STA association, MLO link activation, management TX, and regulatory power updates.

# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/mac.c lines 10095-10380

## Scope And Purpose

This chunk is the final registration and unregister section of the ath10k mac80211 glue in `mac.c`. It completes `ath10k_mac_register()` by advertising firmware- and hardware-dependent `wiphy`/`ieee80211_hw` capabilities to cfg80211/mac80211, deriving regulatory state, registering the device with mac80211, and defining the unwind path for late registration failures. It also contains `ath10k_mac_unregister()`, the matching teardown entry point used by the core unregister path.

The code is not a packet-processing path. Its main job is to translate already-discovered ath10k state (`struct ath10k`, firmware feature bits, WMI service map, hardware parameters, channel/rate allocations prepared earlier in `ath10k_mac_register()`) into the public Linux wireless capability surface. After `ieee80211_register_hw()`, userspace and mac80211 can create interfaces, schedule scans, use WoWLAN, TDLS, airtime fairness, TID configuration, regulatory hints, and other features according to these advertised flags.

## Important APIs, Types, And Constants

- `int ath10k_mac_register(struct ath10k *ar)` is the registration function being completed. Earlier lines allocate 2 GHz/5 GHz channel arrays, fill supported bands, set base interface modes, antenna masks, and core `ieee80211_hw` flags. This chunk finishes feature advertisement and calls `ieee80211_register_hw()`.
- `void ath10k_mac_unregister(struct ath10k *ar)` is the public teardown function declared in `mac.h` and called from `core.c` both on registration unwind and normal core unregister.
- `struct ath10k` carries the persistent driver state: `ar->hw` points to `struct ieee80211_hw`; `ar->hw->wiphy` is the cfg80211-visible radio; `ar->wmi.svc_map` and `ar->running_fw->fw_file` describe firmware services/version; `ar->hw_params` contains chip-family capabilities; `ar->mac.sbands[]` owns dynamically duplicated channel arrays.
- `struct ath10k_vif`, `struct ath10k_sta`, and `struct ath10k_txq` are exposed to mac80211 by setting `ar->hw->vif_data_size`, `sta_data_size`, and `txq_data_size`. This lets mac80211 allocate driver-private storage for each virtual interface, station, and TXQ.
- cfg80211/mac80211 flags used here include `WIPHY_FLAG_IBSS_RSN`, `WIPHY_FLAG_AP_PROBE_RESP_OFFLOAD`, `WIPHY_FLAG_SUPPORTS_TDLS`, `WIPHY_FLAG_HAS_REMAIN_ON_CHANNEL`, `WIPHY_FLAG_HAS_CHANNEL_SWITCH`, `WIPHY_FLAG_AP_UAPSD`, `NL80211_FEATURE_*`, `NL80211_EXT_FEATURE_*`, and `ieee80211_hw_set()` capability bits.
- WMI service bits gate firmware-dependent features: `WMI_SERVICE_NLO`, `BEACON_OFFLOAD`, `TDLS`, `TDLS_EXPLICIT_MODE_ONLY`, `TDLS_WIDER_BANDWIDTH`, `TDLS_UAPSD_BUFFER_STA`, `TX_DATA_ACK_RSSI`, `HTT_MGMT_TX_COMP_VALID_FLAGS`, `REPORT_AIRTIME`, `RTT_RESPONDER_ROLE`, `TX_PWR_PER_PEER`, `PEER_TID_CONFIGS_SUPPORT`, `EXT_PEER_TID_CONFIGS_SUPPORT`, `ADAPTIVE_OCS`, `VDEV_DIFFERENT_BEACON_INTERVAL_SUPPORT`, `SPOOF_MAC_SUPPORT`, and `PER_PACKET_SW_ENCRYPT`.
- The interface-combination tables selected here (`ath10k_if_comb`, `ath10k_tlv_if_comb`, `ath10k_tlv_qcs_if_comb`, `ath10k_10x_if_comb`, `ath10k_10_4_if_comb`, `ath10k_10_4_bcn_int_if_comb`) are defined just above this chunk and constrain how many station/AP/P2P/mesh/IBSS virtual interfaces mac80211 may create.
- `ath10k_wow_init()`, `dfs_pattern_detector_init()`, `ath10k_mac_init_rd()`, `ath_regd_init()`, `ieee80211_register_hw()`, `regulatory_hint()`, and `ieee80211_unregister_hw()` are the major external calls in this chunk.

## Registration Control Flow

The chunk starts by adding remaining wireless capability advertisements:

1. IBSS RSN is always advertised at this point with `WIPHY_FLAG_IBSS_RSN`.
2. Dynamic SMPS is advertised if `ar->ht_cap_info` contains `WMI_HT_CAP_DYNAMIC_SMPS`.
3. AMPDU aggregation and hardware TX AMPDU setup are advertised if HT is enabled in `ar->ht_cap_info`.
4. Scan limits are set to `WLAN_SCAN_PARAMS_MAX_SSID` and `WLAN_SCAN_PARAMS_MAX_IE_LEN`.
5. Scheduled scan and network-detect scan limits are filled only if firmware advertises `WMI_SERVICE_NLO`; this also advertises random MAC support for network detection.

It then binds mac80211-private allocation sizes for VIF/STA/TXQ state and sets `ATH10K_MAX_HW_LISTEN_INTERVAL`. Beacon/probe-response, TDLS, Ethernet TX encapsulation offload, remain-on-channel, channel switch, AP U-APSD, AP scan, and AP channel-width-change support are all added by directly updating `wiphy` flags/features or `ieee80211_hw` flags.

The call to `ath10k_wow_init(ar)` is the first fallible call in this chunk. It is conditional internally: if the firmware image lacks `ATH10K_FW_FEATURE_WOWLAN_SUPPORT`, it returns success without enabling WoWLAN. If the feature bit is present but `WMI_SERVICE_WOW` is missing, it warns and fails with `-EINVAL`. On success it may add network-detect support when `WMI_SERVICE_NLO` is present, sets `ar->hw->wiphy->wowlan`, and marks the device wakeup-capable.

After WoWLAN, the code publishes extended capabilities. Some are unconditional within this driver version (`VHT_IBSS`, `SET_SCAN_DWELL`, `AQL`, `CQM_RSSI_LIST` later), while others depend on hardware parameters or WMI service bits:

- multicast frame registration depends on `ar->hw_params.mcast_frame_registration`;
- ACK signal reporting depends on either TX data ACK RSSI service or valid HTT management TX completion flags;
- airtime fairness depends on peer stats being enabled or firmware airtime reporting support;
- FTM responder, per-station TX power, and TID configuration depend on their matching WMI services.

For TID configuration, support is advertised per VIF and copied to per-peer support. Base attributes include no-ack, short/long retry counts, AMPDU control, TX rate, and TX rate type. Extended peer TID config support adds RTS/CTS control. If firmware lacks the base service, `ar->ops->set_tid_config` is nulled before registration so mac80211 never calls the operation.

Queue state is then declared. The driver sets `ar->hw->queues` to `IEEE80211_MAX_QUEUES`, with a comment that low-latency hardware queues are firmware-managed. The off-channel TX hardware queue is set to `IEEE80211_MAX_QUEUES - 1` because ath10k uses vdev IDs as hardware queue numbers and wants the off-channel queue outside the reachable vdev ID range.

The firmware WMI operation version drives interface-combination selection:

- `ATH10K_FW_WMI_OP_VERSION_MAIN` uses `ath10k_if_comb` and enables IBSS.
- `ATH10K_FW_WMI_OP_VERSION_TLV` uses either `ath10k_tlv_qcs_if_comb` when adaptive OCS is available, or `ath10k_tlv_if_comb` otherwise, and enables IBSS.
- `ATH10K_FW_WMI_OP_VERSION_10_1`, `10_2`, and `10_2_4` use `ath10k_10x_if_comb`.
- `ATH10K_FW_WMI_OP_VERSION_10_4` starts with `ath10k_10_4_if_comb`, but switches to `ath10k_10_4_bcn_int_if_comb` if firmware supports different beacon intervals per vdev.
- unset or max sentinel values trigger `WARN_ON(1)`, set `ret = -EINVAL`, and unwind.

The rest of registration is late capability and subsystem setup. Dynamic SAR support attaches `ath10k_sar_capa`; non-raw mode enables `NETIF_F_HW_CSUM`; DFS certified builds initialize a DFS pattern detector and keep going with only a warning if detector allocation fails. Regulatory state is derived through `ath10k_mac_init_rd()` and registered with `ath_regd_init()`. `set_coverage_class` is disabled in the copied `ieee80211_ops` table when the chipset has no hardware operation for it.

Cipher suites are exposed through a static `cipher_suites[]` table defined at the top of `ath10k_mac_register()`. The number of advertised ciphers is taken from `ar->hw_params.n_cipher_suites`, because older QCA988x/QCA6174-family chips only support the first eight entries while some later variants support the GCMP and CCMP-256 entries too. Invalid zero or too-large values are logged and coerced to eight suites.

Finally, `ar->hw->weight_multiplier` is set to `ATH10K_AIRTIME_WEIGHT_MULTIPLIER`, and `ieee80211_register_hw(ar->hw)` publishes the device. After successful mac80211 registration, the code conditionally adds AP VLAN support for firmware with per-packet software encryption, then sends a regulatory hint if both the copied world regdomain and active regulatory state are non-world domains.

## Error And Unregister Flow

The function uses three local unwind labels:

- `err_unregister` calls `ieee80211_unregister_hw(ar->hw)` and then falls through to DFS/channel cleanup. This is reached if `regulatory_hint()` fails after mac80211 registration.
- `err_dfs_detector_exit` exits the DFS detector when `CONFIG_ATH10K_DFS_CERTIFIED` is enabled and `ar->dfs_detector` is non-NULL. This handles failures after DFS initialization but before successful registration, and also the `ieee80211_register_hw()` failure case.
- `err_free` releases the dynamically duplicated 2 GHz and 5 GHz channel arrays and clears the device association with `SET_IEEE80211_DEV(ar->hw, NULL)`.

`ath10k_mac_unregister()` mirrors the successful-registration cleanup in a simpler order: unregister from mac80211, exit DFS detector if present, free both supported-band channel arrays, and clear the `ieee80211_hw` device pointer.

The wider integration in `core.c` depends on this ordering. Normal `ath10k_core_unregister()` calls `ath10k_mac_unregister()` before testmode cleanup, firmware file release, and debug unregister, and specifically before HTC/HIF shutdown so mac80211 callbacks can still submit firmware commands during unregister. Registration unwind in core also calls `ath10k_mac_unregister()` after coredump/debug/spectral/thermal/LED setup failures.

## State And Persistence Behavior

Most state in this chunk is configuration state persisted in `ar->hw`, `ar->hw->wiphy`, and driver-owned `ar` fields for the lifetime of the registered radio:

- The cfg80211-visible capability set is persisted in `wiphy` flags, feature bitmasks, extended features, interface modes, interface combinations, scan limits, scheduled-scan limits, cipher suite pointers, SAR capability pointer, and regulatory structures.
- The mac80211-private allocation contract is persisted through `vif_data_size`, `sta_data_size`, and `txq_data_size`; changing these after registration would corrupt callback expectations.
- The driver operation table (`ar->ops`) is a copied `ieee80211_ops` table. This chunk mutates it before registration by nulling unsupported callbacks (`set_tid_config`, `set_coverage_class`) so mac80211 sees only operations that the current firmware/hardware can satisfy.
- WoWLAN initialization writes `ar->wow.wowlan_support`, assigns `wiphy->wowlan`, and marks the parent device wakeup-capable. That state outlives the register call and is consumed by suspend/resume paths.
- DFS detector state is held in `ar->dfs_detector` and must be explicitly exited on unregister or failed registration after initialization.
- Regulatory state is stored in `ar->ath_common.regulatory` and associated with the `wiphy`; the later `regulatory_hint()` may trigger cfg80211 regulatory processing after the hardware is registered.
- The supported-band channel arrays were allocated earlier with `kmemdup()` and are freed here on all late failures and normal unregister.

The code does not persist state to disk or firmware NVRAM. It does, however, define the live kernel/userspace contract for the radio until unregister, and that contract controls which userspace operations cfg80211 will allow.

## Dependencies And Integration Points

This chunk is tightly integrated with mac80211 and cfg80211. `ieee80211_register_hw()` is the publication boundary: every flag and pointer must be valid before that call because mac80211 and userspace can observe the device afterward. `ieee80211_unregister_hw()` is the inverse boundary that stops mac80211 use before lower driver resources disappear.

Firmware discovery is another central dependency. `ar->wmi.svc_map`, `ar->ht_cap_info`, `ar->running_fw->fw_file.wmi_op_version`, and `ar->running_fw->fw_file.fw_features` come from earlier firmware/service-ready processing. Incorrect service bits would cause this chunk to over-advertise unsupported nl80211 features or hide working ones.

Hardware parameter tables in `core.c` feed `ar->hw_params` values such as `n_cipher_suites`, `dynamic_sar_support`, `mcast_frame_registration`, and `hw_ops->set_coverage_class`. This chunk trusts those tables, except for range-checking `n_cipher_suites`.

The DFS integration depends on `CONFIG_ATH10K_DFS_CERTIFIED` and the common ath DFS detector API. Regulatory integration depends on the ath common regulatory helpers (`ath10k_mac_init_rd()`, `ath_regd_init()`, `ath10k_reg_notifier()`, `ath_is_world_regd()`, and `regulatory_hint()`).

The source path is under `sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/`, so it is a copied Linux wireless driver source inside the broader `learn_fs` tree. The code does not directly interact with Ceph filesystem logic, but any build that includes this tree relies on these registration flags for ath10k wireless device behavior.

## Risks And Edge Cases

The highest-risk behavior is capability over-advertisement. Many flags are gated by WMI services or hardware parameters; if those inputs are wrong, cfg80211/mac80211 may expose operations that later firmware callbacks cannot execute. Risky examples include TDLS wider bandwidth, per-peer TID configuration, FTM responder, per-station TX power, ACK signal reporting, AP VLAN software interface support, and AP probe-response offload.

The AP VLAN feature is added after `ieee80211_register_hw()`. That is notable because most public `wiphy` capability setup happens before registration. If mac80211/cfg80211 expects interface mode and software-iftype masks to be complete at registration time, this ordering could be subtle. It is presumably intentional for firmware with per-packet software encryption, but any future rework should verify the timing.

Unwind must remain aligned with allocation order. Channel arrays are always freed at `err_free`, including when only one band was allocated; `kfree(NULL)` makes that safe. DFS detector exit is guarded by both config and non-NULL detector checks. A future added resource between these blocks must be placed into the correct unwind label or normal unregister will leak or double-free it.

The invalid WMI operation version path frees channel arrays and clears `SET_IEEE80211_DEV`, but does not unregister mac80211 because the hardware has not yet been registered. That separation is important: using `err_unregister` before successful `ieee80211_register_hw()` would be wrong.

`ar->ops` mutation is permanent for the lifetime of this allocated hardware object. Since `ath10k_core_create()` allocates a private copy of `ath10k_ops`, this is safe per device, but it means callbacks disabled during registration are not restored later if firmware mode or service information changes.

DFS detector initialization failure is warning-only. Registration can continue without `ar->dfs_detector`, so radar/CAC behavior in DFS-certified builds must tolerate a missing detector. Conversely, unregister must tolerate a stale non-NULL pointer only if the detector's `exit()` semantics are single-use; the current code does not clear `ar->dfs_detector` after exit.

The cipher-suite fallback silently mutates `ar->hw_params.n_cipher_suites` to eight after logging. That protects registration from bad table data, but it also hides the original invalid value for later diagnostics and may under-advertise on affected hardware.

The regulatory hint happens after mac80211 registration. If `regulatory_hint()` fails, the code unregisters hardware and tears down DFS/channel resources. Tests need to cover that late failure because it exercises the full registered-hardware unwind path.

## Test Signals

Useful test and review signals for this chunk include:

- Boot/register tests for representative firmware operation versions: MAIN, TLV without adaptive OCS, TLV with adaptive OCS, 10.1/10.2/10.2.4, 10.4 without different beacon interval support, and 10.4 with different beacon interval support. Each should verify advertised interface combinations and IBSS availability.
- Capability matrix tests or debug dumps comparing WMI service bits to visible nl80211/mac80211 features: NLO scheduled scan and network-detect random MAC, beacon/probe-response offload, TDLS and wider bandwidth, TDLS buffer STA, ACK signal support, airtime fairness, FTM responder, station TX power, TID config, scan random MAC, and AP VLAN software interface support.
- Negative registration tests for unsupported/sentinel WMI op versions, `ath10k_wow_init()` failure, `ath_regd_init()` failure, `ieee80211_register_hw()` failure, and `regulatory_hint()` failure. The expected signal is that channel arrays are freed, DFS detector exit runs only when initialized, and `SET_IEEE80211_DEV` is cleared.
- WoWLAN tests for firmware with no WoWLAN feature bit, firmware with WoWLAN feature but missing `WMI_SERVICE_WOW`, and firmware with WoWLAN plus NLO. These should verify `wiphy->wowlan`, wakeup capability, and network-detect limits.
- Cipher-suite tests for hardware parameter values 8, 11, 0, and greater than `ARRAY_SIZE(cipher_suites)`, checking that older chips do not advertise unsupported GCMP/CCMP-256 ciphers and invalid values fall back to eight.
- DFS-certified build tests ensuring registration succeeds when `dfs_pattern_detector_init()` returns NULL and unregister does not call through a NULL detector; a detector-present path should verify exactly one exit on normal unregister and on late registration failure.
- Regulatory tests that exercise WRDD/eeprom-derived regulatory state in the preceding helper, `ath_regd_init()`, world versus non-world domains, successful and failed `regulatory_hint()`, and the resulting unregister path.
- mac80211 private-data tests or compile-time checks verifying `vif_data_size`, `sta_data_size`, and `txq_data_size` match the driver-private structs used by callbacks.
- Core unregister ordering tests or audits should preserve the documented sequence from `core.c`: unregister mac80211 before stopping HTC/HIF, because mac80211 unregister may still need firmware-command callbacks to succeed.

For the research pipeline, the key artifact signal is that this chunk document is source-tree-aligned at `Docs/researches/chunks/subset-b-004720_research.md` and only covers `mac.c` lines 10095-10380. The later merge lane should reconcile it with earlier `ath10k_mac_register()` chunks that cover channel allocation, base hardware flags, and the helper definitions above this range.

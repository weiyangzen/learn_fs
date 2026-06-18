# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/wow.c

## Purpose
`ath11k/wow.c` implements mac80211 wake-on-wireless suspend, wake, resume, wakeup-source toggling, and WoW capability registration for ath11k. It translates `cfg80211_wowlan` requests into firmware WMI wake events, bitmap patterns, NLO/PNO scans, ARP/NS offload, GTK rekey offload, data filters, and keepalive configuration before suspending HIF interrupts and the bus.

## Important APIs, Types, And Functions
- `ath11k_wow_init()` publishes `wiphy_wowlan_support` when firmware advertises `WMI_TLV_SERVICE_WOW`, adjusts pattern limits for native Wi-Fi decap, adds net-detect support when `WMI_TLV_SERVICE_NLO` is present, and marks the device wake-capable.
- `ath11k_wow_op_suspend()`, `ath11k_wow_op_resume()`, and `ath11k_wow_op_set_wakeup()` are the mac80211-facing PM callbacks.
- `ath11k_wow_enable()` sends the firmware WoW enable command and waits for HTC suspend completion with retry.
- `ath11k_wow_wakeup()` sends host wakeup indication unless the hardware uses SMP2P WoW exit.
- Per-vdev setup helpers include `ath11k_vif_wow_set_wakeups()`, `ath11k_wow_set_wakeups()`, `ath11k_wow_vif_cleanup()`, `ath11k_wow_cleanup()`, `ath11k_wow_nlo_cleanup()`, `ath11k_wow_set_hw_filter()`, `ath11k_wow_protocol_offload()`, and `ath11k_wow_set_keepalive()`.
- `ath11k_wow_convert_8023_to_80211()` rewrites cfg80211 Ethernet pattern/mask input into native 802.11 header/RFC1042 layout when firmware receives native Wi-Fi frames.

## Control Flow And State Behavior
Suspend first waits for pending TX, locks `ar->conf_mutex`, stops pktlog/timers as needed, clears prior WoW events/patterns, installs requested vdev wake events and patterns, enables ARP/NS plus GTK offloads, enables hardware data filters, enables null-frame keepalive, and sends WoW enable. On success it stops shadow timers, disables IRQs, and calls `ath11k_hif_suspend()`. On failure it attempts firmware wakeup and/or cleanup before returning `1` to mac80211 for suspend failure semantics.

Resume reverses the path: HIF resume, CE/main IRQ enable, pktlog restart, firmware wakeup indication, NLO cleanup, data filter clear, protocol offload disable, and keepalive disable. If resume fails while the device was `ATH11K_STATE_ON`, it marks the device restarting and returns `1`; other states are treated as unrecoverable `-EIO`.

Runtime state is in `ar->wow`, `ab->wow.wakeup_completed`, `ab->htc_suspend`, `ab->dev_flags`, `ar->nlo_enabled`, per-vif `rekey_data`, and firmware-resident wake/offload tables. The code requires `conf_mutex` for vdev iteration and offload mutation.

## Dependencies And Integration Points
The file integrates mac80211/cfg80211 WoW APIs with ath11k WMI, HIF, DP RX pktlog, CE/DP shadow timers, core device flags, per-vif state, and Linux wakeup-source APIs. Its constants and firmware payloads come from `wmi.h`; `wow.h` supplies exported PM prototypes and local WoW state.

## Risks And Edge Cases
- The 802.3-to-802.11 pattern conversion is offset-sensitive; incorrect mask conversion or reduced limits can make wake patterns ineffective.
- Cleanup loops delete all firmware event IDs and pattern slots; partial failure can leave stale firmware wake state.
- PNO setup validates SSID/channel limits but does not fail the whole suspend path when `ath11k_wmi_wow_config_pno()` fails inside the `!ret` branch because that return is not checked after the call.
- Suspend return maps any nonzero `ret` to `1`, matching mac80211 PM semantics but losing specific errno detail.
- Native Wi-Fi decap reduces public pattern size/offset limits during init; user-space expectations depend on the advertised wiphy values.

## Test Signals
Test with `CONFIG_PM`, firmware with and without WOW/NLO service bits, magic-packet wake, disconnect wake, AP/IBSS wake events, bitmap patterns at boundary lengths and offsets, native Wi-Fi decap pattern conversion, scheduled-scan net-detect with one and two scan plans, ARP/NS and GTK rekey offload, pktlog enabled during suspend, SMP2P WoW exit hardware, HIF suspend failure paths, and resume recovery state transitions.

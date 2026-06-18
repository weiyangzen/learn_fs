# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wow.c

## Purpose

`wow.c` implements ath12k Wake-on-WLAN suspend/resume support. It translates cfg80211/mac80211 WoWLAN requests into WMI firmware configuration, prepares protocol offloads so the device can stay associated while the host sleeps, coordinates HTC/HIF suspend and wakeup handshakes, and exposes firmware-supported WoWLAN capabilities through the wiphy.

## Important APIs And Functions

- `ath12k_wow_enable()` sends WMI WoW enable, waits for HTC suspend completion, and retries up to `ATH12K_WOW_RETRY_NUM`.
- `ath12k_wow_wakeup()` sends host-wakeup indication and waits for `ab->wow.wakeup_completed`.
- `ath12k_wow_op_suspend()` is the mac80211 suspend callback: cleanup stale firmware state, program wakeups, enable protocol offloads, drain TX, set filters/keepalive, enable WoW, disable IRQs, and suspend HIF.
- `ath12k_wow_op_resume()` resumes HIF, re-enables IRQs, wakes firmware, cleans NLO/filter/protocol offloads, disables keepalive, and requests restart on recoverable resume failure.
- `ath12k_wow_convert_8023_to_80211()` converts cfg80211 Ethernet packet patterns into native-WiFi offsets/masks when firmware decap mode is native WiFi.
- `ath12k_wow_pno_check_and_convert()` validates cfg80211 net-detect scheduled-scan data and builds `struct wmi_pno_scan_req_arg`.
- `ath12k_wow_arp_ns_offload()` gathers IPv4/IPv6 addresses and programs ARP/NS response offload.
- `ath12k_gtk_rekey_offload()` enables/disables GTK rekey offload and fetches rekey info before disabling.
- `ath12k_wow_init()` populates `ar->wow.wowlan_support`, adjusts pattern limits for native WiFi, and sets `wiphy->wowlan`.

## Control Flow

Suspend runs in a fixed sequence under the wiphy lock. It first disables all existing events and deletes all possible patterns for default-link vifs. It skips P2P vdevs, then maps cfg80211 wake requests to firmware events: STA disconnect maps to deauth/disassoc/bmiss/CSA, magic packet maps to `WOW_MAGIC_PKT_RECVD_EVENT`, scheduled scan maps to PNO/NLO and `WOW_NLO_DETECTED_EVENT`, and packet patterns map to firmware bitmap patterns plus `WOW_PATTERN_MATCH_EVENT`. AP/IBSS vdevs enable management/HTT/RA-related wake events.

After wake events, suspend enables ARP/NS and GTK offload, waits for TX completion, enables hardware data filtering on STA vdevs, enables null-frame keepalive, enables WoW in firmware, disables CE/core IRQs, and calls `ath12k_hif_suspend()`. Failures unwind by clearing WoW state; if HIF suspend fails after WoW enable, the code wakes firmware before cleanup.

Resume reverses the bus/firmware path: HIF resume, IRQ enable, firmware wakeup, NLO cleanup, hardware-filter clear, ARP/NS and GTK offload disable, and keepalive disable. If an error occurs while state is `ATH12K_HW_STATE_ON`, it marks the hardware restarting and returns `1`; unexpected states return `-EIO`.

## State And Persistence Behavior

`ATH12K_FLAG_HTC_SUSPEND_COMPLETE`, `ab->htc_suspend`, and `ab->wow.wakeup_completed` synchronize asynchronous firmware handshakes. `ar->wow.wowlan_support` persists as the cfg80211 capability object. `ar->wow.max_num_patterns` controls capability and cleanup loops. `ar->nlo_enabled` remembers whether PNO was requested so resume can stop it. Per-vif rekey state decides whether GTK material is offloaded. ARP/NS address data is sampled from live netdev/vif state for each suspend.

## Dependencies And Integration Points

The file integrates cfg80211/mac80211 WoWLAN requests, ath12k WMI helpers, HIF/HTC suspend mechanics, Linux IPv4/IPv6 address state, ath12k vif lists/default links, GTK rekey state, and Linux device wakeup configuration.

## Risks

Native-WiFi pattern conversion is offset-sensitive and must stay aligned with WMI pattern limits. Current loops operate on default links and select radio 0 in callbacks, which is a limitation for richer MLO behavior. `ar->nlo_enabled` is set before PNO conversion fully succeeds, and the PNO WMI config return is not checked when enabling the NLO wake event. Resume failures can leave firmware filters/offloads inconsistent until restart. IPv6 address iteration uses `idev` locks plus RCU and must preserve address lifetime rules.

## Test Signals

Useful tests include WoW capability visibility, suspend/resume smoke, magic packet wake, disconnect wake, bitmap pattern wake in both Ethernet and native-WiFi decap modes, PNO net-detect with valid/invalid scan plans, ARP/NS response while suspended, GTK rekey across suspend, HTC suspend timeout injection, WMI command failure injection, and HIF suspend/resume failure paths.

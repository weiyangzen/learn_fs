# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/core.c

## Purpose
Shared mac80211-facing core for Realtek `rtlwifi`. It exports `rtl_ops` and implements start/stop, TX dispatch, vif lifetime, channel/bandwidth changes, RX filters, station tracking, QoS, beacon/BSS handling, TSF helpers, AMPDU, scanning, key programming, WoWLAN, RF-kill, power-sequence parsing, command TX, LEDs, BT coexistence fallback, and DIG init.

## Important APIs, Types, And Functions
Key callbacks are `rtl_op_start()`, `rtl_op_stop()`, `rtl_op_tx()`, `rtl_op_add_interface()`, `rtl_op_remove_interface()`, `rtl_op_config()`, `rtl_op_configure_filter()`, `rtl_op_bss_info_changed()`, `rtl_op_set_key()`, `rtl_op_ampdu_action()`, `rtl_op_sw_scan_start()`, and `rtl_op_sw_scan_complete()`. Exported helpers include `rtl_fw_cb()`, `rtl_wowlan_fw_cb()`, `rtl_rfreg_delay()`, `rtl_hal_pwrseqcmdparsing()`, `rtl_cmd_send_packet()`, `rtl_init_sw_leds()`, and `rtl_dm_diginit()`.

## Control Flow
mac80211 starts through `rtl_op_start()`, which serializes on `conf_mutex`, calls bus `adapter_start`, and starts watchdog work. TX checks HAL/RF/interface state, optionally queues early-mode traffic, otherwise calls `adapter_tx`. Interface add allows one vif, sets mode/P2P/basic-rate/beacon/retry/MAC state, and writes chip registers. `rtl_op_config()` handles idle IPS, SW PS, and channel width/primary-channel setup before invoking chip channel/bandwidth ops. BSS changes update security, BSSID, rates, HT settings, firmware join status, LPS, and P2P PS.

## State And Persistence
Runtime state lives in `rtl_priv`, `rtl_mac`, `rtl_hal`, `rtl_ps_ctl`, and `rtl_sec`: vif, opmode, BSSID, link state, P2P role, beacon enable, bandwidth flags, retries, firmware buffers, key buffers, encryption algorithms, and DIG thresholds. Hardware state is volatile and replayed through chip `cfg->ops`.

## Dependencies And Integration Points
Integrates mac80211/cfg80211, `base.h`, CAM security, `ps.c`, `pwrseqcmd.h`, bus `rtl_intf_ops`, chip `rtl_hal_ops`, firmware loading, BT coexistence, and PCI command TX.

## Risks
Single-vif assumptions, lock ordering around `conf_mutex`, and the coupling between scan, keys, IPS/LPS, association, and channel changes are the main hazards. Key handling has WEP/group/pairwise/MFP/IBSS exceptions. WoWLAN pattern translation and power-sequence parsing are hardware-format sensitive.

## Test Signals
Probe/register/start, station/AP/IBSS/mesh/P2P operation, association/disassociation, 20/40/80 MHz channel changes, IPS/LPS, scan under traffic, WEP/TKIP/CCMP key install/remove, AMPDU, beacon update, WoWLAN wake, and RF-kill polling.

# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/ps.c

## Purpose
Power-save control for rtlwifi: NIC enable/disable, inactive PS, firmware LPS, software LPS, RF state serialization, delayed work callbacks, and P2P Notice of Absence/offload handling.

## Important APIs, Types, And Functions
Public APIs include `rtl_ps_enable_nic()`, `rtl_ps_disable_nic()`, `rtl_ips_nic_off()`, `rtl_ips_nic_on()`, `rtl_lps_enter()`, `rtl_lps_leave()`, `rtl_lps_set_psmode()`, `rtl_swlps_beacon()`, `rtl_swlps_rf_awake()`, `rtl_swlps_rf_sleep()`, `rtl_p2p_ps_cmd()`, and `rtl_p2p_info()`.

## Control Flow
IPS delayed work refuses unsafe states, notifies BT coexistence, sets inactive RF state, and changes RF/ASPM. FW LPS sends firmware power actions; SW LPS parses TIMs, sleeps after multicast-free beacons, and wakes before DTIM. P2P helpers parse beacon/probe/action vendor IEs and send `HW_VAR_H2C_FW_P2P_PS_OFFLOAD`.

## State And Persistence
`rtl_ps_ctl` stores RF power state, RF-off reasons, `rfchange_inprogress`, IPS/LPS settings, FW/SW PS flags, DTIM/multicast state, `state_inap`, and `p2p_ps_info`. State is volatile and association-dependent.

## Dependencies And Integration Points
Uses chip `cfg->ops`, PCI ring reset/ASPM, watchdog/deferred work, BT coexistence, mac80211 PS flags, beacon parsing, and TX/RX traffic counters.

## Risks
RF changes involve locks and wait loops. IPS/LPS must avoid scans, key setup, P2P, and early association. SW sleep timing depends on beacon interval assumptions. P2P IE parsing is offset/length sensitive.

## Test Signals
Idle IPS, FW/SW LPS enter/leave, beacon TIM handling, nullfunc PM, busy traffic wakeups, linked scans, P2P NoA/CTWindow changes, BT notifications, ASPM, and lockdep.

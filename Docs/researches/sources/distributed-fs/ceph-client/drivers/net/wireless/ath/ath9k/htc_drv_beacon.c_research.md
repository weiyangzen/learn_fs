# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/htc_drv_beacon.c

Purpose: Implements ath9k_htc beacon queue configuration, beacon timer setup for STA/AP/IBSS/mesh modes, SWBA event handling, multi-VIF beacon slot assignment, buffered broadcast/multicast delivery, and channel switch completion checks.

Important APIs and functions: Public functions are `ath9k_htc_beaconq_config()`, `ath9k_htc_beaconep()`, `ath9k_htc_swba()`, `ath9k_htc_assign_bslot()`, `ath9k_htc_remove_bslot()`, `ath9k_htc_set_tsfadjust()`, `ath9k_htc_beacon_config()`, `ath9k_htc_beacon_reconfig()`, and `ath9k_htc_csa_is_finished()`. Internal helpers configure STA/AP/adhoc timers, choose beacon slots from TSF, send buffered CAB frames, and build/transmit beacon SKBs.

Control flow: Beacon configuration validates mode constraints, fills `cur_beacon_conf`, disables firmware interrupts through WMI, programs hardware beacon timers/queues, and re-enables interrupts. On SWBA events, the code handles beacon-pending stuck detection, chooses a slot from TSF modulo interval, sends buffered BC/MC frames from mac80211, then sends the current beacon with HTC beacon metadata prepended. Beacon slot assignment stores VIF pointers under `beacon_lock`; TSF adjustment offsets nonzero slots.

State and persistence: Runtime state includes `priv->cur_beacon_conf`, `priv->beacon.bslot[]`, beacon miss count, per-VIF beacon sequence and TSF adjust, queued TX count, and `priv->csa_vif`. No durable persistence exists.

Dependencies and integration points: Depends on mac80211 beacon APIs, WMI interrupt commands, ath9k common beacon config helpers, HTC TX slot handling, hardware TX queue programming, task/work reset path, and CSA helpers.

Risks: Beacon slot selection assumes a common beacon interval for multi-AP mode. `ath9k_htc_assign_bslot()` assumes a free slot exists. CAB frame padding manipulates SKB headroom and must preserve headers. Repeated beacon-pending events trigger fatal reset after `BSTUCK_THRESHOLD`.

Test signals: STA beacon timer setup, AP/mesh and IBSS beaconing, two beaconing VIFs with TSF adjustment, beacon interval change rejection for multi-AP, CAB delivery and TX slot exhaustion, SWBA stuck reset, CSA countdown finish, and scanning suppression.

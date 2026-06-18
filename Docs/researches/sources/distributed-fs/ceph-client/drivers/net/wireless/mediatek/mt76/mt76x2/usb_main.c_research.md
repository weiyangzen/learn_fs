# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/usb_main.c

Purpose: mac80211 operations table for MT76x2U. It starts/stops the USB MAC, handles channel changes and configuration updates, and wires common mt76x02 callbacks into mac80211.

Important APIs: `mt76x2u_ops`, `mt76x2u_start`, `mt76x2u_stop`, `mt76x2u_set_channel`, and `mt76x2u_config`.

Control flow: start calls common USB MAC start, queues periodic MAC work, and sets running state. Stop clears running, stops USB TX, and invokes hardware stop. Channel setting disables pre-TBTT, stops MAC, sets PHY channel, resets channel counters, resumes MAC, and re-enables pre-TBTT. Config handles monitor flag by toggling `MT_RX_FILTR_CFG_PROMISC`; power changes convert mac80211 dBm to half-dBm, apply SAR, adjust for 2-chain power, and if running reprogram txpower. Channel change updates survey state after releasing the driver mutex.

State and persistence: runtime state is `MT76_STATE_RUNNING`, rx filter bits, configured txpower, chandef, scheduled MAC work, and per-interface/mac80211 state held by common callbacks.

Dependencies and integration: depends on mac80211, mt76 core TX queueing, mt76x02 common interface/key/AMPDU/filter routines, USB PHY channel code, and `mt76_get_sar_power`.

Risks: monitor-mode logic is easy to invert because promiscuous filtering is toggled from `hw->conf.flags`. Channel switch must preserve MAC stop/resume symmetry even when PHY set fails. Power adjustment assumes 2x2 devices and subtracts 6 half-dBm for per-chain power.

Test signals: interface start/stop, monitor mode packet visibility, SAR and txpower changes while idle/running, channel switch failures, survey updates, AP beacon continuity, and mac80211 callback coverage for station/key/AMPDU paths.

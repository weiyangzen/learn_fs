## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/wow.c

Purpose: Wake-on-WLAN support for rtw88. It translates cfg80211 WoWLAN requests into firmware AOAC commands, pattern CAM entries, reserved pages, firmware swapping, power-save transitions, wake reason reporting, and resume restoration.

Important APIs/functions: public `rtw_wow_suspend()` and `rtw_wow_resume()`. Internals cover wake reason reporting, pattern mask translation/CRC/CAM writes, BB/RX-DMA stop/start, firmware status polling, security type iteration, firmware start/stop, reserved-page configuration, normal/WoW firmware swap, PNO request capture, PS leave/enter/restore, wakeup VIF selection, and cleanup.

Control flow: suspend sets wake flags/patterns/PNO and selects one station VIF, leaves normal PS, stops TRX, downloads WoW firmware, sets `RTW_FLAG_WOWLAN`, downloads WoW reserved pages, starts firmware wake controls, stops HCI, restarts BB, protects MAC reset, then enters WoW PS. Resume validates WoW flag, leaves PS, reports wake reason via mac80211, reinitializes HCI, stops firmware wake controls, clears pattern CAM, swaps normal firmware, restores normal reserved pages, restarts RX/BB/watchdog, restores PS, and frees PNO state.

State and persistence: mutates `rtwdev->wow` including selected VIF, pattern array/count, flags, PNO copies, `ips_enabled`, and saved `txpause`; also toggles `RTW_FLAG_WOWLAN` and `RTW_FLAG_LEISURE_PS_DEEP`.

Dependencies and integration: depends on firmware H2C/AOAC APIs, reserved-page builders, mac80211 WoWLAN reporting, PS, MAC/HCI operations, and utility iterators.

Risks and test signals: high-risk areas are firmware swap failures, pattern mask translation from Ethernet to 802.11/LLC layout, unsupported HCI reset avoidance, memory cleanup on partial setup, PNO deep PS behavior, and resume ordering. Test disconnect/magic/pattern/GTK/PNO wake, linked and no-link states, firmware failure injection, suspend/resume over PCI/USB, and leak checks for PNO arrays.

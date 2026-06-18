# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/wow.c

Purpose: implements rtw89 Wake-on-WLAN suspend/resume support. It selects a WoW-capable station/no-link vif, programs wake reasons and pattern CAMs, synchronizes key packet numbers and GTK/IGTK rekey state, swaps normal/WoW firmware, configures power-save and HCI/MAC state, and reports wakeup reasons to mac80211.

Important APIs/functions: `rtw89_wow_suspend()` and `rtw89_wow_resume()` are the main PM entry points. `__rtw89_wow_parse_akm()` records AKM from association requests. Internal major blocks handle cipher recognition, PN/IV conversion, key-info construction/update, AOAC report retrieval, GTK rekey notification, pattern generation, PNO offload, wake configuration, firmware swap, TRX pre/post transitions, and wake reason reporting.

Control flow: suspend parses requested wakeups, leaves normal PS, sets `RTW89_FLAG_WOWLAN`, disables normal TX/RX paths, swaps to WoW firmware, programs keep-alive/disconnect/GTK/ARP or PNO offloads, enables firmware WoW, enters PS/deep PS, and resets HCI/MAC for low power. Resume verifies WoW/power, leaves deep PS, reads wake reason, re-enables HCI/MAC, fetches AOAC reports before and after RX is ready, updates mac80211 key sequences/rekey state, disables WoW offloads, swaps back to normal firmware, restores RX filters/PPDU status, and clears wake state.

State and persistence: `rtwdev->wow` stores selected link, flags, patterns, PNO request/list, key info, GTK info, AOAC report, cipher algorithms, AKM, and counts. State is in-memory and cleared after resume/failure. Firmware maintains AOAC counters during suspend and reports them back.

Dependencies/integration: mac80211 WoWLAN/GTK APIs, cfg80211 patterns and scheduled scan, firmware H2C/C2H, CAM/security, MAC/PHY/HCI control, power-save code, util PN helpers, and chip generation callbacks.

Risks: PN/IV byte ordering and TKIP MIC swapping are security-critical. Pattern masks are translated from Ethernet to 802.11/LLC layout; off-by-one errors break wake matching. Firmware download with interrupts disabled must re-enable on failures. No-link PNO and linked WoW paths differ but share cleanup.

Test signals: suspend/resume with magic packet, disconnect, pattern, GTK rekey, PMF IGTK, and PNO; AOAC report debug logs; wakeup reason reporting; firmware swap success; key PN continuity after resume.

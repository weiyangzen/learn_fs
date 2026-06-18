# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/sta.h

Purpose: Declares WFx mac80211 callback functions, station-private data, and firmware event helper APIs.

Important APIs and types: `struct wfx_sta_priv` stores firmware link ID and vif ID for each mac80211 station. Prototypes cover lifecycle/config/filter/interface/AP/IBSS/TX queue/BSS/station/TIM/AMPDU/channel-context/PM callbacks, plus hardware-event helpers for cooling, hot-device suspend, multicast suspend/resume, RSSI report, PM update, and reset.

Control flow and integration: `main.c` wires most functions into `ieee80211_ops`; `hif_rx.c` calls event helpers for RSSI, BSS lost, PM completion, and suspend/resume indications; data TX uses station private link IDs.

State and persistence: Per-station private state persists while mac80211 station objects live and maps firmware link IDs back to vifs.

Dependencies: Depends on mac80211 types and WFx device/vif private structures.

Risks and test signals: Build tests should catch mac80211 signature changes. Runtime tests should validate station private initialization/removal, link ID reuse, and helper calls for firmware indications.

Test signals: Source read size: 73 lines, 3343 bytes.

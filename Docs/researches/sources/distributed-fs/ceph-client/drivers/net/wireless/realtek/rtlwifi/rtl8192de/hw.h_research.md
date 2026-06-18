# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/hw.h

Purpose: Declares rtl8192de PCI hardware operation entry points.

Important APIs/types: Exposes hardware get/set, interrupt recognition and mask control, initialization and card disable, network type/BSSID/beacon controls, DBI read/write, suspend/resume, and linked-channel IQK check.

Control flow: Header declarations support the rtl8192de ops table in `sw.c` and calls across firmware/DM/PHY code.

State and persistence: No header state. Functions manipulate PCI rings, hardware registers, interrupts, RF state, and cached suspend register values.

Dependencies and integration: Requires `ieee80211_hw`, `rtl_int`, `nl80211_iftype`, and kernel integer types. Included by rtl8192de hardware and ops setup.

Risks: Raw value-pointer API mirrors rtlwifi core and depends on callers passing the correct type for each `HW_VAR`. Interrupt functions must be paired correctly by bus layer.

Test signals: Compile/link coverage through rtl8192de HAL ops and runtime init/interrupt/network-mode paths.

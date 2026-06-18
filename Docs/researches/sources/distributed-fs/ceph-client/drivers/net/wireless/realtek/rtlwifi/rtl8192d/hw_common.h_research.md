# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/hw_common.h

Purpose: Declares the shared RTL8192D hardware helper API used by bus-specific implementations.

Important APIs/types: Exposes beacon stop/resume, common hardware get/set, LLT write, security configuration, QoS reset, EEPROM read, HAL rate update, channel access update, GPIO RF switch check, and CAM key setup.

Control flow: The API is intended to be called from bus-specific initialization, mac80211 callbacks, rate-control updates, key setup, and power-management paths. The header itself has no runtime logic.

State and persistence: Functions mutate hardware registers and driver structures such as `rtl_efuse`, `rtl_hal`, `rtl_phy`, `rtl_ps_ctl`, and `rtlpriv->sec`; no header-local state.

Dependencies and integration: Included by rtl8192d common users and rtl8192de hardware code. Requires `ieee80211_hw`, `ieee80211_sta`, and rtlwifi enums/types from surrounding includes.

Risks: Function prototypes expose raw pointers for values and keys, so caller type/length discipline is essential. Common helpers assume bus-specific wrappers supply PCI/USB-specific register and interrupt behavior when needed.

Test signals: Compile coverage and smoke tests through rtl8192de `rtl_hal_ops` paths that call these helpers.

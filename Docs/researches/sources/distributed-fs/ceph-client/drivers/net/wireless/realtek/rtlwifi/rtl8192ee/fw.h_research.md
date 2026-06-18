# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/fw.h

Purpose: Defines RTL8192EE firmware limits, header detection, H2C command IDs/lengths, firmware power-state bits, H2C packing macros, and firmware-facing function declarations.

Important APIs/definitions: Firmware size/page/polling constants, `IS_FW_HEADER_EXIST()`, H2C IDs for reserved pages/media/scan/offload/power/RA/RSSI/P2P/WoWLAN/AOAC, power bits such as `FW_PS_RF_ON`, `FW_PS_REGISTER_ACTIVE`, `FW_PS_ACK`, `FW_PS_CLOCK_OFF`, `pagenum_128()`, pwrmode/reserved-page/media-status setters, and declarations implemented by `fw.c`.

Control flow/integration: `fw.c` uses the constants/macros for download and H2C packing. DM and power/hardware paths call the declared functions for RSSI, LPS, media status, reserved pages, P2P offload, and C2H RA handling.

State and persistence: Header is stateless. Macros mutate caller-provided command buffers that are sent to firmware.

Dependencies: Requires endian helpers, bit macros, and rtlwifi/mac80211 types. `USE_OLD_WOWLAN_DEBUG_FW` changes some command IDs.

Risks/test signals: Command packing is macro-based and not type-safe. `H2C_92E_P2P_PS_OFFLOAD = 024` is octal decimal 20. `FW_PWR_STATE_ACTIVE`/`RF_OFF` are duplicated. Some media-status MACID macros reference `__ph2ccmd` despite taking `__cmd`. Build and firmware command traces are primary validation.

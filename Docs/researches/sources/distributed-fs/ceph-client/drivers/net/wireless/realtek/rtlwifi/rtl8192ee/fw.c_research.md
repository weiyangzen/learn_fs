# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/fw.c

Purpose: Handles RTL8192EE firmware download/readiness, firmware reset, H2C mailbox commands, power-mode/media-status commands, reserved-page offload, P2P PS offload, and C2H RA report handling.

Important APIs/functions: `rtl92ee_download_fw()` strips optional firmware header, enables download mode, writes firmware pages, and waits for checksum/ready. `_rtl92ee_fill_h2c_command()` serializes mailbox access, waits for firmware to clear boxes, writes normal/extension H2C boxes, and advances `last_hmeboxnum`. `rtl92ee_fill_h2c_cmd()` gates on `fw_ready`. `rtl92ee_firmware_selfreset()` toggles 8051 reset bits. `rtl92ee_set_fw_pwrmode_cmd()` packs LPS mode with Bluetooth coexistence overrides. `rtl92ee_set_fw_media_status_rpt_cmd()` sends connect/disconnect state. `rtl92ee_set_fw_rsvdpagepkt()` patches and sends a 1024-byte reserved-page packet image, then sends page locations. `rtl92ee_set_p2p_ps_offload_cmd()` programs CTWindow/NoA registers and sends P2P offload state. `rtl92ee_c2h_ra_report_handler()` delegates ARFB updates to DM.

Control flow: Firmware bytes in `rtlhal->pfirmware` are padded, page-written, and validated by `FWDL_CHKSUM_RPT` and `WINTINI_RDY`. H2C commands are blocked when firmware is unavailable or RF is off, protected by `h2c_lock` and `h2c_setinprogress`, and use four rotating mailboxes. Reserved page setup sends a command skb before informing firmware of page locations.

State and persistence: Updates `fw_version`, `fw_subversion`, `last_hmeboxnum`, `h2c_setinprogress`, `p2p_ps_offload`, power/FW registers, and a static `reserved_page_packet`. Firmware state persists only in device memory.

Dependencies/integration: rtlwifi firmware helpers, PCI/base/core/EFUSE, RTL8192EE `reg.h`, `def.h`, `fw.h`, `dm.h`, Bluetooth coexistence, P2P/mac80211 state, and 802.11 frame patch macros.

Risks: Unused `buse_wake_on_wlan_fw`, unused `version`, missing-firmware return value `1`, silent H2C drops after timeouts, command length limit of 7, suspicious media-status macros in `fw.h`, static reserved-page buffer races across devices, ignored `b_dl_finished`, and uncapped local NoA loop.

Test signals: Firmware checksum/ready success, H2C command traces, LPS entry/exit, reserved-page setup after association, P2P GO/client CTWindow/NoA behavior, C2H RA report handling, and multi-device concurrency.

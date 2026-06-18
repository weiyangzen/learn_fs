# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192c/fw_common.c

`fw_common.c` implements shared RTL8192C-family firmware download and host-to-controller command handling. It loads firmware into device memory, waits for firmware readiness, serializes H2C mailbox writes, sends power-save commands, prepares reserved pages, reports join state, and configures P2P power-save offload.

Important functions include `rtl92c_download_fw()`, `_rtl92c_enable_fw_download()`, `_rtl92c_write_fw()`, `_rtl92c_fw_free_to_go()`, `_rtl92c_fill_h2c_command()`, `rtl92c_fill_h2c_cmd()`, `rtl92c_firmware_selfreset()`, `rtl92c_set_fw_pwrmode_cmd()`, `rtl92c_set_fw_rsvdpagepkt()`, `rtl92c_set_fw_joinbss_report_cmd()`, and `rtl92c_set_p2p_ps_offload_cmd()`. Firmware download enables MCU download, writes pages or blocks, disables download, waits for checksum, sets ready, and polls initialization. H2C command flow uses `h2c_lock`, `h2c_setinprogress`, four HME boxes, firmware-read polling, extended mailbox bytes, and `last_hmeboxnum` rotation.

State includes `rtlhal->pfirmware`, firmware version/subversion/size, `fw_ready`, H2C mailbox state, static reserved-page packet data, MAC/BSSID/AID fields, and P2P PS offload descriptors. Dependencies include rtlwifi firmware write helpers, skb allocation, rtl8192ce registers, and common H2C IDs.

Risks include `rtl92c_download_fw()` returning success even after firmware-ready failure, static reserved-page mutation across devices, mailbox timeout handling, command length limits, and P2P NoA time loops. Test signals include firmware checksum/ready logs, H2C traces, LPS transitions, reserved page download, join reports, P2P offload, and concurrent command stress.

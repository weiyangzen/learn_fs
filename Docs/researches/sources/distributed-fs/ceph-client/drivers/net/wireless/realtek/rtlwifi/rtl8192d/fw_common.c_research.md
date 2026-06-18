# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/fw_common.c

Purpose: Provides shared RTL8192D firmware download, firmware readiness, self-reset, and host-to-controller command mailbox helpers.

Important APIs/functions: `rtl92d_is_fw_downloaded()` checks `REG_MCUFWDL`. `rtl92d_enable_fw_download()` toggles MCU download mode. `rtl92d_write_fw()` writes firmware pages. `rtl92d_fw_free_to_go()` waits for checksum and sets `MCUFWDL_RDY`. `rtl92d_firmware_selfreset()` resets the 8051 firmware core. `rtl92d_fw_init()` waits for MAC0/MAC1 firmware ready bits. `rtl92d_fill_h2c_cmd()` serializes H2C mailbox writes. `rtl92d_set_fw_joinbss_report_cmd()` wraps the join-BSS report command.

Control flow: Firmware download enables CPU/download registers, writes up to page-sized firmware chunks, disables download mode, polls checksum report, marks firmware ready, then polls MAC-specific ready bytes. H2C command flow first refuses RF-off states, acquires `h2c_lock` to serialize `h2c_setinprogress`, waits for firmware to clear the selected HME box, writes normal or extended mailbox bytes depending on command length, advances the 4-box ring, and clears the in-progress flag.

State and persistence: Hardware state lives in `REG_MCUFWDL`, `REG_SYS_FUNC_EN`, `REG_HMETFR`, `REG_HMEBOX_*`, and ready registers. Driver state lives in `rtlhal->last_hmeboxnum` and `rtlhal->h2c_setinprogress`. No on-disk persistence.

Dependencies and integration: Uses rtlwifi register I/O, PCI/base/efuse helpers, firmware layout constants from `fw_common.h`, command IDs from RTL8192D definitions, and power state from `rtl_ps_ctl`. Called by rtl8192de firmware download, DM RSSI report, reserved-page setup, and hardware join-BSS handling.

Risks: Busy waits and polling limits can cause slow initialization or command loss when firmware is hung. `rtl92d_write_fw()` warns on more than 8 pages but continues. H2C only accepts command lengths 1-5. Incorrect RF-off gating or missing lock release would break firmware commands. USB reset has extra interrupt masking and timing, so shared changes can affect multiple buses.

Test signals: Firmware load success, checksum-ready logs, MAC0/MAC1 ready polling, H2C command traces for join, RSSI, power mode, and reserved pages, plus suspend/resume and dual-MAC firmware-sharing tests.

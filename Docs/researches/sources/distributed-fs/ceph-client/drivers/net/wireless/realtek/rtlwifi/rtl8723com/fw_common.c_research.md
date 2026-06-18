<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723com/fw_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723com/fw_common.c

## Purpose
Implements shared RTL8723 firmware download, page writing, firmware-ready polling, and 8051 self-reset helpers for RTL8723AE and RTL8723BE.

## Important APIs, Types, And Functions
- `rtl8723_enable_fw_download` toggles MCU firmware download mode through `REG_SYS_FUNC_EN` and `REG_MCUFWDL`.
- `rtl8723_write_fw` pads firmware with `rtl_fill_dummy`, splits it into `FW_8192C_PAGE_SIZE` pages, and writes pages through `rtl_fw_page_write`.
- `rtl8723ae_firmware_selfreset` and `rtl8723be_firmware_selfreset` implement chip-specific 8051 reset sequences.
- `rtl8723_fw_free_to_go` waits for `FWDL_CHKSUM_RPT`, sets `MCUFWDL_RDY`, optionally resets BE firmware, and polls `WINTINI_RDY`.
- `rtl8723_download_fw` validates loaded firmware buffer, strips a firmware header when present, resets any existing firmware state, enables download, writes firmware, disables download, and waits for readiness.
- All public helpers are exported with `EXPORT_SYMBOL_GPL`.

## Control Flow
Firmware download starts by checking `rtlpriv->max_fw_size` and `rtlhal->pfirmware`, reading firmware header version/subversion, choosing max page count of 6 for AE or 8 for BE, optionally skipping the header, resetting the MCU if bit 7 of `REG_MCUFWDL` indicates an existing firmware state, enabling download mode, writing all full and remaining pages, disabling download mode, and polling readiness. Polling loops are bounded by the caller-provided max count and report errors on checksum or ready timeout.

## State And Persistence
The file mutates MCU control registers, firmware download status bits, 8051 reset state, and `rtlhal->fw_version`/`fw_subversion`. Firmware bytes are transferred from `rtlhal->pfirmware` into device memory and persist until hardware reset, firmware reset, or power loss.

## Dependencies And Integration Points
Used by RTL8723AE/BE firmware-specific code through `fw_common.h`. Depends on rtlwifi firmware helpers, register constants, `struct rtlwifi_firmware_header`, and chip-specific `is_fw_header` HAL op. Kernel firmware request and callback code populates `rtlhal->pfirmware` before this path runs.

## Risks And Edge Cases
`rtl8723_write_fw` only prints if page count exceeds `max_page` and continues, so oversized firmware relies on earlier size limits. `rtl8723_download_fw` returns 0 even after `rtl8723_fw_free_to_go` reports an error, while logging failure; callers must inspect behavior carefully. Header stripping depends on chip-specific signature checks. Reset sequences differ between AE and BE, and timing/polling constants are hardware-sensitive.

## Test Signals
Signals include firmware version logs, successful checksum report, `WINTINI_RDY` polling success, working H2C commands after download, recovery when firmware was already loaded, and failure-path logs for missing firmware, bad checksum, or ready timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723com/fw_common.c -->

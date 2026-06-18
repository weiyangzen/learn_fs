# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/fw.c

## Purpose
Downloads and starts RTL8192DU firmware using shared rtl8192d firmware helpers. It parses the Realtek firmware header, skips it when present, resets running RAM firmware when needed, writes the firmware image, waits for readiness, and performs firmware initialization.

## Important APIs, Types, And Functions
The single exported function is `rtl92du_download_fw()`. It uses `GET_FIRMWARE_HDR_VERSION()`, `GET_FIRMWARE_HDR_SUB_VER()`, `GET_FIRMWARE_HDR_SIGNATURE()`, `IS_FW_HEADER_EXIST()`, `rtl92d_is_fw_downloaded()`, `rtl92d_firmware_selfreset()`, `rtl92d_enable_fw_download()`, `rtl92d_write_fw()`, `rtl92d_fw_free_to_go()`, and `rtl92d_fw_init()`.

## Control Flow
The function first rejects missing firmware storage. It records firmware version and subversion from the header, advances past the 32-byte header if present, and skips direct download if firmware is already loaded. If the MCU firmware download register indicates RAM code is running, it triggers firmware self-reset and clears `REG_MCUFWDL`. It then enables firmware download mode, writes the body, disables download mode, waits for firmware to be free-to-go, logs failure if not ready, and finally calls firmware init regardless of whether the image was newly downloaded.

## State And Persistence
Updates `rtlhal->fw_version` and `rtlhal->fw_subversion`; reads `rtlhal->pfirmware`, `fwsize`, `max_fw_size`, and chip version. Persistent firmware state lives in the device MCU after successful download/init. `REG_MCUFWDL` tracks download/readiness status.

## Dependencies And Integration Points
Called by `rtl92du_hw_init()` in `hw.c`. Depends on firmware memory prepared by software init, rtl8192d common firmware routines, and register constants. The exact firmware name and request path are handled in DU `sw.c`, not this file.

## Risks
The function returns failure when firmware storage is missing, and hardware init treats some firmware errors specially. Header parsing assumes at least a valid header-sized buffer when macros inspect it. If `rtl92d_fw_free_to_go()` fails, the code still calls `rtl92d_fw_init()`, so callers must interpret the returned error carefully. Resetting running RAM code is timing sensitive.

## Test Signals
Firmware logs should show version, subversion, and signature, optional header shift, successful free-to-go, and successful firmware init. Reinitialization after suspend/reset should exercise the self-reset and already-downloaded paths.

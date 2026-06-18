<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/init.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/init.c

## Purpose
`init.c` owns ath6kl hardware bring-up, firmware discovery/loading, target host-interest configuration, HTC/WMI endpoint initialization, and the stop/restart paths used by firmware recovery. It is the central transition layer between bus-specific HIF operations and the higher cfg80211/WMI runtime.

## Important APIs, Types, And Functions
The static `hw_list[]` table maps supported AR6003/AR6004 hardware versions to firmware directories, board file names, load addresses, reserved RAM sizes, UART pins, reference clocks, and workarounds. `ath6kl_init_hw_params()` selects one entry based on `ar->version.target_ver` and copies it into `ar->hw`.

Buffer/profile initialization is handled by `ath6kl_buf_alloc()`, `ath6kl_init_profile_info()`, and `ath6kl_init_control_info()`. Target setup is split across `ath6kl_configure_target()`, `ath6kl_set_htc_params()`, `ath6kl_set_host_app_area()`, and `ath6kl_target_config_wlan_params()`. Firmware retrieval is split into legacy API 1 file fetchers and `ath6kl_fetch_fw_apin()`, which parses newer firmware container IEs for firmware image, OTP, patch, capabilities, VIF count, reserved RAM, and target addresses. Upload helpers include `ath6kl_upload_board_file()`, `ath6kl_upload_otp()`, `ath6kl_upload_firmware()`, `ath6kl_upload_patch()`, `ath6kl_upload_testscript()`, and the sequencing wrapper `ath6kl_init_upload()`.

Runtime lifecycle entry points are `ath6kl_init_hw_start()`, `ath6kl_init_hw_stop()`, `ath6kl_init_hw_restart()`, and exported `ath6kl_stop_txrx()`.

## Control Flow
Startup powers on HIF, writes host-interest fields, temporarily disables target sleep, programs clock/LPO/GPIO workaround registers, uploads board/OTP/firmware/patch/testscript assets through BMI, ends BMI, waits for HTC target ready, connects WMI control and data services, starts HTC, waits for `WMI_READY`, validates ABI, writes host application area protocol version, then sends per-VIF WLAN configuration WMI commands. Error labels stop HTC, clean scatter support, and power off HIF according to progress reached.

Firmware fetch first requires a board file, optionally from exact firmware name, device-tree board-id fallback, or default board file. Testmode firmware can replace normal firmware before API container probing. API containers are tried from API5 down to API2 before falling back to API1 loose files.

## State And Persistence
Persistent state is all in memory and on target RAM/registers: `ar->hw`, `ar->fw*` image buffers, `ar->fw_api`, `ar->fw_capabilities`, `ar->vif_max`, `ar->state`, `ar->flag`, WMI endpoint maps, and host-interest fields. Firmware blobs are copied with `kmemdup()` or `vmalloc()` and retained for upload. No filesystem state is written; firmware is read through Linux firmware loading.

## Dependencies And Integration Points
This file depends on firmware loader APIs, device tree, BMI, HIF ops, HTC ops, WMI command helpers, cfg80211 VIF cleanup, debug logging, and target register constants in `target.h`. Bus backends provide HIF power, BMI, diagnostic, and scatter operations. `recovery.c` calls `ath6kl_init_hw_restart()`, while SDIO/USB remove paths call `ath6kl_stop_txrx()`.

## Risks
Risk concentrates around target-specific constants, firmware container validation, and partial-start unwind. Host-interest offsets must match firmware ABI. `ath6kl_init_get_fwcaps()` uses a suspicious bound based on `sizeof(ar->fw_capabilities) * 4`; changes to the bitmap layout should be checked carefully. `ath6kl_upload_board_file()` assumes board file sizes and target RAM addresses are consistent with hardware. Restart paths deliberately bypass outer state changes and can leave device state inconsistent if stop or start fails mid-recovery.

## Test Signals
Useful validation signals include firmware API selection logs, first-boot firmware/capability output, WMI ready wait success, ABI mismatch errors, board/OTP/patch upload failures, HTC endpoint connection failures, and successful restart after recovery. Practical tests should cover missing board files, device-tree board-id fallback, API container parse errors, testmode 1/2 firmware selection, and suspend/recovery interactions that call restart or stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/init.c -->

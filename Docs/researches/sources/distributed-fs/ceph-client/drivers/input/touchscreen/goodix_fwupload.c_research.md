# sources/distributed-fs/ceph-client/drivers/input/touchscreen/goodix_fwupload.c

## Purpose
`goodix_fwupload.c` supports legacy Goodix controllers without flash by uploading firmware into SRAM, answering firmware runtime requests, sending main-clock/config data, and preserving backup-reference calibration values across suspend where possible.

## Important APIs, types, and functions
- `struct goodix_fw_header` describes the firmware blob header containing hardware info, PID, and VID.
- `goodix_firmware_verify()` checks the exact expected firmware size and verifies separate additive checksums for the main firmware and DSP firmware regions.
- `goodix_enter_upload_mode()` holds the controller cores in reset, powers DSP clocks, disables watchdog/cache, selects SRAM boot, reboots, disables scrambling, and enables code-memory access.
- `goodix_firmware_upload()` requests `goodix/<firmware-name>`, verifies it, resets without INT sync, enters upload mode, writes four main 8 KiB sections across SRAM banks 0/1, writes the 4 KiB DSP section to bank 2, starts firmware, and performs INT sync.
- `goodix_prepare_bak_ref()` sizes and initializes backup-reference data from the current config matrix dimensions.
- `goodix_send_main_clock()` derives a 6-byte checksum-protected clock payload from `goodix,main-clk` or default 54.
- `goodix_firmware_check()` detects the `firmware-name` property and triggers upload during probe.
- `goodix_handle_fw_request()` services controller requests for config, backup reference, reset/reupload, main clock, unknown, and idle states.
- `goodix_save_bak_ref()` reads backup-reference data on suspend when firmware reports valid status.

## Control flow
During probe, `goodix_firmware_check()` returns early for normal flash-backed controllers. If a firmware name is present, it requires an IRQ-pin access method, marks config loading from disk as necessary, and uploads firmware before the main driver reads version/config. After firmware boot, the event path in `goodix.c` may see a zero coordinate status and call `goodix_handle_fw_request()`. That helper reads `GOODIX_REG_REQUEST`, performs the requested side effect, and acknowledges with `GOODIX_RQST_RESPONDED`.

## State and persistence
Uploaded firmware resides in volatile controller SRAM. The driver keeps the selected firmware name, config bytes, main-clock bytes, and backup-reference buffer in `struct goodix_ts_data`. Backup-reference data is initialized to neutral values and refreshed on suspend if available; it is not persisted to the filesystem.

## Dependencies and integration points
The file depends on the firmware loader, I2C helpers and shared state from `goodix.h`, device properties, Goodix reset/INT-sync sequencing, and the main event/PM paths in `goodix.c`.

## Risks
- Firmware upload is timing- and register-sequence-sensitive; partial failures can leave the controller in upload/reset mode.
- Firmware blob verification only checks size and additive checksums, not semantic compatibility with the current panel.
- `goodix_handle_fw_request()` acknowledges even for unknown/idle cases and ignores ack write errors, so request state can diverge silently.
- `goodix_save_bak_ref()` assumes `bak_ref` is allocated before a valid firmware status is seen; request ordering must ensure `goodix_prepare_bak_ref()` ran before reads that need the buffer.
- Main-clock values are truncated into bytes in a loop; unusual `goodix,main-clk` values should be tested.

## Test signals
- Probe a flashless controller with valid, missing, bad-size, and bad-checksum firmware files.
- Exercise request handling for CONFIG, BAK_REF, RESET, MAIN_CLOCK, UNKNOWN, and IDLE.
- Suspend/resume tests should verify backup-reference preservation and firmware reupload after controller reset requests.
- Fault-injection tests should cover I2C failures during bank selection, section writes, firmware start, and request acknowledgement.

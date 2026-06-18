# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00firmware.c

## Purpose
Implements common firmware request, validation, upload, version reporting, and release for rt2x00 drivers whose capability flags require firmware.

## Important APIs, Types, And Functions
Private `rt2x00lib_request_firmware()` asks chip code for a firmware filename, calls `request_firmware()`, validates non-empty data, logs version bytes from the end of the image, stores `wiphy->fw_version`, and dispatches chip `check_firmware()`. Exported `rt2x00lib_load_firmware()` caches and uploads firmware through chip `load_firmware()`. `rt2x00lib_free_firmware()` releases the cached image.

## Control Flow
`rt2x00lib_start()` calls `rt2x00lib_load_firmware()`. If `REQUIRE_FIRMWARE` is clear, the load path returns immediately. Otherwise it requests firmware once and reuses `rt2x00dev->fw` on later starts, validates chip-specific status codes (`FW_OK`, bad CRC/length/version), uploads through `ops->lib->load_firmware`, then resets association LED state because firmware upload can disturb LEDs.

## State And Persistence
The cached firmware pointer persists in `rt2x00dev->fw` until `rt2x00lib_free_firmware()` during device removal. The wiphy firmware version string persists for userspace until unregister.

## Dependencies And Integration Points
Depends on Linux firmware loader, wiphy device association, chip-specific `get_firmware_name`, `check_firmware`, and `load_firmware` callbacks, capability flag `REQUIRE_FIRMWARE`, and LED association helper.

## Risks
Version extraction assumes firmware has at least four bytes and stores bytes at `size - 4` and `size - 3`. Firmware status values must match chip check callback contract. If firmware upload succeeds but later radio init fails, cached firmware remains and later retries may skip request but still upload. SoC stubs must not be reached with `REQUIRE_FIRMWARE` set.

## Test Signals
Missing firmware, zero-length firmware, bad CRC/length/version from chip callbacks, successful upload for PCI/USB, repeated start/stop using cached firmware, removal release, wiphy `fw_version`, and LED association reset after upload.

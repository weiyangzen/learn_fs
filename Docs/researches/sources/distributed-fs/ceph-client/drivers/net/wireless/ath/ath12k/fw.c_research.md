# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/fw.c

## Purpose

`fw.c` parses ath12k API 2 firmware container files. It validates the firmware magic, walks typed information elements, records firmware feature bits, and maps embedded AMSS, M3, auxiliary microcode, and dual-MAC AMSS image spans into `ab->fw`. It also exposes firmware map/unmap and feature query helpers.

## Important APIs, Types, and Functions

The local `ath12k_fw_request_firmware_api_n()` requests `firmware-2.bin`, validates `ATH12K_FIRMWARE_MAGIC`, iterates `struct ath12k_fw_ie` records, and handles IE IDs for timestamp, features, AMSS image, M3 image, auxiliary microcode image, and dual-MAC AMSS image.

`ath12k_fw_map()` tries API 2 firmware and sets `ab->fw.api_version` to 2 on success or 1 on failure. `ath12k_fw_unmap()` releases the firmware and zeroes the firmware state. `ath12k_fw_feature_supported()` checks `fw_features_valid` and a bit in `ab->fw.fw_features`.

## Control Flow

Firmware map requests the API 2 file through `ath12k_core_firmware_request()`. On success, parsing starts with a magic string including its trailing NUL, aligns past padding, and loops over IE headers while enough bytes remain. Each IE length is bounds-checked before use, payloads are interpreted by ID, then the payload length is aligned to four bytes before advancing.

On parse errors, the requested firmware is released and `ab->fw.fw` is cleared. Unknown IE IDs are warned but skipped, so forward-compatible metadata does not fail loading.

## State and Persistence Behavior

State persists in `ab->fw`: the `struct firmware *`, API version, feature bitmap validity, image data pointers, and image lengths. Image pointers reference memory owned by the firmware blob and remain valid until `ath12k_fw_unmap()` releases it. Unmap clears the whole firmware state to prevent stale pointers.

## Dependencies and Integration Points

This file depends on core firmware request/release support, `fw.h` constants and enums, `hw.h` image naming conventions indirectly, debug logging, and later boot/QMI/MHI paths that consume `ab->fw.amss_data`, `m3_data`, `aux_uc_data`, or feature bits such as MLO and multi-QRTR support.

## Risks and Edge Cases

- API 2 parse failure silently falls back to API version 1 in `ath12k_fw_map()` without requesting legacy files here; legacy consumers must handle that path elsewhere.
- If aligned IE length exceeds remaining length, the loop breaks and returns success rather than failing. This tolerates trailing truncation/padding but can hide malformed final IEs.
- Feature bitmap parsing stops when `index == ie_len`; using `>=` would be more defensive if future edits alter loop bounds.
- Image data pointers are borrowed from the firmware blob; no consumer may outlive `ath12k_fw_unmap()`.

## Test Signals

Test with valid API 2 blobs, missing firmware, invalid magic, too-small files, truncated IE payloads, unknown IEs, feature bitmaps of varying length, and boot paths that require MLO or auxiliary microcode features.

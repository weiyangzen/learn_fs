# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/fw.c

## Purpose

`fw.c` handles ath11k firmware container pre-initialization for the API 2 firmware format. It requests `firmware-2.bin`, validates the ath11k firmware magic, parses aligned information elements, records embedded AMSS and M3 image spans, captures advertised feature bits, and falls back to API 1 behavior when API 2 firmware is unavailable.

## Important APIs, Types, and Functions

- `ath11k_fw_request_firmware_api_n()` is the parser/loader for named API-N firmware files. In this file it is used for `ATH11K_FW_API2_FILE`.
- `ath11k_fw_pre_init()` attempts to load API 2 firmware, sets `ab->fw.api_version` to 2 on success, and otherwise sets it to 1 while returning success to let older firmware flows continue.
- `ath11k_fw_destroy()` releases `ab->fw.fw` and is exported.
- Parsed IE ids come from `enum ath11k_fw_ie_type`: timestamp, feature bitmap, AMSS image, and M3 image.

## Control Flow

`ath11k_fw_pre_init()` calls `ath11k_fw_request_firmware_api_n(ab, "firmware-2.bin")`. The helper requests firmware through `ath11k_core_firmware_request()`, stores the `struct firmware` in `ab->fw.fw`, and validates that the file starts with `ATH11K_FIRMWARE_MAGIC` including its terminating null byte. The parser aligns past the magic to a 4-byte boundary and then iterates `struct ath11k_fw_ie` records while enough bytes remain.

For each IE, the parser converts little-endian `id` and `len`, ensures the payload fits inside the remaining file, and dispatches by IE type. Timestamp IEs are logged when exactly 4 bytes. Feature IEs set bits in `ab->fw.fw_features` up to `ATH11K_FW_FEATURE_COUNT`. AMSS and M3 IEs set `ab->fw.amss_data/amss_len` and `ab->fw.m3_data/m3_len` to point directly into the firmware blob. Unknown IEs are warned but skipped. Payload length is aligned to 4 bytes before moving to the next IE.

If validation fails, the helper releases the firmware and clears `ab->fw.fw`. If API 2 loading fails, `ath11k_fw_pre_init()` deliberately records API version 1 and returns 0.

## State and Persistence Behavior

Firmware state is stored in `ab->fw`. The firmware blob remains owned by the kernel firmware loader until `ath11k_fw_destroy()` releases it. AMSS and M3 image pointers are not copied; they reference slices inside `ab->fw.fw->data`, so they are valid only while the firmware object is held. Feature bits are set in `ab->fw.fw_features`. There is no on-disk persistence.

## Dependencies and Integration Points

The file depends on `ath11k_core_firmware_request()`, Linux firmware release APIs, endian helpers, bitmap helpers, debug logging, and `struct ath11k_fw_ie` from core firmware definitions. It integrates with boot/pre-init code that needs firmware API version, feature flags, and image payload pointers before hardware start.

## Risks and Edge Cases

- API 2 parser returns success even if mandatory AMSS/M3 images are absent; later boot stages must validate required image pointers/lengths.
- AMSS/M3 pointers alias the firmware blob. Releasing `ab->fw.fw` too early invalidates them.
- The IE loop stops silently if aligned IE length exceeds remaining bytes after the earlier payload-fit check; this avoids overrun but can leave trailing malformed padding unreported.
- `ATH11K_FW_FEATURE_COUNT` is currently only a sentinel with no feature values in this snapshot, so feature parsing is structurally present but has no meaningful feature bits to set.
- Any parser change must preserve little-endian interpretation and 4-byte alignment.

## Test Signals

Test with missing `firmware-2.bin` to verify API 1 fallback, invalid magic and too-small files for `-EINVAL` cleanup, malformed IE lengths, unknown IE ids, valid timestamp/features/image IEs, and module/device teardown to ensure `ath11k_fw_destroy()` releases the firmware without dangling later access.

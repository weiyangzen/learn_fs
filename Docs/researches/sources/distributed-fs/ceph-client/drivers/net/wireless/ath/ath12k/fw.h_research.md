# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/fw.h

## Purpose

`fw.h` defines ath12k firmware container constants, firmware IE IDs, firmware feature bits, and the public firmware map/unmap/feature-query API.

## Important APIs, Types, and Functions

Constants include `ATH12K_FW_API2_FILE` (`firmware-2.bin`) and `ATH12K_FIRMWARE_MAGIC`.

`enum ath12k_fw_ie_type` identifies timestamp, features, AMSS image, M3 image, dual-MAC AMSS image, and auxiliary microcode image records.

`enum ath12k_fw_features` currently exposes `ATH12K_FW_FEATURE_MULTI_QRTR_ID`, `ATH12K_FW_FEATURE_MLO`, and a count sentinel.

Declared functions are `ath12k_fw_map()`, `ath12k_fw_unmap()`, and `ath12k_fw_feature_supported()`.

## Control Flow and Integration

Boot code calls `ath12k_fw_map()` before image download and feature-dependent setup. Consumers check features through `ath12k_fw_feature_supported()`. Teardown calls `ath12k_fw_unmap()` after all users of borrowed firmware image pointers are done.

## State and Persistence Behavior

The header defines no storage, but its API fills and clears `ab->fw`, including borrowed pointers into the firmware blob and feature bitmap validity.

## Dependencies and Integration Points

The header depends on `struct ath12k_base` from core declarations and is consumed by firmware boot, QMI/transport setup, and feature gating code.

## Risks and Contract Notes

- Feature enum ordering is ABI-like for firmware bitmaps; new features must be appended before `ATH12K_FW_FEATURE_COUNT`.
- API 2 image IDs are container-specific and should stay synchronized with firmware tooling.
- Feature checks are false until `fw_features_valid` is set by a successfully parsed features IE.

## Test Signals

Compile checks, firmware parser unit/fault tests, and boot tests that assert feature gates for MLO and multi-QRTR are the main signals.

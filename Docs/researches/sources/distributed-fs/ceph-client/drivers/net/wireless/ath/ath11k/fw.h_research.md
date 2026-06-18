# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/fw.h

## Purpose

`fw.h` defines the ath11k firmware API 2 filename, firmware magic string, firmware IE identifiers, firmware feature enum, and the pre-init/destroy entry points implemented by `fw.c`.

## Important APIs, Types, and Functions

- `ATH11K_FW_API2_FILE` is `"firmware-2.bin"`.
- `ATH11K_FIRMWARE_MAGIC` is the magic string expected at the start of API 2 containers.
- `enum ath11k_fw_ie_type` defines IE ids for timestamp, features, AMSS image, and M3 image.
- `enum ath11k_fw_features` currently contains only the `ATH11K_FW_FEATURE_COUNT` sentinel.
- `ath11k_fw_pre_init()` and `ath11k_fw_destroy()` are the exported firmware lifecycle hooks.

## Control Flow

There is no executable control flow in this header. Boot code calls `ath11k_fw_pre_init()` to parse or fall back from API 2 firmware and calls `ath11k_fw_destroy()` during cleanup.

## State and Persistence Behavior

The header declares constants and prototypes only. Runtime firmware state lives in `ab->fw` and is managed by `fw.c`.

## Dependencies and Integration Points

`fw.h` is included by ath11k boot/core code that needs firmware API constants and lifecycle APIs. The IE definitions must match the binary container format consumed by `fw.c` and produced by firmware packaging.

## Risks and Edge Cases

- Changing IE ids, filename, or magic string breaks compatibility with packaged firmware.
- Adding feature enum values requires corresponding parser/users and enough bitmap storage in `ab->fw.fw_features`.
- The header does not define the actual IE record struct; parser code depends on the core definition remaining compatible with these ids.

## Test Signals

Compile coverage for firmware lifecycle users and boot tests with API 2 and API 1 firmware layouts are the key signals. New feature enum values should be accompanied by parser and behavior tests.

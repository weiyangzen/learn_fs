# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/firmware.c

## Purpose
Implements firmware feature-capability bitmap helpers for WCN36xx. It maps known capability enum values to debug names and provides set/get/clear operations used after firmware capability exchange.

## Important APIs, Types, and Functions
`wcn36xx_firmware_caps_names[]` is an indexed string table keyed by `enum wcn36xx_firmware_feat_caps`. `wcn36xx_firmware_get_cap_name()` returns a printable capability name or `"UNKNOWN"` for out-of-table values. `wcn36xx_firmware_set_feat_caps()`, `wcn36xx_firmware_get_feat_caps()`, and `wcn36xx_firmware_clear_feat_caps()` operate on a four-word `u32` bitmap, translating enum values into array and bit indexes.

## Control Flow and State
Each bitmap operation validates that the capability index is in the 0..127 firmware range, logs a warning for invalid indexes, and otherwise mutates or tests one bit in the caller-owned bitmap. The file owns no persistent state except the static name table. Runtime feature state is held in `wcn->fw_feat_caps`, populated by SMD feature exchange and later read by `main.c` to decide whether scan offload is available and to print firmware capabilities.

## Dependencies and Integration Points
Includes `wcn36xx.h` for logging and integer types and `firmware.h` for the enum contract. `main.c` calls `wcn36xx_firmware_get_feat_caps()` for capability decisions and `wcn36xx_feat_caps_info()` iterates through `MAX_FEATURE_SUPPORTED` using `wcn36xx_firmware_get_cap_name()`. SMD feature exchange code fills the bitmap with values defined by `hal.h`'s `WCN36XX_HAL_CAPS_SIZE`.

## Risks and Test Signals
The helper accepts any enum value up to 127 even when the name table has gaps, so callers must not assume a printable name proves support is known to the driver. Bit operations use `1 << bit_idx`, so the bitmap must remain 32-bit words with indexes under 32 per word. Test signals include firmware feature exchange on old and new firmware, scan-offload fallback when the `SCAN_OFFLOAD` bit is absent, debug output for known capability names, and invalid-index warning coverage.

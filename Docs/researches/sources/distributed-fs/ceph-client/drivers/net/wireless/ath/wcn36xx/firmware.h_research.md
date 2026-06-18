# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/firmware.h

## Purpose
Declares the WCN36xx firmware feature-capability enum and bitmap helper API used by the driver after firmware capability exchange.

## Important APIs, Types, and Functions
`enum wcn36xx_firmware_feat_caps` assigns stable bit positions for capabilities such as MCC, P2P, DOT11AC, SCAN_OFFLOAD, BCN_FILTER, RATECTRL, WOW, FW_IN_TX_PATH, UPDATE_CHANNEL_LIST, WLAN_MCADDR_FLT, FW_STATS, extended scan/statistics features, WIFI_CONFIG, and antenna diversity. `MAX_FEATURE_SUPPORTED` is fixed at 128, matching the four-word firmware capability bitmap. The header declares `wcn36xx_firmware_set_feat_caps()`, `wcn36xx_firmware_get_feat_caps()`, `wcn36xx_firmware_clear_feat_caps()`, and `wcn36xx_firmware_get_cap_name()`.

## Control Flow and State
The header has no runtime control flow. Its state model is declarative: enum numeric values are persistent bit positions in `wcn->fw_feat_caps` and in firmware messages, not ordinary local constants that can be reordered.

## Dependencies and Integration Points
Consumed by `firmware.c`, `main.c`, and SMD feature-capability exchange paths. The enum aligns with `struct wcn36xx_hal_feat_caps_msg` in `hal.h`, whose `feat_caps[WCN36XX_HAL_CAPS_SIZE]` carries the bitset over the control channel. Higher-level mac80211 operations use these bits to choose firmware offloads or fall back to host/mac80211 behavior.

## Risks and Test Signals
Changing enum values would break compatibility with firmware. The enum has intentional gaps, for example no value 50 and no 59, so loops can traverse unsupported bit positions. Test signals are compile coverage for all users, feature exchange with firmware that advertises old and new bitsets, capability-gated behavior such as scan offload, and debug logs that map known bits to the expected names.

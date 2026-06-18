# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/cmn_defs.h

## Purpose
Provides small shared capacity constants used across ath12k multi-radio and multi-link code. It centralizes limits derived from maximum devices, radios per device, mac80211 MLD links, and MU group IDs.

## Important APIs, Types, And Functions
Defines `MAX_RADIOS` as 2, `ATH12K_MAX_DEVICES` as 3, `ATH12K_GROUP_MAX_RADIO` as devices times radios, `ATH12K_SCAN_MAX_LINKS`, `ATH12K_NUM_MAX_LINKS`, and `MAX_MU_GROUP_ID`. It includes mac80211 for `IEEE80211_MLD_MAX_NUM_LINKS`.

## Control Flow
No executable flow. These constants size arrays and bitmaps used by core, scan, MLO, vif, station, and statistics paths.

## State And Persistence
No state is stored here, but the constants determine persistent structure sizes such as per-group hardware link arrays and link pointer arrays in `core.h`.

## Dependencies And Integration Points
The file couples ath12k internal limits to mac80211 MLD link capacity. It is consumed by `core.h` and other shared ath12k headers.

## Risks
Changing these values changes ABI-like in-kernel structure sizes and may expose hidden assumptions in firmware, hardware grouping, scan link allocation, and debug stats arrays. `MAX_RADIOS` must remain consistent with `ath12k_base.pdevs[MAX_RADIOS]`.

## Test Signals
Build coverage catches most array-size fallout. Runtime validation requires multi-radio and multi-device MLO configurations, plus scan/link creation paths that use the maximum link counts.

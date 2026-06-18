# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/common.h

Purpose: Central common header for ath9k shared code, pulling in mac80211, ath core, hardware ops, and common init/beacon/debug/spectral headers while defining shared RSSI, aggregation, beacon config, and helper prototypes.

Important APIs/types: Defines block-ack buffer sizing constants, RSSI low-pass filter macros, `IEEE80211_MS_TO_TU()`, and `struct ath_beacon_config`. Declares common RX processing, crypto, channel, stream count, TX power, and crypto initialization functions.

Control flow: Driver RX/TX/channel/beacon code includes this header to get consistent helper contracts and shared macros. RSSI macros update filtered beacon RSSI only above threshold and convert fixed-point EP values back to integer RSSI.

State/persistence: `struct ath_beacon_config` is embedded in channel context state and persists beacon interval, DTIM, BMISS, creator/enabled flags, next TBTT, and programmed interval. Other macros operate on caller-owned state.

Dependencies/integration: Includes `../ath.h`, `hw.h`, `hw-ops.h`, and other ath9k common headers; exposes interfaces implemented in `common.c`.

Risks: Macro side effects require careful argument use. Beacon config stores mixed units (`beacon_interval` in TU, `intval` in usec after configuration). Header fan-in makes it sensitive to include-order changes.

Test signals: Build all common consumers, RSSI filter behavior, beacon config unit handling, and include dependency cycles.

# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00config.c

## Purpose
Implements common configuration translation from mac80211 structures to rt2x00 driver-specific configuration callbacks. It handles interface identity/synchronization, ERP/timing values, antenna diversity setup, channel/HT selection, power-save autowakeup scheduling, and common cached configuration fields.

## Important APIs, Types, And Functions
Exports `rt2x00lib_config_intf()`, `rt2x00lib_config_erp()`, `rt2x00lib_config_antenna()`, and `rt2x00lib_config()`. Private helper `rt2x00ht_center_channel()` maps HT40 center channel selection back to the hardware channel table. It fills `rt2x00intf_conf`, `rt2x00lib_erp`, and `rt2x00lib_conf` before calling `rt2x00dev->ops->lib` hooks.

## Control Flow
Interface config chooses TSF sync mode by nl80211 interface type, copies MAC/BSSID into 32-bit-aligned little-endian arrays, computes update flags, and delegates to chip code. ERP config calculates short preamble, CTS protection, slot/SIFS/PIFS/DIFS/EIFS, basic rates, beacon interval, AID, last beacon TSF, and HT opmode. Antenna config converts software diversity requests into concrete antennas, stops RX if radio is enabled, calls `config_ant`, resets link tuner, updates active antenna, and restarts RX. Main config reacts to channel and power-save changes, sets HT flags, fills RF/channel entries, calls chip `config`, updates cached band/frequency/power/retry flags, resets tuner on channel changes, and schedules autowakeup before DTIM when required.

## State And Persistence
Updates `rt2x00dev->aid`, `last_beacon`, `beacon_int`, `rf_channel`, `curr_band`, `curr_freq`, `tx_power`, `short_retry`, `long_retry`, and flags `CONFIG_HT_DISABLED`, `CONFIG_CHANNEL_HT40`, `CONFIG_POWERSAVING`, `CONFIG_MONITORING`. Antenna diversity state persists in `rt2x00dev->link.ant`.

## Dependencies And Integration Points
Called by mac80211 callbacks from `rt2x00mac_config()` and `bss_info_changed()`, by link tuning antenna changes, and by MMIO autowake. Depends on mac80211 channel definitions, `conf_is_ht*()` helpers, rt2x00 queue start/stop, workqueue scheduling, and chip-specific config hooks such as RT2800 config handlers.

## Risks
HT40 center-channel lookup warns and falls back if channel tables are inconsistent. Antenna changes stop RX around hardware programming, so failure or races can disrupt reception. Autowakeup timeout subtracts 15 jiffies-equivalent units without explicit underflow guard. MAC/BSSID clearing on NULL is intentional but can confuse multi-interface behavior if counts are stale. `conf_mutex` in link tuner protects some, not all, config interactions.

## Test Signals
Channel changes including HT20/HT40+/HT40-, AP/STA/mesh/adhoc interface configuration, antenna set/get and software diversity, power-save DTIM wake/sleep behavior, monitor mode, retry/power updates, and link tuner reset after channel/antenna changes.

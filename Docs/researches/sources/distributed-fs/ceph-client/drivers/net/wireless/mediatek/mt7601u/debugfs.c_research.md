# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/debugfs.c

## Purpose
Creates MT7601U debugfs files for live register access, temperature metadata, AMPDU/stat counters, and parsed EEPROM calibration parameters.

## Important APIs, Types, And Functions
`mt7601u_init_debugfs()` creates the directory and files. `regidx`/`regval` expose arbitrary register read/write through `mt76_reg_get()` and `mt76_reg_set()`. `mt7601u_ampdu_stat_show()` dumps accumulated RX/TX/aggregation counters and average AMPDU length. `mt7601u_eeprom_param_show()` dumps EEPROM-derived RF offset, RSSI offset, temperature/LNA values, regulatory channels, per-rate/channel power, and TSSI parameters.

## Control Flow
Initialization runs after `ieee80211_register_hw()`. Reads of show files format current in-memory driver state; `regval` writes issue immediate register writes to the address selected by `regidx`.

## State And Persistence
Reads `dev->stats`, `avg_ampdu_len`, `raw_temp`, `temp_mode`, `debugfs_reg`, and parsed `dev->ee` contents. Arbitrary `regval` writes persist in hardware state.

## Dependencies And Integration Points
Depends on Linux debugfs/seq_file helpers, EEPROM parsed data from `eeprom.c`, MAC statistics accumulated in `mac.c`, and register access wrappers.

## Risks
Writable raw register access can disrupt hardware state and should be considered a diagnostic-only interface. The EEPROM show path assumes `dev->ee` has been initialized before debugfs creation.

## Test Signals
Files appear under the wiphy debugfs directory, register read/write works, AMPDU counters update after traffic, EEPROM parameters match efuse data, and absent TSSI hides the TSSI block.

# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/phy.c

## Purpose

`phy.c` programs AR9170 PHY/RF state for channel operation. It applies large band/bandwidth-specific init tables, EEPROM modal calibration, RF bank values, synthesizer parameters, target power and regulatory conformance limits, noise-floor reads, and the channel-change sequence used by mac80211 config.

## Important APIs, Types, and Functions

Public functions are `carl9170_get_noisefloor()` and `carl9170_set_channel()`. Key internal structures are `carl9170_phy_init`, `carl9170_rf_initvals`, `carl9170_phy_freq_params`, `carl9170_phy_freq_entry`, and `enum carl9170_bw`. Important helpers include PHY init, EEPROM modal overlay, RF bank initialization, bank 4 synthesizer setup, channel coefficient lookup, interpolation helpers, frequency calibration table writes, CTL calculation, and target-power calculation.

## Control Flow

`carl9170_set_channel()` maps the nl80211 channel type to internal bandwidth, clears the current channel, cold-resets BB/ADDA, writes the PHY init table for band/bandwidth, overlays EEPROM modal values, initializes power calibration, programs RF banks, sends `FREQ_START`, configures heavy-clip base state, programs bank 4 synthesizer power values, sets HT/turbo flags, writes calibration data, computes target powers and CTL limits, updates MAC TPC, builds an `RF_INIT` firmware command with frequency and delta-slope coefficients, and handles firmware RF calibration result.

## State and Persistence Behavior

The file updates hardware PHY/RF registers, firmware RF state, `ar->channel`, `ar->ht_settings`, `ar->noise[]`, `ar->survey[channel].noise`, `ar->power_*` target arrays, `ar->heavy_clip`, `ar->chan_fail`, and `ar->total_chan_fail`. EEPROM calibration data remains read-only but drives all derived power and VPD table writes.

## Dependencies and Integration Points

It depends on EEPROM layout/constants, PHY register constants from `phy.h`, hardware bitfield helpers from `hw.h`, firmware command structs from `fwcmd.h`, mac80211 channel config, ath regulatory CTL lookup, MAC TPC programming, command execution, and register batch helpers.

## Risks and Edge Cases

The channel table in `main.c` must stay synchronized with `carl9170_phy_freq_params[]`; mismatches trigger warnings and wrong coefficients. Calibration interpolation assumes at least two valid target/calibration piers after sentinel filtering. `carl9170_set_channel()` recursively retries failed RF init, bounded by `chan_fail`; changes must preserve that limit. CTL handling currently applies heavy-clip and power limiting only for FCC-derived groups.

## Test Signals

Exercise every advertised 2 GHz and 5 GHz channel in HT20, no-HT, HT40 plus, and HT40 minus where legal. Verify RF init failures recover or trigger restart after the threshold. Check noise floor reads update survey data. Compare target power and CTL limiting against known EEPROM/regdomain fixtures. Trace register writes for PHY init, modal overrides, RF banks, heavy clip, calibration tables, turbo flags, and RF_INIT command payload.

# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/libipw_geo.c

## Purpose
Implements channel geography helpers for libipw. It stores regulatory channel maps in `struct libipw_device`, validates channels against the active band and mode, and converts between channels, frequencies, indexes, and channel flags.

## Important APIs, Types, and Functions
Exported functions are `libipw_is_valid_channel`, `libipw_channel_to_index`, `libipw_channel_to_freq`, `libipw_freq_to_channel`, `libipw_set_geo`, `libipw_get_geo`, `libipw_get_channel_flags`, and `libipw_get_channel`. `bad_channel` is a static invalid-channel sentinel returned when lookup fails.

## Control Flow
All helpers first assume the driver has initialized `ieee->geo`. Validation scans 2.4 GHz channels if `freq_band` includes `LIBIPW_24GHZ_BAND`, requiring non-invalid channels and excluding B-only channels when the current mode includes G. It then scans 5 GHz channels if `freq_band` includes `LIBIPW_52GHZ_BAND`. Frequency conversion divides input frequency by 100000 before comparing against stored MHz values, matching Wireless Extensions frequency formatting. `libipw_set_geo()` copies the country name and channel arrays into the device.

## State and Persistence Behavior
State is entirely in-memory in `ieee->geo`, with separate BG and A channel arrays, channel counts, country/name bytes, flags, and max power. No external persistence is performed here; ipw2200 populates geography from EEPROM/country data and calls `libipw_set_geo()`.

## Dependencies and Integration Points
Depends on `libipw.h` types and is used by scan rendering in `libipw_wx.c`, association/channel selection in ipw drivers, and any code needing regulatory flags. The flag values include passive-only, 802.11h, B-only, no-IBSS, uniform spreading, radar detect, and invalid.

## Risks
The lookup logic uses `channel <= LIBIPW_24GHZ_CHANNELS` to decide whether a returned index maps to BG or A arrays; this is correct for normal channel numbering but fragile if unusual channel maps are introduced. `libipw_set_geo()` trusts source channel counts and copies without bounds checks against fixed array sizes. Calling helpers before geography initialization returns invalid/zero values and can suppress scan/association behavior.

## Test Signals
Country/EEPROM geography initialization, 2.4 GHz and 5 GHz channel validation, G-mode exclusion of B-only channels, invalid/radar/passive flags in scan output, frequency-to-channel and channel-to-frequency conversions, missing geography handling, and boundary channel counts are useful signals.

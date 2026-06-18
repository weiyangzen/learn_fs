# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/cfp.c

## Purpose
`cfp.c` supplies mwifiex channel/frequency/power and data-rate helpers. It holds static tables for legacy, HT, and VHT rates, region-code to country-code mapping, and functions that convert firmware rate indexes and band settings into cfg80211/driver-visible rates. It also locates channel-frequency-power data from the registered wiphy bands and derives supported-rate lists for station, P2P, and ad-hoc modes.

## Important APIs, types, and functions
`mwifiex_11d_code_2_region()` maps firmware region codes such as `0x10`, `0x20`, `0x40`, and `0x50` to 802.11 country strings. `mwifiex_index_to_data_rate()` and `mwifiex_index_to_acs_data_rate()` decode firmware rate index plus HT/VHT metadata into rates in 500 kb/s-style firmware units. `mwifiex_get_active_data_rates()` returns either current BSS rates or supported rates depending on connection state. `mwifiex_get_cfp()` searches `wiphy->bands[]` for a usable channel/frequency and stores the result in `priv->cfp`. `mwifiex_is_rate_auto()` checks whether the configured rate bitmap contains more than one active slot. `mwifiex_get_rates_from_cfg80211()` converts a cfg80211 scan request rate mask to mwifiex scan rates. `mwifiex_get_supported_rates()` chooses a rate table based on station/P2P versus ad-hoc mode and band flags. `mwifiex_adjust_data_rate()` maps RX rate/HT info into histogram indexes.

## Control flow
Rate conversion first tests format bits. For VHT, it clamps MCS to 0-9, extracts bandwidth and guard interval from `ht_info`, chooses NSS based on the high nibble of the index, and indexes the AC MCS table. For HT, it handles MCS32 specially, then indexes 20/40 MHz LGI/SGI tables for MCS 0-15, with fallback to the first legacy rate. For non-HT, it bounds the index into `mwifiex_data_rates`.

Channel lookup in `mwifiex_get_cfp()` converts a mwifiex band into a cfg80211 band, rejects missing bands, skips disabled channels, and matches either exact center frequency or channel number, with `FIRST_VALID_CHANNEL` as a wildcard for the first valid channel. Supported-rate selection switches on `adapter->config_bands` for infrastructure/P2P and `adapter->adhoc_start_band` for ad-hoc, copying a zero-terminated table into the caller buffer with `mwifiex_copy_rates()`.

## State and persistence behavior
Most data is static read-only lookup state. Mutable state updates are limited and explicit: `mwifiex_get_cfp()` writes `priv->cfp.channel`, `priv->cfp.freq`, and `priv->cfp.max_tx_power`; `mwifiex_get_rates_from_cfg80211()` reads `priv->scan_request`; supported-rate selection reads `adapter->config_bands` and `adapter->adhoc_start_band`; rate-auto reads `priv->bitmap_rates`. No persistent storage is touched.

## Dependencies and integration points
This file depends on cfg80211 band/channel structures populated by `cfg80211.c`, firmware band constants from mwifiex headers, scan request state from cfg80211, and helper macros such as `mwifiex_band_to_radio_type()`, `mwifiex_copy_rates()`, and capability flags from `main.h`/`fw.h`. `cfg80211.c` uses the country-code mapper during regulatory hints and the channel/rate helpers during scan, association, station info, and histogram reporting.

## Risks and test signals
Incorrect table indexes or bit interpretation can report bad data rates, break rate masks, or corrupt histogram buckets. Channel lookup depends on wiphy band registration and regulatory-disabled flags, so regulatory changes can make expected channels unavailable. Test signals include connecting on 2.4 GHz and 5 GHz, HT20/HT40/VHT rate reporting, scan requests with custom rate masks, ad-hoc band selection, regulatory country changes, and debugfs histogram rate buckets. Boundary cases should cover MCS32, 1x1 versus 2x2, disabled channels, missing 5 GHz band, and out-of-range firmware indexes.

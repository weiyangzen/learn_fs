# sources/distributed-fs/ceph-client/net/wireless/of.c

## Purpose

`of.c` applies device-tree frequency limits to a wiphy. It reads the optional `ieee80211-freq-limit` property, validates pairs of start/end kHz values, and disables any advertised channels whose 20 MHz operating bandwidth does not fit within one of the declared ranges.

## Important APIs, Types, and Functions

- `wiphy_read_of_freq_limits()` is exported for drivers/core code to call after wiphy bands are populated.
- `wiphy_freq_limits_apply()` iterates all `wiphy->bands[]` and marks out-of-range channels with `IEEE80211_CHAN_DISABLED`.
- `wiphy_freq_limits_valid_chan()` checks whether a channel center frequency with a fixed 20 MHz bandwidth fits a parsed `ieee80211_freq_range`.
- Device-tree helpers include `dev_of_node()`, `of_find_property()`, and `of_prop_next_u32()`.

## Control Flow

The exported function obtains the wiphy device, exits if no OF node/property exists, and validates that the property length is non-zero, u32-aligned, and composed of start/end pairs. It allocates an array of frequency ranges, parses each pair, rejects zero or inverted ranges, then applies the ranges. Cleanup always frees the temporary array and logs parse/allocation errors through the device.

## State and Persistence Behavior

The parsed range array is temporary. Persistent effects are direct mutations of `struct ieee80211_channel.flags`: channels outside the OF limits are permanently disabled for the registered wiphy unless later code explicitly rebuilds or restores channel flags. The code skips already disabled channels and never re-enables anything.

## Dependencies and Integration Points

The file depends on Linux OF/property APIs, cfg80211 frequency helpers, and `core.h`. It integrates with driver registration paths that call `wiphy_read_of_freq_limits()` and with later regulatory processing, which sees OF-disabled channels as part of each channel's flag baseline.

## Risks and Edge Cases

The property format is strict; malformed length or invalid ranges abort the whole application. The check uses a fixed 20 MHz bandwidth, so very narrow channels are not specially handled here. Because the function only disables channels, an overly restrictive device-tree property can remove channels even if regulatory data would otherwise allow them.

## Test Signals

Device-tree tests should cover missing property, bad length, zero/inverted ranges, multiple valid ranges, and mixed bands. Runtime signals include `pr_debug()` lines for disabled frequencies and observing `IEEE80211_CHAN_DISABLED` in wiphy channel dumps or `iw list`.

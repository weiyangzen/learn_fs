# sources/distributed-fs/ceph-client/net/mac80211/wbrf.c

## Purpose
`wbrf.c` bridges mac80211 channel usage to AMD ACPI WBRF, the Wi-Fi Band Exclusion interface. It detects whether the parent device supports WBRF producer notifications and adds/removes frequency ranges for active WLAN channel definitions.

## Important APIs, Types, And Functions
The public functions are `ieee80211_check_wbrf_support()`, `ieee80211_add_wbrf()`, and `ieee80211_remove_wbrf()`. Internal helpers are `get_chan_freq_boundary()` and `get_ranges_from_chandef()`. Important types are `struct ieee80211_local`, `struct cfg80211_chan_def`, `struct wbrf_ranges_in_out`, and ACPI WBRF record operations `WBRF_RECORD_ADD` and `WBRF_RECORD_REMOVE`.

## Control Flow
Support detection reads `local->hw.wiphy->dev.parent` and sets `local->wbrf_supported` from `acpi_amd_wbrf_supported_producer()`. Add/remove calls return immediately when unsupported, convert the supplied chandef into one or two frequency ranges, and call `acpi_amd_wbrf_add_remove()` on the parent device. `80+80` MHz channel definitions produce two ranges; other widths produce one.

## State And Persistence
The only local state is the boolean `local->wbrf_supported`. The actual exclusion records are external ACPI/platform state managed by the WBRF subsystem and are added or removed by matching calls during channel-use transitions.

## Dependencies And Integration Points
This file depends on `linux/acpi_amd_wbrf.h`, `linux/units.h`, cfg80211 chandef width helpers, and mac80211 local state. It is integrated by channel context/channel switch paths that notify WBRF when WLAN operating ranges become active or inactive.

## Risks And Edge Cases
The code assumes a valid wiphy parent device after support detection; add/remove do not recheck `dev` for NULL. Frequency conversion multiplies MHz to kHz to Hz in `u64`, which is safe for WLAN frequencies but depends on callers passing MHz units. Correct add/remove pairing is essential; leaked WBRF records can leave stale platform exclusion ranges.

## Test Signals
Useful tests/mock traces verify support detection with missing wiphy/parent, 20/40/80/160/320 MHz range boundaries, 80+80 dual ranges, and balanced ACPI add/remove calls during channel assignment and teardown.

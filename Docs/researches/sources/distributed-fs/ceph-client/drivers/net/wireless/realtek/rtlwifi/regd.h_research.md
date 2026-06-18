# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/regd.h

## Purpose
Declares regulatory structures, country-code enums, channel flag compatibility aliases, and rtlwifi regulatory APIs.

## Important APIs, Types, And Functions
`struct country_code_to_enum_rd` maps Realtek codes to ISO alpha2 names. `enum country_code_type_t` includes FCC, IC, ETSI, Spain, France, MKK variants, Israel, TELEC, MIC, global/world-wide plans, and 5 GHz-all world-wide. APIs are `rtl_regd_init()` and `rtl_reg_notifier()`.

## Control Flow
Initialization calls `rtl_regd_init()` after efuse is read; cfg80211 later invokes `rtl_reg_notifier()`.

## State And Persistence
No storage. Enum values are stored in `rtlpriv->regd.country_code` and drive wiphy channel flags.

## Dependencies And Integration Points
Requires cfg80211/mac80211 regulatory types. Aliases map old `NO_IBSS` and passive-scan naming to `IEEE80211_CHAN_NO_IR`.

## Risks
Enum values are coupled to implementation tables/switches. New channel plans require coordinated updates.

## Test Signals
Build against current kernel flag names, initialize mapped enum values, and verify notifier wiring.

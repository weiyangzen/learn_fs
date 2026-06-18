<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/regd.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/regd.h

Purpose: Declares ath regulatory constants, country codes, CTL groups, EEPROM regulatory flags, helper structs, and exported regulatory APIs.

Important APIs/types/functions: Defines `enum ctl_group`, CTL constants, `CTRY_*` country code enum values, `COUNTRY_ERD_FLAG`, `WORLDWIDE_ROAMING_FLAG`, world SKU masks, `struct country_code_to_enum_rd`, and prototypes for `ath_regd_init()`, `ath_reg_notifier_apply()`, `ath_regd_get_band_ctl()`, `ath_is_world_regd()`, `ath_is_49ghz_allowed()`, and `ath_regd_find_country_by_name()`.

Control flow: No executable flow; it defines the contract implemented by `regd.c`.

State and persistence: Provides symbolic values that represent EEPROM regulatory state and cfg80211-facing regulatory state.

Dependencies and integration points: Includes nl80211/cfg80211 and `ath.h`; used by ath drivers during wiphy registration and regulatory notifications.

Risks and test signals: Risks include stale or missing country code definitions and typo-level API mismatch. Test signals are compile coverage and correct mapping behavior through `regd.c` tests or runtime regulatory logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/regd.h -->

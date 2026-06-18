<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/regd.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/regd.c

Purpose: Implements shared ath regulatory-domain initialization, world regulatory rules, country/regpair lookup, dynamic country updates, channel flag adjustments, and CTL band lookup.

Important APIs/types/functions: Exports `ath_is_world_regd()`, `ath_is_49ghz_allowed()`, `ath_regd_find_country_by_name()`, `ath_reg_notifier_apply()`, `ath_regd_init()`, and `ath_regd_get_band_ctl()`. Internal helpers include `ath_world_regdomain()`, `ath_reg_apply_radar_flags()`, `ath_reg_apply_world_flags()`, `ath_reg_apply_beaconing_flags()`, `ath_reg_apply_ir_flags()`, `__ath_reg_dyn_country()`, `ath_regd_is_eeprom_valid()`, `ath_get_regpair()`, and `__ath_regd_init()`.

Control flow: Initialization sanitizes and validates EEPROM regulatory data, maps country or regdomain values to a `reg_dmn_pair_mapping`, sets alpha2, stores a world-roaming copy if needed, installs a wiphy notifier, applies a custom world regdomain, and forces radar/world flags. The notifier always reapplies radar flags, then reacts to core/driver/user/country-IE hints, optionally dynamically mapping alpha2 to EEPROM country/regdomain state and relaxing no-IR flags according to world-domain rules.

State and persistence: Mutates `struct ath_regulatory` fields (`current_rd`, `country_code`, `regpair`, `alpha2`, `region`) and wiphy channel/regulatory flags. State is runtime only but derived from EEPROM-provided regulatory data.

Dependencies and integration points: Uses cfg80211/mac80211 regulatory APIs, tables from `regd_common.h`, constants from `regd.h`, `ath_common`, kernel config gates for dynamic user hints, and wiphy channel structures.

Risks and test signals: Regulatory correctness is high risk: wrong no-IR/radar flags can violate domain rules. Edge cases include invalid EEPROM codes, India DFS range exception, world roaming restoration, and user hints denied for US/Japan. Test signals include regdomain changes by core/user/country IE, channel flag audits, CTL lookup per band, and EEPROM invalid/sanitized logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/regd.c -->

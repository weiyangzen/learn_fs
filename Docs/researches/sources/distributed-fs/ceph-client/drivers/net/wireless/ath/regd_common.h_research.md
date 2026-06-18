<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/regd_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/regd_common.h

Purpose: Supplies the shared regulatory mapping tables used by ath regulatory code: enum regdomain IDs, regdomain-to-CTL mappings, and country-to-regdomain mappings.

Important APIs/types/functions: Defines `enum EnumRd`, static `regDomainPairs[]`, and static `allCountries[]`.

Control flow: No executable control flow, but `regd.c` linearly searches these tables when validating EEPROM data, mapping alpha2/country codes, selecting regpairs, and deriving CTL values.

State and persistence: Static compile-time lookup data only. Runtime state in `ath_regulatory` references entries from these tables.

Dependencies and integration points: Included by `regd.c`; table value meanings are tied to constants in `regd.h` and cfg80211 regulatory behavior.

Risks and test signals: Regulatory table errors have compliance impact. Risks include duplicate/legacy country entries, missing new countries, and static table definitions in a header if included by more than one C file. Test signals are country alpha2 lookup, EEPROM regpair validation, CTL selection for 2 GHz/5 GHz, and regulatory selftests if available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/regd_common.h -->

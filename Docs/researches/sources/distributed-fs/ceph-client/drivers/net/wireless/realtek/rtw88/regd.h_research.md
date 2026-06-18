# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/regd.h

## Purpose
This header declares the rtw88 regulatory interface and legacy channel-plan constants used by the regulatory and transmit-power code. It gives other rtw88 modules a compact API for regulatory initialization, regulatory hints, current TX-power regulatory group lookup, alternative-group lookup, and China/SRRC detection.

## Important APIs, Types, And Functions
The header aliases older mac80211 channel flags (`IEEE80211_CHAN_NO_IBSS`, `IEEE80211_CHAN_PASSIVE_SCAN`) to `IEEE80211_CHAN_NO_IR`. `enum rtw_chplan_id` lists Realtek channel-plan IDs seen in efuse/vendor data, including world, FCC, ETSI, MKK, IC, KCC, ACMA, CN-related, and Realtek-defined plans. `struct country_code_to_enum_rd` represents a country-code-to-domain mapping pair. `enum country_code_type` names legacy domain categories and terminates with `COUNTRY_CODE_MAX`.

The exported function declarations are `rtw_regd_init()`, `rtw_regd_hint()`, `rtw_regd_get()`, `rtw_regd_has_alt()`, and `rtw_regd_srrc()`.

## Control Flow
The header does not implement control flow. It defines call points used by probe and registration: initialize before `ieee80211_register_hw()`, send a hint after registration, then query current regulatory values during PHY/TX-power operation.

## State And Persistence
No state is stored here. The enums and constants must remain stable because efuse/channel-plan values and vendor-derived tables may encode these IDs persistently in hardware data. The API functions operate on `struct rtw_dev` state managed in `regd.c`.

## Dependencies And Integration Points
The declarations assume rtw88 core types such as `struct rtw_dev` and kernel wireless channel flags are visible through including context. `regd.c` implements the functions, while PHY and transmit-power code query the current regulatory group and alternate groups. The channel-plan IDs also document the efuse-facing vocabulary used by adjacent efuse parsing and power-limit code.

## Risks
Because this header mixes historical channel-plan constants with the current regulatory API, unused-looking values may still be hardware or vendor-data contracts. Removing or renumbering enum values would risk misinterpreting efuse/channel-plan data. The legacy channel flag aliases also hide API churn; call sites should not infer old IBSS/passive-scan semantics beyond `NO_IR`.

## Test Signals
Build coverage is the primary signal for declarations. Runtime signals come from successful probe-time `rtw_regd_init()`/`rtw_regd_hint()` flow, correct power-limit lookup through `rtw_regd_get()`, and chip code using `rtw_regd_srrc()` or `rtw_regd_has_alt()` without out-of-range values.

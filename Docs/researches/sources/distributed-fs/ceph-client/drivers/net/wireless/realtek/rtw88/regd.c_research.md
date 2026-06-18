# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/regd.c

## Purpose
This file implements rtw88 regulatory-domain management. It maps ISO alpha-2 country codes to Realtek transmit-power regulatory groups for 2.4 GHz and 5 GHz, initializes cfg80211 regulatory behavior before hardware registration, handles later regulatory notifications, updates PHY adaptivity and transmit power when the regulatory domain changes, and exposes helpers for current regulatory selection and alternative power-limit groups.

## Important APIs, Types, And Functions
The large `rtw_reg_map[]` table maps countries to `struct rtw_regulatory` entries using `COUNTRY_REGD_ENT()`, with `rtw_reg_ww` as the worldwide fallback. `rtw_regd_init()` installs `wiphy->reg_notifier`, detects whether efuse contains a valid country, sets `REGULATORY_STRICT_REG` and `REGULATORY_COUNTRY_IE_IGNORE` for programmed domains, initializes `rtwdev->regd`, and applies channel capability limits. `rtw_regd_hint()` sends `regulatory_hint()` after `ieee80211_register_hw()` when efuse programmed a country.

Runtime handling is in `rtw_regd_notifier()`, driven by `rtw_regd_state_hdl()` and per-state handlers for worldwide, programmed, and user-setting modes. Public helpers are `rtw_regd_get()` for the active 2G/5G tx-power group, `rtw_regd_srrc()` for China/SRRC detection, and `rtw_regd_has_alt()` for mapping special groups such as IC, KCC, ACMA, CN, Qatar, Mexico, UK, and Ukraine to fallback groups.

## Control Flow
Before mac80211 registration, `rtw_regd_init()` checks efuse country code through `rtw_reg_find_by_name()`. A recognized code moves state to `RTW_REGD_STATE_PROGRAMMED`, configures strict regulatory flags, and later `rtw_regd_hint()` asks cfg80211 to apply that country. An unrecognized code stays worldwide.

When cfg80211 calls the notifier, the current state chooses the transition rule. Worldwide mode accepts user country requests and moves to setting mode when the requested domain is not worldwide. Programmed mode accepts only the driver-initiated request matching the efuse country. Setting mode accepts user requests and returns to worldwide if the requested alpha2 maps to the worldwide fallback. Accepted requests are applied under `rtwdev->mutex`, update `rtwdev->regd`, call `rtw_phy_adaptivity_set_mode()`, and recompute TX power for `hal->current_channel`.

## State And Persistence
The persistent software state is `rtwdev->regd`, containing the state enum, a pointer to the selected `struct rtw_regulatory`, and the DFS region from cfg80211. The file also mutates `wiphy->regulatory_flags` to ignore country IEs or clear that ignore flag when returning to worldwide. Hardware-observable state is applied indirectly through PHY adaptivity and TX power reprogramming. Channel flags can be permanently constrained for the lifetime of the registered wiphy when efuse hardware capability lacks 80 MHz support.

## Dependencies And Integration Points
This code depends on cfg80211/mac80211 regulatory APIs (`struct wiphy`, `struct regulatory_request`, `regulatory_hint()`), rtw88 core state in `main.h`, logging in `debug.h`, and PHY functions from `phy.h`. `rtw_regd_get()` feeds transmit-power-limit selection elsewhere in rtw88, and `rtw_regd_srrc()` lets PHY/coexistence code identify China-specific behavior. `rtw_regd_apply_hw_cap_flags()` integrates efuse hardware capability with `wiphy->bands`.

## Risks
Regulatory correctness is high impact. Wrong country mapping, fallback behavior, or state transitions can allow invalid channels or power levels, or unnecessarily restrict operation. The handler table indexes by `rtwdev->regd.state`, so invalid state values would be unsafe. `rtw_regd_has_alt()` indexes `rtw_regd_alt[regd]` without a local bounds check and relies on callers passing values below `RTW_REGD_MAX`. The country table is static and can drift from current regulatory requirements. Mutating wiphy flags in notifier paths must stay consistent with cfg80211 expectations.

## Test Signals
Test with efuse programmed to a valid country, efuse unset/invalid, user regulatory changes, worldwide fallback, and country changes while associated. Signals include expected cfg80211 regulatory events, correct `rtwdev->regd` state transitions, correct `REGULATORY_COUNTRY_IE_IGNORE` behavior, TX power table selection through `rtw_regd_get()`, adaptivity updates, and no 80 MHz channel exposure when efuse hardware capability lacks 80 MHz.

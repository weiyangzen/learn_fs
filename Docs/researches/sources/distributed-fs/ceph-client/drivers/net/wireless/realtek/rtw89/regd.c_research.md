# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/regd.c

## Purpose

`regd.c` is the rtw89 regulatory-domain policy bridge between cfg80211/mac80211, Realtek firmware regulatory tables, efuse country programming, ACPI platform policy, and chip transmit-power programming. It maps alpha2 country codes to Realtek regulatory power domains for 2.4, 5, and 6 GHz; applies platform blocks for UNII-4 and 6 GHz operating classes; installs the wiphy regulatory notifier; and recalculates 6 GHz power/TPE limits when links become active or inactive.

## Important APIs, Types, And Functions

`COUNTRY_REGD()` builds `struct rtw89_regd` rows for `rtw89_regd_map[]`; `rtw89_ww_regd` is the worldwide fallback. Public entry points are `rtw89_regd_get_string()`, `rtw89_regd_setup()`, `rtw89_regd_init_hint()`, and `rtw89_reg_6ghz_recalc()`. The installed cfg80211 callback is `rtw89_regd_notifier()`. Key helpers include country lookup/indexing, ACPI policy setup for UNII-4 and 6 GHz, policy application, TAS and antenna-gain gates, and TPE/power-type recalculation.

## Control Flow

`rtw89_regd_setup()` selects either firmware ELM regulatory data or the built-in map, initializes default 6 GHz power state, applies ACPI rule policy, then configures UNII-4 and 6 GHz policy before assigning `wiphy->reg_notifier`. `rtw89_regd_init_hint()` honors known efuse country codes by setting strict regulatory flags and issuing `regulatory_hint()`. Runtime notifications enter `rtw89_regd_notifier()`, which locks the wiphy, leaves power save, updates country state unless efuse-programmed, applies all policies, and calls `rtw89_core_set_chip_txpwr()`.

6 GHz recalculation first updates per-link and aggregate AP power type, then computes aggregate TPE constraints from active 6 GHz links. That ordering is explicit because TPE handling depends on standard-power status.

## State And Persistence Behavior

State lives under `rtwdev->regulatory`, plus per-link `reg_6ghz_power` and `reg_6ghz_tpe`. Inputs are efuse country code, firmware regulatory ELMs, cfg80211 requests, and ACPI DSM results. The code can mutate `wiphy->bands[]`, channel disabled flags, and regulatory flags for the lifetime of the device; it does not persist to disk.

## Dependencies And Integration Points

The file integrates with cfg80211/mac80211, Realtek ACPI DSM helpers, power-save handling, TAS, antenna-gain policy, and core TX power programming. ACPI policy blobs are explicitly freed with `kfree()`.

## Risks

Pointer identity with `rtw89_ww_regd` and pointer subtraction inside active regulatory maps are important invariants. 6 GHz band removal frees wiphy band data, so later paths must tolerate a missing 6 GHz band. Fixed TPE offsets encode regulatory assumptions. Policy changes must refresh transmit power.

## Test Signals

Use `RTW89_DBG_REGD` logs, efuse-country vs worldwide tests, cfg80211 user/country-IE initiator tests, ACPI allow/block lists including `EU`, UNII-4 channel disabling, 6 GHz SP/VLP blocking, invalid TPE rejection, and verification that TX power is recomputed on aggregate regulatory changes.

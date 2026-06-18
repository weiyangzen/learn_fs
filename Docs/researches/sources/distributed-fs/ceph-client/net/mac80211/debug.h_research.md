# sources/distributed-fs/ceph-client/net/mac80211/debug.h

## Purpose

`debug.h` centralizes mac80211 debug logging macros. It gates subsystem-specific debug output behind Kconfig symbols and provides uniform prefixes for interface, link, link ID, and wiphy messages. It is used by mac80211 code that wants compile-time selectable debug traces without hand-coding `pr_debug()`, `wiphy_debug()`, or interface names repeatedly.

## Important APIs, Types, And Functions

The file defines boolean compile-time flags such as `MAC80211_OCB_DEBUG`, `MAC80211_IBSS_DEBUG`, `MAC80211_PS_DEBUG`, `MAC80211_HT_DEBUG`, mesh-related debug flags, `MAC80211_TDLS_DEBUG`, `MAC80211_STA_DEBUG`, and `MAC80211_MLME_DEBUG`. With `CONFIG_MAC80211_VERBOSE_DEBUG` enabled it declares `__sdata_info()`, `__sdata_dbg()`, `__sdata_err()`, and `__wiphy_dbg()` and routes the `_sdata_*` and `_wiphy_dbg` macros to those helpers. Otherwise the macros map to `wiphy_info`, `wiphy_dbg`, `wiphy_err`, and their `struct wiphy` variants.

The main consumer-facing macros are `sdata_info`, `sdata_err`, `sdata_dbg`, `link_info`, `link_err`, `link_err_once`, `link_id_info`, `link_dbg`, and specialized families such as `ht_dbg`, `ibss_dbg`, `ps_dbg`, `mpl_dbg`, `mpath_dbg`, `mhwmp_dbg`, `msync_dbg`, `mcsa_dbg`, `mps_dbg`, `tdls_dbg`, `sta_dbg`, `mlme_dbg`, and `mlme_link_id_dbg`.

## Control Flow

There is no runtime control flow beyond macro expansion. At compile time, each specialized macro embeds a boolean debug flag into `_sdata_dbg()` or `_link_id_dbg()`. In verbose-debug builds, helper functions can decide whether to print and can include richer interface context. In normal builds, output routes directly to wiphy logging helpers and the `print` argument controls debug printing. Link macros derive `sdata` and `link_id` from `struct ieee80211_link_data`; `link_err_once()` uses `net_ratelimit()` to suppress repeated errors.

## State And Persistence

The file stores no state. It reads stable fields such as `sdata->local->hw.wiphy`, interface names, and link IDs only when a macro is evaluated. Compile-time Kconfig settings determine which calls remain meaningful. There is no persistence.

## Dependencies And Integration Points

It depends on `ieee80211_i.h` for mac80211 internal types and on kernel wiphy logging helpers. Other files in this group use these macros for reservation failures and driver operation diagnostics, especially `chan.c` and broader MLME/channel-switch code.

## Risks

Because this is macro-heavy, side-effecting macro arguments must be avoided by callers. Debug category flags are compile-time choices, so missing Kconfig coverage can make expected traces silent. Link macros assume valid `link` or `sdata` pointers and are not defensive beyond their own formatting decisions. `link_err_once()` is global-ratelimit based and can hide repeated per-link failures during stress.

## Test Signals

Build coverage should include verbose and non-verbose debug configurations plus individual debug-category Kconfig combinations. Runtime signals are correct prefixes for interface/link messages, no format warnings from `__printf` declarations, and no unexpected evaluation warnings when macros are compiled out or debug flags are false.

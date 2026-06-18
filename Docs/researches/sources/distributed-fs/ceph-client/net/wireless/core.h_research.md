# sources/distributed-fs/ceph-client/net/wireless/core.h

## Purpose
This header defines cfg80211 internal data structures and function prototypes shared by wireless core files. It is the private contract between cfg80211 lifecycle, scan, MLME, SME, regulatory, channel, mesh, IBSS, PMSR, and debugfs code.

## Important APIs, types, and functions
`struct cfg80211_registered_device` wraps driver ops, global list linkage, rfkill, regulatory state, wiphy index, opencount, beacon registrations, scan/BSS state, scheduled scans, current command info, connection/event work, DFS/background CAC work, management registration lock/work, wiphy work queue, suspend state, and the embedded `struct wiphy`.

Other key structures include `cfg80211_scan_request_int`, `cfg80211_internal_bss`, `cfg80211_event`, `cfg80211_cached_keys`, `cfg80211_beacon_registration`, `cfg80211_cqm_config`, and `cfg80211_colocated_ap`. Inline helpers include `wiphy_to_rdev()`, `cfg80211_rdev_free_wowlan()`, `cfg80211_assign_cookie()`, `cfg80211_hold_bss()`, `cfg80211_unhold_bss()`, `cfg80211_has_monitors_only()`, and `elapsed_jiffies_msecs()`.

The header declares internal APIs for wiphy lookup, netns switching, wdev registration, IBSS, mesh, AP stop, MLME auth/assoc/deauth/disassoc/mgmt TX, SME events, scan, scheduled scan, DFS, CAC, monitor channels, interface counts, leave paths, NAN/P2P stop, PMSR, MLO link removal/reconfiguration, and colocated AP parsing under KUnit.

## Control flow
The header does not execute runtime flow, but it defines the shared state machine vocabulary. Registered devices own wdevs, BSS entries, work items, and driver ops. Mode-specific code updates pieces of `wireless_dev` state and calls prototypes declared here while core code handles registration, locking, and teardown.

## State and persistence
All state described here is in-kernel memory. RCU, spinlocks, RTNL, and the wiphy mutex protect different fields. No durable persistence exists.

## Dependencies and integration points
It depends on kernel networking headers, debugfs, rfkill, generic netlink, public cfg80211 headers, and `reg.h`. Every cfg80211 internal source file relies on this header for type layout and prototypes.

## Risks
Because this is a private central header, struct layout or locking-contract changes have broad blast radius. Misdocumented ownership of BSS refs, wdev lists, or work items can create leaks or use-after-free bugs. KUnit-only exports must stay aligned with test configuration.

## Test signals
Compile coverage across config variants is essential. Runtime signals include lockdep, KASAN/KCSAN, BSS refcount assertions, wiphy work cancellation tests, WoWLAN cleanup, and MLO link state tests.

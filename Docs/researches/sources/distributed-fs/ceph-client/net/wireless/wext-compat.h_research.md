# sources/distributed-fs/ceph-client/net/wireless/wext-compat.h

## Purpose
`wext-compat.h` is the local declaration header for cfg80211 Wireless Extensions compatibility glue. It exposes the managed-mode and IBSS WEXT helper functions implemented in neighboring files, declares common WEXT MLME/genie/frequency helpers, and publishes the `cfg80211_wext_handler` handler table implemented by `wext-compat.c`.

## Important APIs And Types
The header includes `<net/iw_handler.h>` and `<linux/wireless.h>` because all declared functions use WEXT request types such as `struct iw_request_info`, `union iwreq_data`, `struct iw_freq`, `struct iw_point`, and `struct sockaddr`, along with `struct net_device`.

IBSS declarations are:

- `cfg80211_ibss_wext_siwfreq` / `cfg80211_ibss_wext_giwfreq`
- `cfg80211_ibss_wext_siwap` / `cfg80211_ibss_wext_giwap`
- `cfg80211_ibss_wext_siwessid` / `cfg80211_ibss_wext_giwessid`

Managed station declarations are:

- `cfg80211_mgd_wext_siwfreq` / `cfg80211_mgd_wext_giwfreq`
- `cfg80211_mgd_wext_siwap` / `cfg80211_mgd_wext_giwap`
- `cfg80211_mgd_wext_siwessid` / `cfg80211_mgd_wext_giwessid`

Shared declarations are `cfg80211_wext_siwmlme`, `cfg80211_wext_siwgenie`, `cfg80211_wext_freq`, and `extern const struct iw_handler_def cfg80211_wext_handler`.

## Control Flow
The header has no runtime control flow. It provides compile-time coupling between `wext-compat.c` and separate managed/IBSS compatibility implementations. `wext-compat.c` dispatches AP, ESSID, and frequency requests by interface type to the declared helper families.

## State And Persistence Behavior
The header owns no state. Its declarations expose functions that operate on `wireless_dev`, `wiphy`, and WEXT compatibility state in implementation files.

## Dependencies And Integration Points
This header is an integration contract inside `net/wireless`. It lets the common WEXT handler table call managed and IBSS specific code without duplicating declarations in each C file. The final `cfg80211_wext_handler` declaration is consumed by cfg80211 netdevice registration code to attach the legacy ioctl surface.

## Risks And Edge Cases
Prototype drift is the main risk. WEXT helper signatures must stay consistent with the handler table and implementation files. Because the header exposes legacy WEXT request structures, any modernization around MLO or nl80211-only behavior must preserve ABI expectations for existing callers or explicitly reject unsupported paths in the C implementations.

## Test Signals
Build coverage is the primary signal: all users of the declared managed/IBSS helpers and `cfg80211_wext_handler` should compile without implicit declarations. Runtime coverage comes indirectly from WEXT ioctl tests that exercise common dispatch in `wext-compat.c` and the per-mode helpers declared here.

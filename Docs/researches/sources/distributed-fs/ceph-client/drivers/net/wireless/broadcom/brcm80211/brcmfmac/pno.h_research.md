# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/pno.h

## Purpose
`pno.h` declares the scheduled-scan/PNO interface used by the cfg80211 and firmware-event portions of `brcmfmac`.

## Important APIs, types, and functions
- Constants: `BRCMF_PNO_SCAN_COMPLETE`, `BRCMF_PNO_MAX_PFN_COUNT`, and scheduled-scan min/max period limits.
- Forward declaration: `struct brcmf_pno_info`.
- Public functions: `brcmf_pno_start_sched_scan()`, `brcmf_pno_stop_sched_scan()`, `brcmf_pno_wiphy_params()`, `brcmf_pno_attach()`, `brcmf_pno_detach()`, `brcmf_pno_find_reqid_by_bucket()`, and `brcmf_pno_get_bucket_map()`.

## Control flow
The header has no implementation flow. It defines the call surface: cfg80211 setup attaches PNO state and publishes wiphy limits; scheduled-scan callbacks start/stop firmware PNO; firmware result processing can resolve request IDs and bucket maps from PNO state.

## State and persistence behavior
The header exposes `struct brcmf_pno_info` opaquely, forcing users to manage it through attach/detach and helper functions. Runtime state lives in `pno.c` and under `cfg->pno`; there is no persisted data.

## Dependencies and integration points
The declarations depend on driver types such as `struct brcmf_if`, `struct brcmf_cfg80211_info`, `struct brcmf_pno_net_info_le`, cfg80211 scheduled-scan request types, and `struct wiphy`. It integrates cfg80211-facing code with firmware result handling.

## Risks and edge cases
The opaque type keeps internals private, but callers must obey lifetime expectations: attach before start/stop/result mapping, stop all active requests before detach, and pass netinfo structures with firmware-compatible SSID/BSSID fields.

## Test signals
Compile coverage across cfg80211 and event code is the primary test signal. Runtime tests should verify attach/start/stop/detach ordering and bucket-map helpers under multiple scheduled scan requests.

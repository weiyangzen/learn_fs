# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/pno.c

## Purpose
`pno.c` implements preferred network offload and cfg80211 scheduled-scan support for `brcmfmac`. It tracks active scheduled scan requests, translates cfg80211 match sets, channels, scan plans, and random-MAC options into firmware PFN/GSCAN iovars, starts/stops firmware PNO, and maps firmware bucket results back to cfg80211 request IDs.

## Important APIs, types, and functions
- `struct brcmf_pno_info` stores up to `BRCMF_PNO_MAX_BUCKETS` live `cfg80211_sched_scan_request *` pointers and protects them with `req_lock`.
- `brcmf_pno_start_sched_scan()` stores a request and reprograms firmware PNO. On failure it removes the new request and restores any older active requests.
- `brcmf_pno_stop_sched_scan()` removes a request, clears firmware PNO state, and reprograms remaining requests if any.
- `brcmf_pno_prep_fwconfig()` computes a base scan period using `gcd()` of the first scan-plan interval for each request, fills a shared channel list, creates one firmware GSCAN bucket per request, and returns the bucket count.
- `brcmf_pno_config_sched_scans()` is the main firmware programming sequence: clean existing PFN state, set PFN parameters, configure channels, configure GSCAN buckets, set random MAC if requested, add SSID/BSSID match entries, and enable PFN.
- `brcmf_pno_add_ssid()` and `brcmf_pno_add_bssid()` issue `pfn_add` and `pfn_add_bssid` iovars.
- `brcmf_pno_set_random()` constructs `brcmf_pno_macaddr_le` from cfg80211 random address/mask and local-random bits.
- `brcmf_pno_find_reqid_by_bucket()` and `brcmf_pno_get_bucket_map()` map firmware bucket indexes and netinfo matches to request IDs/maps.
- `brcmf_pno_wiphy_params()` publishes scheduled-scan capabilities to cfg80211.

## Control flow
Attach allocates `brcmf_pno_info` under `cfg->pno`. Starting a scheduled scan appends the cfg80211 request to the in-memory request array under lock, then rebuilds all firmware PNO state from the full request set. Rebuild first disables and clears PFN, configures base PFN scanning, sets channel and bucket information, optionally programs random MAC, pushes SSID/BSSID match entries, then enables `pfn`.

Stopping a scan removes the request by `reqid`, disables/clears PFN, and, if other requests remain, performs the same full reconfiguration. Firmware result handling elsewhere can call the bucket helpers to convert firmware bucket indexes or netinfo entries into cfg80211 request IDs/bucket bitmaps.

## State and persistence behavior
PNO state is memory-resident and tied to the cfg80211 driver configuration lifetime. The module stores raw pointers to cfg80211 scheduled scan requests, not copies; it assumes cfg80211 keeps those requests valid until stopped. Firmware state is persistent inside the dongle until explicitly cleared by `pfn=0` and `pfnclear` or overwritten by a new configuration. No on-disk persistence exists.

## Dependencies and integration points
The file depends on cfg80211 scheduled-scan structs, Broadcom firmware iovar helpers (`brcmf_fil_iovar_*`), firmware layout structs from `fwil_types.h`, driver config from `cfg80211.h`, `core.h`, and scan/debug helpers. It integrates with wiphy capability setup, cfg80211 scheduled-scan start/stop callbacks, and firmware event/result decoding through bucket-map helpers declared in `pno.h`.

## Risks and edge cases
- `brcmf_pno_store_request()` checks capacity with `WARN()` before taking the mutex, so concurrent callers rely on higher-level serialization plus the mutexed write section.
- The request array stores external pointers; stale request lifetime would corrupt later matching or stop handling.
- Only `scan_plans[0].interval` is used for each request, so multi-plan cfg80211 semantics are collapsed.
- Channel aggregation can exceed `BRCMF_NUMCHANNELS`; that returns `-ENOSPC` and rolls back the current start.
- `brcmf_pno_set_random()` uses the first request with `NL80211_SCAN_FLAG_RANDOM_ADDR`; multiple active requests with different randomization needs are not independently represented.
- Full firmware reprogramming on every add/remove means transient failures can clear active PNO; start failure attempts restoration for previous requests, stop failure does not restore the removed one.
- Hidden SSID active-scan detection is based on SSID equality between match sets and request SSID list.

## Test signals
Signals include wiphy scheduled-scan limits, successful `pfn_set`, `pfn_cfg`, `pfn_gscan_cfg`, `pfn_macaddr`, `pfn_add`, `pfn_add_bssid`, and `pfn=1` iovars; rollback after an injected iovar failure; bucket-to-request ID mapping for multiple simultaneous requests; random MAC bit correctness; channel overflow behavior; and `WARN_ON(pi->n_reqs)` staying quiet during detach.

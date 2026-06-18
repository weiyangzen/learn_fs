# sources/distributed-fs/ceph-client/net/wireless/pmsr.c

## Purpose

`pmsr.c` implements nl80211 peer measurement request handling and result reporting for cfg80211. Its current measurement type is FTM ranging. The file parses nested nl80211 request attributes, validates them against `wiphy->pmsr_capa`, starts driver work through `start_pmsr`, tracks active requests on `wireless_dev`, emits result/complete netlink messages, and aborts outstanding work when a netlink port or wireless device disappears.

## Important APIs, Types, and Functions

- `nl80211_pmsr_start()` is the command entry point declared in `nl80211.h`.
- `pmsr_parse_peer()` parses one peer: MAC address, nested channel definition, request flags, AP TSF reporting, and measurement type data.
- `pmsr_parse_ftm()` validates and fills `cfg80211_pmsr_request_peer.ftm` fields, including bandwidth, preamble, ASAP/non-ASAP, burst counts, FTM-per-burst, retries, LCI/civic location, trigger/non-trigger based ranging, LMR feedback, BSS color, and RSTA support.
- `cfg80211_pmsr_report()` sends `NL80211_CMD_PEER_MEASUREMENT_RESULT` for one peer result.
- `cfg80211_pmsr_complete()` sends `NL80211_CMD_PEER_MEASUREMENT_COMPLETE`, removes the request from `wdev->pmsr_list`, and frees it if not already moved to abort cleanup.
- `cfg80211_pmsr_wdev_down()` and `cfg80211_release_pmsr()` mark requests for abort when an interface goes down or the originating netlink port is released.
- `cfg80211_pmsr_free_wk()` runs deferred abort processing under the wiphy guard.

## Control Flow

Request start first checks that the device advertises PMSR capabilities and that `NL80211_ATTR_PEER_MEASUREMENTS` contains peers. It counts peers and enforces `max_peers`, allocates a flexible `cfg80211_pmsr_request`, copies timeout and MAC randomization settings, then parses each peer. MAC randomization is rejected unless the device advertises it; otherwise the request uses the wdev address and a broadcast mask. A cookie and sender portid are assigned before dispatch to `rdev_start_pmsr()`. Only successful driver start links the request into `wdev->pmsr_list` and returns the cookie through extack.

FTM parsing starts with existing channel data and capability checks. Non-DMG bands require an explicit preamble. Capability flags gate ASAP, non-ASAP, LCI, civic location, trigger based, non-trigger based, LMR feedback, and RSTA. The parser rejects inconsistent combinations such as both trigger modes, non-EDCA modes without HE preamble, LMR feedback on EDCA ranging, BSS color on EDCA ranging, RSTA without LMR feedback, and too many FTMs per burst.

Reporting builds a nested peer-measurement response with wiphy, wdev id, cookie, peer address, status, host time, optional AP TSF, final flag, and type-specific FTM response attributes. Complete sends a simpler completion event and then carefully removes/frees the request unless abort processing has already moved it out of the active list.

Abort flow is port and device driven. `cfg80211_release_pmsr()` zeroes `nl_portid` for matching requests and schedules work. `cfg80211_pmsr_wdev_down()` zeroes all portids, synchronizes outstanding cleanup work, aborts immediately if needed, and warns if the list is not empty. `cfg80211_pmsr_process_abort()` moves zero-portid requests to a local free list under `pmsr_lock`, calls driver `abort_pmsr`, and frees them.

## State and Persistence Behavior

Active PMSR requests persist in `wdev->pmsr_list`, protected by `wdev->pmsr_lock` for list mutation and portid changes. Each request stores peers, parsed per-peer FTM settings, timeout, randomized/source MAC parameters, cookie, and originating netlink portid. Cookie assignment uses cfg80211's registered-device cookie allocator.

Request lifetime is split between normal driver completion and abort cleanup. Normal completion may race with abort processing, so `cfg80211_pmsr_complete()` only frees if the request is still present in `wdev->pmsr_list`. Aborted requests are identified by `nl_portid == 0`.

## Dependencies and Integration Points

The file depends on nl80211 nested attributes and policies, `nl80211_parse_chandef()`, `nl80211_parse_random_mac()`, `nl80211hdr_put()`, `nl80211_put_sta_rate()`, `wdev_id()`, cfg80211 cookie assignment, tracepoints, and `rdev_start_pmsr()`/`rdev_abort_pmsr()`. Drivers implement the actual ranging operation and call `cfg80211_pmsr_report()` and `cfg80211_pmsr_complete()`.

## Risks and Edge Cases

The parser reuses `info->attrs` while parsing peer channel definitions; callers must not rely on original attrs after that point. Missing `return -EINVAL` after unsupported LCI/civicloc extack messages means those flags are noted but not rejected in this code path, which may be intentional compatibility or a risk if drivers assume unsupported requests were filtered. Result messages allocate only `NLMSG_DEFAULT_SIZE`, so oversized LCI/civic location blobs can fail with rate-limited errors. Lifetime races between completion and abort are subtle and depend on list membership under spinlock.

## Test Signals

Tests should exercise unsupported PMSR, missing peer data, max peer overflow, invalid chandefs, MAC randomization support, every FTM capability gate, trigger/non-trigger combinations, result serialization for success and failure, complete events, netlink-port release abort, and wdev-down abort. Tracepoints for PMSR start/report/complete plus nl80211 event captures provide runtime confirmation.

# sources/distributed-fs/ceph-client/net/netfilter/nfnetlink_osf.c

## Purpose
`nfnetlink_osf.c` implements passive operating-system fingerprint storage and matching for IPv4 TCP SYN packets. Userspace loads and removes fingerprints through nfnetlink; xtables/nft users can match packets against the RCU-protected fingerprint lists and optionally log detected genres.

## Important APIs, Types, and Functions
The exported global database is `nf_osf_fingers[2]`, indexed by the IPv4 don't-fragment bit. Exported match APIs are `nf_osf_match()` and `nf_osf_find()`. Header parsing is centralized in `nf_osf_hdr_ctx_init()` and per-fingerprint comparison in `nf_osf_match_one()`. nfnetlink callbacks are `nfnl_osf_add_callback()` and `nfnl_osf_remove_callback()`.

Important structures include `struct nf_osf_finger`, `struct nf_osf_user_finger`, `struct nf_osf_info`, `struct nf_osf_data`, and local `struct nf_osf_hdr_ctx`.

## Control Flow, State, and Persistence
Matching first reads IPv4 and TCP headers using `skb_header_pointer()`, accepts only SYN packets, captures total length, DF bit, TCP window, and TCP option bytes. `nf_osf_match_one()` requires packet total length and TTL policy to match, validates fingerprint option size against packet option size, walks expected options in order, extracts MSS when present, and validates window size as plain, MSS multiple, MTU multiple, or modulo.

`nf_osf_match()` filters by requested genre unless logging all matches, logs matches or unknown OS messages through `nf_log_packet()`, and returns true when at least one fingerprint matches. `nf_osf_find()` returns the first matching genre/version pair.

Fingerprint add requires `CAP_NET_ADMIN`, `NLM_F_CREATE`, an exact-size fingerprint attribute, bounded option count/lengths, valid WSS mode, NUL-terminated strings, and duplicate detection. New fingerprints are appended to the DF-indexed RCU list under the nfnetlink mutex. Remove finds an exact fingerprint and deletes it with RCU freeing. Module exit unregisters the subsystem and RCU-frees all fingerprints.

## Dependencies and Integration Points
The file integrates nfnetlink subsystem `NFNL_SUBSYS_OSF`, IPv4/TCP header helpers, netfilter logging, and external match expressions/modules that call the exported OSF APIs under RCU. It is IPv4/TCP-specific and does not parse IPv6 fingerprints.

## Risks and Test Signals
Risks include option parser assumptions, MSS endian handling, duplicate exact-match semantics, RCU deletion during matching, TTL policy edge cases, and logging volume. Tests should add/remove fingerprints, reject malformed option strings and non-terminated genres, match DF/non-DF lists, exercise all WSS modes, verify TTL true/less/nocheck behavior, confirm only SYN packets match, validate unknown logging, and run concurrent match with fingerprint removal.

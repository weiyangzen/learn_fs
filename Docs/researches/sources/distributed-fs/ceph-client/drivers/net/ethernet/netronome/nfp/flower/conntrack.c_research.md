# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/conntrack.c

## Purpose
This file implements conntrack-aware TC Flower offload merging for the NFP Flower app. It recognizes pre-CT and post-CT TC rules, registers nft flow-table callbacks per zone, stores copied flow rules, merges compatible pre/post/nft rules into a single hardware flow, manages recursive multi-zone NAT/CT chains, and reports merged stats back to the original software flows.

## Important APIs, types, and functions
- `is_pre_ct_flow()` and `is_post_ct_flow()` classify TC flower rules around conntrack.
- `nfp_fl_ct_handle_pre_ct()` and `nfp_fl_ct_handle_post_ct()` add TC CT entries to zone tables and attempt TC merges.
- `nfp_fl_ct_handle_nft_flow()` handles netfilter flow-table replace/destroy/stats callbacks.
- `nfp_ct_merge_check()`, `nfp_ct_merge_act_check()`, `nfp_ct_check_meta()`, and helpers validate that overlapping masks/actions/metadata are compatible.
- `nfp_ct_do_tc_merge()` combines pre and post TC entries; `nfp_ct_do_nft_merge()` adds an nft entry and either creates a next pre-CT rule for recirculation or calls `nfp_fl_ct_add_offload()`.
- `nfp_fl_ct_add_offload()` builds the merged key/mask/action payload, adds tunnel offload references, installs metadata, inserts the flow table entry, and sends `FLOW_ADD`.
- `nfp_fl_ct_del_flow()` and cleanup helpers unwind map entries, merge entries, generated pre-CT entries, hardware offloads, copied rules, and tunnel allocations.
- `nfp_fl_ct_stats()` aggregates hardware stats from merged flows into pre/post/nft flow stats.

## Control flow
Pre-CT rules must be chain 0, contain CT/NAT action without commit, and have a goto. The first pre-CT in a zone registers an nft callback. Post-CT rules either match established CT state or represent NAT post rules with ct clear on a nonzero chain. Adding either side triggers merge attempts with the opposite side in the zone and, for wildcard post-CT zones, across all concrete zones. TC merge checks chain/goto compatibility and overlapping match fields, considering pre-CT mangle effects. NFT merge then checks action conflicts, metadata labels/mark, multi-zone compatibility, creates a three-cookie merge entry, and offloads when no further goto chain is needed.

## State and persistence
State is fully in-memory: zone rhashtable plus wildcard zone pointer, per-zone pre/post/nft lists, TC and NFT merge rhashtables, global CT cookie map, copied `flow_rule` objects, child lists linking entries to merges, cached stats, tunnel allocations, generated next-zone pre-CT entries, and hardware `nfp_fl_payload` pointers. No state persists across reload; firmware state is deleted when merge entries are cleaned.

## Dependencies and integration points
The file depends on Linux TC action/dissector APIs, netfilter flow table callbacks, rhashtable/list primitives, Flower match/action compiler helpers, metadata allocation, tunnel offload reference helpers, NFP flow xmit/delete paths, representor port accounting, and `conntrack.h` data structures.

## Risks
This is high-risk logic: it copies short-lived nft flow rules, translates nft mangle endian/order, and recursively creates pre-CT entries up to `NFP_MAX_RECIRC_CT_ZONES`. Merge correctness depends on comparing only overlapping cared bits and on accounting for NAT mangle changes. Cleanup must remove hardware flows before freeing copied rules and must avoid deadlocks when unregistering nft callbacks. Stats aggregation resets per-context counters and can double count if merge-child traversal is wrong.

## Test signals
Test pre/post classification, zone-specific and wildcard-zone merges, NAT IPv4/IPv6/tport mangles, VLAN/MPLS rejection paths, tunnel encap copied action lifetime, multi-zone recirculation limit, nft duplicate replace suppression, destroy ordering for pre/post/nft flows, hardware add/delete error unwinds, and stats requests for all three original flow types.

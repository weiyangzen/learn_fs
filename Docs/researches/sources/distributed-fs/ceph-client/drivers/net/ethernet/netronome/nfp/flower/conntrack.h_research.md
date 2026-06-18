# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/conntrack.h

## Purpose
This header declares the data model and public API for NFP Flower conntrack offload merging. It defines zone, flow-entry, TC-merge, nft-merge, and cookie-map structures used by `conntrack.c`, along with comparison macros and function prototypes used by the broader Flower classifier path.

## Important APIs, types, and functions
- `COMPARE_UNMASKED_FIELDS()` compares two flow match structures on bits cared about by both masks.
- `struct nfp_fl_ct_zone_entry` owns one CT zone's pre/post/nft flow lists and merge tables.
- `enum ct_entry_type` distinguishes pre-CT, nft, and post-CT entries.
- `struct nfp_fl_ct_flow_entry` stores a copied flow rule, cookie, netdev, chain/goto indices, stats cache, child merge links, tunnel action offset, flags, and previous recursive merge entries.
- `struct nfp_fl_ct_tc_merge` represents a compatible pre/post TC pair.
- `struct nfp_fl_nft_tc_merge` represents a TC pair plus nft flow and points at any generated hardware flow or next pre-CT entry.
- Prototypes expose CT classification, add/delete/stats handling, cleanup, nft callback handling, and recursive pre-CT creation.

## Control flow
There is no direct runtime flow in the header. It establishes the contracts used by the Flower setup path: classify a flow, route it to pre/post/nft handling, store an entry, merge compatible children, and later delete or collect stats through the cookie map.

## State and persistence
All structs describe volatile kernel state. Zone entries contain rhashtables/lists that must be initialized and destroyed by `conntrack.c`. `NFP_MAX_RECIRC_CT_ZONES` and `NFP_MAX_ENTRY_RULES` bound recursive merge state and merged-rule arrays.

## Dependencies and integration points
The header includes Linux netfilter flow-table declarations and `main.h` for Flower private types. Its extern rhashtable parameters are defined in this file's implementation or related Flower code. It is consumed by Flower classifier code to decide whether normal flow offload should be replaced by CT merge handling.

## Risks
The macro compares raw bytes of typed match structs and relies on `.key`/`.mask` pointers and structure sizes being valid. The list topology is complex: one entry may be on a zone list and also parent multiple merge lists. Incorrect initialization or cleanup order can corrupt lists. Recursive arrays are fixed-size and must be bounded by implementation checks.

## Test signals
Compile coverage should catch structure/prototype drift. Runtime signals are correct classification into CT handlers, stable add/delete under list/rhashtable debug options, recursive CT zone limit handling, and stats/delete callbacks finding the expected `nfp_fl_ct_map_entry` by cookie.

# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/abm/cls.c

## Purpose
`abm/cls.c` implements TC u32 classifier offload for the NFP Advanced Buffer Management NIC app. It accepts a constrained subset of u32 filters that classify IPv4/IPv6 DSCP class-selector bits into ABM priority bands, keeps a software list of DSCP mappings per ABM link, converts that list into a packed firmware priority map, and registers the TC block callback.

## Important APIs, types, and functions
`struct nfp_abm_u32_match` records a TC handle, target band, mask, value, and list node. `nfp_abm_u32_check_knode()` validates the supported u32 shape. `nfp_abm_find_band_for_prio()` resolves a priority through the mapping list with fallback to `alink->def_band`. `nfp_abm_update_band_map()` repacks all priority-to-band entries and sends them with `nfp_abm_ctrl_prio_map_update()`. `nfp_abm_u32_knode_replace()` adds or updates one mapping after conflict checks. `nfp_abm_u32_knode_delete()` removes one. `nfp_abm_setup_tc_block_cb()` dispatches TC block callbacks. `nfp_abm_setup_cls_block()` registers through `flow_block_cb_setup_simple()`.

## Control flow
TC block setup invokes the callback for classifier events. The callback accepts only `TC_SETUP_CLSU32`, chain 0, and IPv4/IPv6 protocols. New or replacement knodes are validated, DSCP mask/value bits are extracted at protocol-specific offsets, conflicts against existing mappings are rejected, the match is allocated or updated, the packed map is recalculated, qdisc offload state is refreshed, and the map is written to firmware. Delete events remove the match and repack the map.

## State and persistence
Runtime classifier state is the `alink->dscp_map` list and the packed `alink->prio_map` buffer. `alink->has_prio` reflects whether any DSCP mapping exists. The resulting firmware state is persisted only until firmware/driver reset through the vNIC mailbox priority map.

## Dependencies and integration points
The file depends on TC u32 offload structures, flow block callbacks, netlink extack reporting, `struct nfp_repr`, ABM state from `main.h`, qdisc offload refresh in `qdisc.c`, and control mailbox code in `ctrl.c`.

## Risks and edge cases
The supported classifier shape is intentionally narrow: no actions, no links, terminal-only, no variable offsets, no hashing, no mark matching, one key, and only high DSCP class selector bits supported by firmware. On validation or firmware update failure, replacement falls through to delete the existing mapping for that handle, which can remove prior offload state. Conflict detection is mask-overlap based and must stay consistent with firmware match semantics. The map packing depends on power-of-two `num_bands` and `num_prios` validated in control init.

## Test signals
Useful tests include TC u32 add/replace/delete for IPv4 and IPv6 DSCP masks, invalid actions/links/nonterminal/multiple-key cases with extack messages, conflicting filters, classid out of range, firmware mailbox failures, qdisc offload status transitions when the first/last mapping is added or removed, and map packing correctness across one-band and multi-band firmware descriptions.

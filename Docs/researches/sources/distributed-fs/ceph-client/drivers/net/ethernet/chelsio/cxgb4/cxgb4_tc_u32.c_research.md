# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_tc_u32.c

Purpose: implements TC `u32` classifier offload by parsing u32 keys and links into Chelsio filter specs and installing/removing hardware filters.

Important APIs/functions: `cxgb4_config_knode`, `cxgb4_delete_knode`, `cxgb4_init_tc_u32`, and `cxgb4_cleanup_tc_u32`; internal helpers `fill_match_fields` and `fill_action_fields` translate u32 selectors/actions.

Control flow: config rejects unsupported devices/protocols, reserves a free filter id by priority, validates root or linked u32 handles, records jump-table links for supported IPv4/IPv6 TCP/UDP next-header transitions, copies linked specs for child buckets, fills match fields and one supported action, sets ingress port/hitcount/type defaults, and calls `cxgb4_set_filter`. Delete searches both high-priority and normal filter tables for the cookie, validates linked-bucket ownership, deletes the filter, clears bitmaps, and recursively deletes filters associated with a deleted link handle.

State and persistence: `adapter->tc_u32` points to a variable-sized table of link entries, each with a saved partial filter spec, link handle, next-header match table, and tid bitmap. Hardware filter entries persist until deleted.

Dependencies/integration: depends on Linux TC u32 structures/actions, Chelsio filter table/TID state, parser tables in `cxgb4_tc_u32_parse.h`, and `cxgb4_filter` add/delete helpers.

Risks: u32 offload accepts a narrow selector grammar; unsupported offsets, masks, actions, or jump shapes fail. Delete path manually scans filter bitmaps and must account for multi-slot IPv6 filters on pre-T6 chips. Link table size is based on available filter IDs and allocates a bitmap per entry, so memory use grows quadratically with max filter count.

Test signals: root IPv4/IPv6 drop and redirect filters, linked TCP/UDP port matches, unsupported action rejection, duplicate link rejection, delete of link with child filters, high-priority table scanning, and memory allocation failure in `cxgb4_init_tc_u32`.

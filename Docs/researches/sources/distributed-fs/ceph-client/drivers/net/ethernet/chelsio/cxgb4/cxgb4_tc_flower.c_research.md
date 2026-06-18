# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_tc_flower.c

Purpose: implements TC flower offload by validating flower matches/actions, translating them into Chelsio `ch_filter_specification` records, creating/deleting hardware filters, and reporting hardware counters.

Important APIs/functions: `cxgb4_tc_flower_replace`, `cxgb4_tc_flower_destroy`, `cxgb4_tc_flower_stats`, `cxgb4_flow_rule_replace`, `cxgb4_flow_rule_destroy`, `cxgb4_validate_flow_actions`, `cxgb4_process_flow_actions`, `cxgb4_init_tc_flower`, and `cxgb4_cleanup_tc_flower`. Internal helpers cover match parsing, pedit/NAT mode translation, rhashtable lookup, hash-priority tracking, and periodic stats polling.

Control flow: replace validates actions and match keys, parses basic/IP/ports/VLAN/VNI/TOS fields, applies actions such as drop/pass/redirect/VLAN/pedit/queue, selects TCAM versus hash filter placement, waits for asynchronous filter set completion, then inserts the entry keyed by TC cookie. Destroy removes the rhashtable entry, deletes the hardware filter, updates hash-priority tracking, and RCU-frees the entry. Stats read filter counters and update TC stats deltas.

State and persistence: per-adapter `flower_tbl` stores `ch_tc_flower_entry` objects, with spinlock-protected stats. `flower_stats_timer` and `flower_stats_work` periodically refresh `last_used`. Hardware filter state persists until explicit delete or cleanup.

Dependencies/integration: depends on Linux flow dissector/action APIs, rhashtable/RCU/timers/workqueues, `cxgb4_filter` allocation and counter APIs, and shared `tid_info` priority bookkeeping.

Risks: only selected match keys/actions are supported, and pedit is valid only with egress redirect. NAT mode support is chip-specific. The periodic stats worker walks the table while rules can be removed, so RCU/rhashtable lifetime rules are important. Filter creation waits up to 10 seconds and must handle firmware timeout cleanly.

Test signals: TC flower add/delete/stats for IPv4/IPv6, VLAN, VNI, queue steering, redirect, pedit combinations on T5 and T6, hash versus LETCAM placement, timeout/error injection from `__cxgb4_set_filter`, and cleanup while the stats timer is active.

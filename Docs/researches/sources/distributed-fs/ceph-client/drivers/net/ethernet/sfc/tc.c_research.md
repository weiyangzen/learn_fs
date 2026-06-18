<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tc.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tc.c

## Purpose
Implements EF100/SFC TC flower offload into MAE hardware: match parsing, representor/uplink/wire mport resolution, action translation, encap-match tracking, conntrack left-hand-side rules, recirculation IDs, pedit MAC tables, rule insert/delete/stats, default switching rules, fallback actions, representor RX filters, and TC state lifecycle.

## Important APIs, Types, And Functions
- Public API: `efx_tc_flower()`, `efx_tc_flower_lookup_efv()`, `efx_tc_flower_external_mport()`, `efx_tc_configure_default_rule_rep()`, `efx_tc_deconfigure_default_rule()`, `efx_tc_insert_rep_filters()`, `efx_tc_remove_rep_filters()`, `efx_init_tc()`, `efx_fini_tc()`, `efx_init_struct_tc()`, and `efx_fini_struct_tc()`.
- Match/action machinery: `efx_tc_flower_parse_match()`, `efx_tc_flower_replace()`, `efx_tc_flower_replace_foreign()`, `efx_tc_flower_destroy()`, `efx_tc_flower_stats()`, `efx_tc_flower_action_order_ok()`, `efx_tc_mangle()`, and `efx_tc_pedit_add()`.
- Resource tables: MAC pedits, encap matches, match-action rules, LHS rules, counters, conntrack, recirc IDs, encap actions, and MAE table metadata.

## Control Flow
`efx_tc_flower()` serializes operations with `efx->tc->mutex` and dispatches replace/destroy/stats. Replace validates offload support, resolves ingress device to PF/representor or foreign tunnel device, parses flower dissector keys, adds ingress mport and recirc matches, rewrites some conntrack masks, checks MAE capabilities, then translates sequential TC actions into MAE action sets and action-set lists. Delivery actions allocate hardware action sets; mirror actions clone cursor state; redirect/drop terminate the cursor. Conntrack lookup/goto rules become LHS rules, sometimes using Outer Rule encap matches for foreign tunnel traffic. Destroy removes LHS or action rules from hardware and releases all referenced software/hardware resources.

## State And Persistence Behavior
All state is runtime and rooted in `struct efx_tc_state`: capability data, block bindings, mutex, rhashtables, recirc IDA, conntrack metadata, representor mport/filter IDs, counter flush state, default rules, fallback action-set lists, and `up` flag. Rule resources are refcounted through rhashtables and freed on destroy or defensive teardown.

## Dependencies And Integration Points
Depends on Linux TC flower/flow offload APIs, indirect device registration, VXLAN/Geneve netdev identification, representor netdev ops, MAE firmware APIs, TC counters, encap actions, conntrack offload, filters, rhashtable, IDA, waitqueues, and netlink extack reporting. EF100 NIC lifecycle calls `efx_init_struct_tc()`, `efx_init_tc()`, `efx_fini_tc()`, and `efx_fini_struct_tc()`.

## Risks And Test Signals
Action ordering and unsupported masks must reject rules before partial hardware programming leaks resources. Foreign tunnel/LHS rules have overlap constraints through pseudo encap matches. Counter stats are delta-reported and lock protected. Teardown warns if rules remain. Test signals include TC flower replace/destroy/stats on PF and representors, tunnel encap/decap via VXLAN/Geneve, conntrack goto-chain rules, VLAN push/pop, pedit MAC/TTL, delayed hardware stats, rule readiness fallback, indirect tunnel binding, default PF/wire/representor switching, and leak-free teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tc.c -->

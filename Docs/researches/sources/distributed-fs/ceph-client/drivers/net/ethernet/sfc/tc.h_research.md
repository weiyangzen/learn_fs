<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tc.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tc.h

## Purpose
Defines the TC flower offload data model for SFC MAE hardware, including match fields, action sets, encap matches, recirculation IDs, flow/LHS rules, MAE table descriptors, and the top-level `struct efx_tc_state`.

## Important APIs, Types, And Functions
- Core types: `struct efx_tc_action_set`, `struct efx_tc_match_fields`, `struct efx_tc_match`, `struct efx_tc_flow_rule`, `struct efx_tc_lhs_rule`, `struct efx_tc_state`.
- Resource types: `struct efx_tc_mac_pedit_action`, `struct efx_tc_encap_match`, `struct efx_tc_recirc_id`, `struct efx_tc_action_set_list`, `struct efx_tc_lhs_action`, and MAE table descriptor structs.
- Helpers/API declarations: `efx_tc_match_is_encap()`, `efx_ipv6_addr_all_ones()`, `efx_tc_indr_netdev_type()`, `efx_tc_flower()`, representor filter/default-rule helpers, and TC init/fini functions.

## Control Flow
The header describes the structures filled by `tc.c` during rule parsing and consumed by MAE programming helpers. Match structs carry value/mask pairs plus encap and recirc references. Action sets model MAE's fixed-order packet mutations and delivery. Top-level state groups all lookup tables and default/fallback rules used while TC offload is active.

## State And Persistence Behavior
`struct efx_tc_state` is runtime-only but long-lived for the NIC. It persists across individual TC rule operations until NIC teardown, holding rhashtables, counters, recirc ID allocation, mports, filters, default rules, fallback actions, flush state, and an `up` gate.

## Dependencies And Integration Points
Includes Linux flow offload and rhashtable APIs plus driver `net_driver.h` and TC counter definitions. It is shared by TC bindings, representor code, encap actions, conntrack, counters, MAE programming, and EF100 NIC lifecycle.

## Risks And Test Signals
Structure field semantics must stay synchronized with MAE MCDI encoders and `tc.c` parser assumptions. Refcounted table entries require matching release paths. Test signals include successful build across IPv6/no-IPv6 configs, TC rule lifecycle exercising each structure, rhashtable teardown without warnings, recirc IDA returning empty, and default/fallback rules being deconfigured before final struct teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tc.h -->

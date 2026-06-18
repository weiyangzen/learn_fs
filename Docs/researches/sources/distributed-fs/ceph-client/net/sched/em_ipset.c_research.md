
# sources/distributed-fs/ceph-client/net/sched/em_ipset.c

## Purpose

`em_ipset.c` implements an ematch that tests IPv4 or IPv6 packets against a netfilter ipset. It bridges traffic-control ematch evaluation with `ip_set_test()` using `struct xt_set_info` configuration.

## Important APIs, Types, and Functions

`em_ipset_change()` validates the fixed `xt_set_info` payload, gets a netns ipset reference by index, and copies the payload. `em_ipset_match()` determines packet family, ensures network headers are present, prepares `ip_set_adt_opt` and `xt_action_param`, temporarily pulls the skb to the network offset, resolves input/output devices under RCU, calls `ip_set_test()`, and restores the skb. `em_ipset_destroy()` releases the ipset reference and frees state.

## Control Flow

Configuration fails if the payload size is wrong or the set index is invalid. Match accepts only IPv4 and IPv6 packets. It fills ipset dimensions and flags from the saved config, uses the skb input interface if available, and returns the ipset test result as the ematch result.

## State and Persistence Behavior

Each ematch instance holds a copied `xt_set_info` and a reference to the netns ipset index. Destruction releases the reference through `ip_set_nfnl_put()`. No other persistent state is kept.

## Dependencies and Integration Points

It depends on netfilter ipset (`xt_set_info`, `ip_set_nfnl_get_byindex()`, `ip_set_test()`), IPv4/IPv6 header helpers, `nf_hook_state`, ematch core, and skb protocol helpers.

## Risks and Edge Cases

The skb pull/push around `network_offset` must be balanced. ipset currently does not use IPv6 transport header offset here, so the code uses a fixed IPv6 header length. Set index lifetime depends on correct get/put. Non-IP packets fail closed.

## Test Signals

Test IPv4 and IPv6 sets, input-interface dependent sets, invalid set index, destroy/reconfigure reference balance, truncated network headers, and non-IP packets.

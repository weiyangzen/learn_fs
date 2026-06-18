
# sources/distributed-fs/ceph-client/net/sched/em_ipt.c

## Purpose

`em_ipt.c` implements an ematch that runs selected x_tables matches from traffic control. This snapshot supports the `policy` and `addrtype` xt matches for IPv4/IPv6, allowing TC filters to reuse netfilter match logic.

## Important APIs, Types, and Functions

`struct em_ipt_match` stores the selected `xt_match`, hook, nfproto, and aligned match data. `em_ipt_change()` parses netlink attributes, validates nfproto and supported match name/revision, loads the xt match with `xt_request_find_match()`, copies match data, and calls `xt_check_match()`. `em_ipt_match()` prepares `nf_hook_state` and `xt_action_param` and calls the xt match callback. `em_ipt_destroy()` calls the xt destroy callback if present, drops the module reference, and frees state. `em_ipt_dump()` serializes the match name, hook, revision, nfproto, and match data.

## Control Flow

Configuration requires hook, match name, match data, and nfproto. `get_xt_match()` whitelists match names and invokes match-specific validators: policy revision 0 only and only on `NF_INET_PRE_ROUTING`, addrtype revision 1 only. Runtime match accepts IPv4 or IPv6 packets, ensures the relevant network header is present, resolves the incoming device under RCU, initializes hook state, and returns the xt match result.

## State and Persistence Behavior

Each ematch instance owns one `em_ipt_match` allocation and a module reference on the xt match. Match-specific internal resources are owned by x_tables and released through the match destroy callback. There is no global state beyond ematch registration.

## Dependencies and Integration Points

It depends on x_tables, IPv4/IPv6 netfilter headers, `xt_check_match()`, `xt_request_find_match()`, `nf_hook_state_init()`, ematch core, and skb protocol/header helpers. It exposes ematch kind `TCF_EM_IPT`.

## Risks and Edge Cases

Only whitelisted xt matches are supported; blindly allowing arbitrary xt modules would need stronger validation. Hook and nfproto must match what the xt module expects. Module references and match destroy callbacks must be balanced. `match_data` is aligned with `XT_ALIGN()` and dump uses `usersize` where available, so size mismatches can break round trips.

## Test Signals

Test policy and addrtype valid configs, unsupported names/revisions, wrong hook for policy, IPv4/IPv6 packets, truncated headers, dump round trips, and module unload/reload reference behavior.

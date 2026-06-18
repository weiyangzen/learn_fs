# sources/distributed-fs/ceph-client/net/sched/act_police.c

## Purpose

`act_police.c` implements the tc policing action. It enforces MTU, byte-per-second, peak-rate, packet-per-second, and estimator-based average-rate limits, returning different control actions for conforming and exceeding traffic.

## Important APIs, types, and functions

`tcf_police_init()` parses `TCA_POLICE_*`, handles rate tables and 64-bit rate attributes, installs estimators, validates fallback actions, initializes token state, and RCU-replaces `tcf_police_params`. `tcf_police_act()` performs MTU and token-bucket checks. `tcf_police_mtu_check()` handles GSO-aware length validation. `tcf_police_act_to_flow_act()` and `tcf_police_offload_act_setup()` translate policing configuration to `FLOW_ACTION_POLICE`. Dump and stats hooks serialize rates, bursts, pps fields, and estimator settings.

## Control flow

Initialization supports byte-rate/peak-rate policers or packet-per-second policers, but rejects mixing pps and byte rate in one action. Runtime first updates stats, checks EWMA average rate if configured, then validates MTU. If no rate limiter is present, conforming packets return `tcfp_result`. Otherwise it computes elapsed nanoseconds, refills normal, peak, or packet tokens under `tcfp_lock`, subtracts packet cost, and returns `tcfp_result` when enough tokens remain. Exceeded packets increment overlimit stats and return the configured exceed action.

## State and persistence

Each action has RCU configuration params plus mutable token state in `tcfp_t_c`, `tcfp_toks`, `tcfp_ptoks`, and `tcfp_pkttoks`, serialized by `tcfp_lock`. Optional rate estimator state is attached to the action's basic stats. Per-net lifecycle is standard tc action storage.

## Dependencies and integration points

It depends on qdisc rate tables, packet scheduler time conversion, GSO validation, generic rate estimators, tc action control-action validation, and flow offload.

## Risks and edge cases

Token arithmetic is timing-sensitive, especially with peak and pps modes. Estimator-only policing requires an active estimator. GSO MTU validation differs from normal packet length. Fallback `goto chain` is forbidden, and offload support depends on conform/exceed action translation. Misconfigured bursts can cause systematic drops or unintended pass-through.

## Test signals

Cover byte-rate, peak-rate, pps, estimator average rate, MTU-only, GSO MTU, conform/exceed actions, invalid mixed pps/byte-rate config, dump round trips, overlimit/drop qstats, and hardware offload translation.

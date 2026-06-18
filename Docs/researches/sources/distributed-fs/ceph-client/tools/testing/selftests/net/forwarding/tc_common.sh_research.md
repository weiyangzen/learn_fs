# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_common.sh

Purpose: small shared helper library for tc selftests. It sets `CHECK_TC=yes`, defines a configurable `TC_HIT_TIMEOUT`, and provides busywait wrappers around tc rule packet counters.

The exported functions are `tc_check_packets`, `tc_check_at_least_x_packets`, and `tc_check_packets_hitting`. Each accepts a tc location string such as `dev $h2 ingress` or `block 22`, a rule handle, and optionally a target count. They call `busywait "$TC_HIT_TIMEOUT" until_counter_is ... tc_rule_handle_stats_get "$id" "$handle"`.

Control flow is just helper invocation by other scripts. State is not mutated except through the implied read of tc statistics; the timeout can be overridden by environment or config before sourcing. Dependencies are `lib.sh` functions `busywait`, `until_counter_is`, and `tc_rule_handle_stats_get`, plus a working `tc` command because `CHECK_TC` signals the harness to require it. Risks include equality checks being brittle when extra packets arrive and timeout too short for slow/offloaded hardware paths. Test signals are the helper return codes used by caller `check_err`/`check_fail`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_police.h -->
# sources/distributed-fs/ceph-client/include/net/tc_act/tc_police.h

Purpose: Defines TC policing action parameters, token-bucket runtime state, legacy compatibility format, and locked accessors for rates and bursts.

Important APIs/types/functions: `struct tcf_police_params` stores action, result, EWMA rate, MTU, byte and packet bursts, MTU peak tokens, rate/peak/pps configs and presence flags, plus RCU head. `struct tcf_police` embeds `tc_action`, RCU params, cacheline-aligned lock, token counters, packet tokens, and last time. `tc_police_compat` mirrors old policer UAPI. Accessors return byte rate, byte burst, packet rate, packet burst, MTU, peak byte rate, EWMA rate, and rate overhead while the action lock is held.

Control flow: Runtime refills tokens from elapsed time, compares packet size/count against configured byte/packet/peak buckets, updates token state under `tcfp_lock`, and returns conform or exceed action.

State and persistence behavior: Config params are RCU-replaced and read under action lock in accessors. Mutable token state persists per action and changes for every packet.

Dependencies/integration points: Depends on `act_api.h`, psched rate configs, TC netlink dump, and `tcf_police_act`.

Risks: Burst conversion uses nanosecond arithmetic and can overflow if not bounded by setup validation. Locking must protect token state. Byte and packet modes must not be confused.

Test signals: Rate/peak/pps policing tests, token refill over time, burst conversion checks, legacy dump compatibility, replacement while traffic runs, and lockdep coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_police.h -->

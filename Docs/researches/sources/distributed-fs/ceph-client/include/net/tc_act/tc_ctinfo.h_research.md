<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_ctinfo.h -->
# sources/distributed-fs/ceph-client/include/net/tc_act/tc_ctinfo.h

Purpose: Defines TC ctinfo action state for copying conntrack metadata such as DSCP and connmark into packets or skb marks.

Important APIs/types/functions: `struct tcf_ctinfo_params` stores net namespace, action, DSCP mask/state mask, cpmark mask, zone, mode, and DSCP mask shift. `struct tcf_ctinfo` embeds `tc_action`, RCU params, and atomic stats for DSCP set/errors and cpmark set. Mode bits are `CTINFO_MODE_DSCP` and `CTINFO_MODE_CPMARK`.

Control flow: Packet action reads params, finds conntrack state in the selected zone, and applies DSCP or mark updates depending on mode bits while updating stats.

State and persistence behavior: Params are RCU-replaced; counters persist for the action instance until deletion.

Dependencies/integration points: Depends on `act_api.h` and conntrack action implementation. Exposed to TC netlink stats and `tc_wrapper.h`.

Risks: Mask/shift mistakes can overwrite unrelated DSCP or mark bits. Atomic stats must correspond to actual packet outcomes.

Test signals: DSCP and cpmark transfer tests, invalid mask validation, zone isolation, stats checks, and replace/delete concurrency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_ctinfo.h -->

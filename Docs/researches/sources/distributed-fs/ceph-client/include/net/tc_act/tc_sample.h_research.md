<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_sample.h -->
# sources/distributed-fs/ceph-client/include/net/tc_act/tc_sample.h

Purpose: Defines TC sample action state for probabilistic packet sampling to psample groups.

Important APIs/types/functions: `struct tcf_sample` embeds `tc_action`, sample rate, truncate flag, truncate size, RCU psample group pointer, group number, and list node. Accessors return rate, truncate flag, and truncate size.

Control flow: Packet action samples approximately one out of `rate` packets, optionally truncates copied packet data, and sends samples to the configured psample group while returning the configured TC action.

State and persistence behavior: Per-action state persists until deletion; psample group pointer is RCU-protected; list node supports group/action lifecycle.

Dependencies/integration points: Depends on `act_api.h`, TC sample UAPI, and `net/psample.h`; integrated with `tcf_sample_act`.

Risks: Truncation size must not exceed packet bounds. Group lifetime and RCU access must be correct. Sampling rate zero or invalid values must be rejected at setup.

Test signals: Sampling distribution tests, truncate-size validation, psample group deletion under traffic, action dump, and disabled psample behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_sample.h -->

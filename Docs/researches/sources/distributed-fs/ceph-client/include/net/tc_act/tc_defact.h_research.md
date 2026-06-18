<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_defact.h -->
# sources/distributed-fs/ceph-client/include/net/tc_act/tc_defact.h

Purpose: Defines the generic/default TC action container used by simple actions carrying opaque action data.

Important APIs/types/functions: `struct tcf_defact` embeds `tc_action`, stores data length in `tcfd_datalen`, and stores opaque data in `tcfd_defdata`. `to_defact()` casts the generic action.

Control flow: Setup allocates opaque data from netlink configuration, action execution interprets it in the implementation, and deletion frees it with the action.

State and persistence behavior: State is per-action heap data, not RCU-param based in this header.

Dependencies/integration points: Depends on `act_api.h`; used by simple/default action implementations.

Risks: Opaque data length and ownership validation are central; mismatched length can cause parser overread or leak.

Test signals: Netlink create/replace/delete with varying data sizes, invalid length rejection, and action dump symmetry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_defact.h -->

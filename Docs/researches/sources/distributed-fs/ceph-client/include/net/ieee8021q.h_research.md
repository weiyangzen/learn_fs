# sources/distributed-fs/ceph-client/include/net/ieee8021q.h

Purpose: maps IETF DSCP and IEEE 802.1Q traffic types/classes. It provides a common enum and conversion hooks for QoS classification.

Important APIs/types: `enum ieee8021q_traffic_type` names traffic types such as best effort, background, excellent effort, critical applications, video, voice, internetwork control, and network control. `SIMPLE_IETF_DSCP_TO_IEEE8021Q_TT()` maps DSCP by the upper traffic-class bits. When `CONFIG_INET` is enabled, `ietf_dscp_to_ieee8021q_tt()` and `ieee8021q_tt_to_tc()` are extern functions; otherwise inline stubs provide simple mapping and `-EINVAL`.

Control flow and state: callers convert DSCP to an 802.1Q traffic type, then map the traffic type to a traffic class based on number of queues. No persistent state is declared.

Dependencies and integration: depends on errno and DSCP conventions. It integrates with qdisc, VLAN/priority mapping, DCB-like traffic classes, and drivers exposing multiple queues.

Risks: config-disabled behavior differs from full mapping, especially traffic-class conversion. Tests should cover DSCP boundary values, invalid queue counts, `CONFIG_INET` and non-INET builds, and expected queue selection for QoS-sensitive traffic.

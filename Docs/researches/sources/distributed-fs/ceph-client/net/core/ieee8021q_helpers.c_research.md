# sources/distributed-fs/ceph-client/net/core/ieee8021q_helpers.c

Purpose: Implements helper mappings between IEEE 802.1Q traffic types, NIC traffic classes, and IETF DSCP values. It codifies table-based queue mappings and DSCP-to-traffic-type policy used by networking components that configure priority handling.

Important APIs, types, and functions: `ieee8021q_tt_to_tc()` maps `enum ieee8021q_traffic_type` to a traffic class for one through eight queues using static tables based on IEEE 802.1Q-2022 Annex I examples. `ietf_dscp_to_ieee8021q_tt()` maps DSCP values to IEEE traffic types, with explicit handling for CS/AF/EF/VOICE_ADMIT values and fallback to `SIMPLE_IETF_DSCP_TO_IEEE8021Q_TT()`. Compile-time `TT_MAP_SIZE_OK()` assertions ensure each table covers all traffic types.

Control flow: Traffic-type-to-class validates the traffic type range, switches on `num_queues`, asserts the selected table size, and returns a mapped class or `-EINVAL` for unsupported queue counts. DSCP mapping switches over known DSCP values, grouping service classes into background, best effort, excellent effort, critical applications, video, voice, internetwork control, and network control, then falls back for values without explicit policy.

State and persistence: All mappings are static read-only arrays. No mutable state or persistence exists.

Dependencies and integration points: Depends on `net/dscp.h` and `net/ieee8021q.h`. It is likely consumed by drivers or qdisc/priority configuration paths that translate packet QoS markings into hardware queue or traffic class choices.

Risks: Policy choices affect QoS behavior and interoperability. Invalid queue counts return errors; callers must handle them rather than silently using class 0. DSCP fallback behavior must remain consistent with macro semantics. Table changes can reorder traffic priority for existing deployments.

Test signals: Unit-test all traffic types across 1-8 queues, invalid traffic type values, invalid queue counts, every explicitly mapped DSCP, and fallback DSCP values. Compile-time assertions should fail if `IEEE8021Q_TT_MAX` grows without table updates.

# sources/distributed-fs/ceph-client/include/net/rps.h

Purpose: declares Receive Packet Steering/Flow Steering data structures and inline hot-path helpers for recording socket flow CPU hints and queue head/tail counters.

Important APIs and types: enabled builds define static keys `rps_needed`/`rfs_needed`, `struct rps_map`, `struct rps_dev_flow`, and `struct rps_sock_flow_table`. Helpers record flow hash to the current CPU, record/delete flows from sockets, test if RFS is needed, and update `softnet_data` input queue head/tail. Disabled builds compile helpers to no-ops or zero.

Control flow: receive-side socket paths save rxhash; recvmsg or packet processing records the CPU handling a flow; RPS lookup later uses the table to steer packets to that CPU. Device flow entries track selected CPU/filter/tail information.

State and persistence: RPS maps, socket flow table entries, device flow entries, static keys, socket `sk_rxhash`, and softnet queue counters are runtime-only.

Dependencies and integration points: depends on socket core, TCP established state, RCU, static keys, net hotdata, RPS tagged pointer helpers, and softnet data.

Risks and test signals: risks include racing table updates, stale CPU hints after socket close, raw CPU use under preemption, hash zero special-casing, and disabled-config behavior. Test RPS/RFS sysctls, socket flow record/delete, CPU hotplug, table resize, accelerated RFS filters, and CONFIG_RPS disabled builds.

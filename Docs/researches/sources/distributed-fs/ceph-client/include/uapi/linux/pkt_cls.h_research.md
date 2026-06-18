<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pkt_cls.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/pkt_cls.h

Purpose: defines the traffic-control classifier and action netlink ABI used by `tc` and kernel networking to configure packet classification, policing, action chains, BPF/flower/u32 filters, extended matches, and hardware offload metadata.

Important APIs and types: generic action attributes are `TCA_ACT_*`, action return codes are `TC_ACT_*`, and extended opcodes use `TC_ACT_JUMP`/`TC_ACT_GOTO_CHAIN` with `TC_ACT_EXT_*` helpers. `enum tca_id`, `struct tc_police`, `struct tcf_t`, and `tc_gen` provide common action/police layout. Classifier sections expose `TCA_U32_*` plus `struct tc_u32_sel/key/mark/pcnt`, route4, fw, flow, basic, cgroup, BPF (`TCA_BPF_*`, `TCA_BPF_FLAG_ACT_DIRECT`), flower (`TCA_FLOWER_*` plus nested tunnel, MPLS, conntrack, CFM, and encapsulation option attributes), matchall, and ematch (`struct tcf_ematch_*`, `TCF_EM_*`).

Control flow: userspace builds rtnetlink messages with classifier-specific nested attributes. The kernel validates attributes, creates or updates filter/action objects, optionally offloads them, and later dumps stats and offload state through the same attribute IDs. Action chains return `TC_ACT_*` values that direct packet traversal, reclassification, redirect, trap, drop, or chain jumps.

State and persistence: persistent state is kernel qdisc/filter/action state bound to netdevices, chains, blocks, and net namespaces. This header defines serialized netlink attribute IDs and fixed structs; runtime counters, offload state, cookies, and timestamps live in classifier/action objects.

Dependencies and integration points: includes `linux/pkt_sched.h` for rate specs and uses fixed Linux integer and endian types. Integrates with rtnetlink, `tc`, cls_u32, cls_flower, cls_bpf, actions, ematch modules, BPF program fds/ids/tags, tunnel metadata, conntrack, MPLS, PPPoE/L2TP, CFM, and switchdev/devlink offload drivers.

Risks and test signals: high-risk areas are ABI numbering stability, nested attribute parsing, endian/mask handling, flexible-array sizing, offload flags (`SKIP_HW`, `SKIP_SW`, `IN_HW`), and range/tunnel/conntrack matches diverging between software and hardware. Test via `tc` filter add/replace/delete/dump for u32, flower, BPF, matchall, chained actions, police rate64 fields, hardware offload skip flags, malformed nested attrs, and netns cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/pkt_cls.h -->

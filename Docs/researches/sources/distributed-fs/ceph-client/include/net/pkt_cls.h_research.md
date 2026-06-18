# sources/distributed-fs/ceph-client/include/net/pkt_cls.h

Purpose: declares traffic-control classifier front-end APIs, filter extension/action plumbing, ematch trees, qevents, classifier offload descriptors, and helper predicates for software/hardware TC.

Important APIs and types: `struct tcf_walker`, `tcf_block_ext_info`, `tcf_qevent`, `tcf_exts`, ematch structs/ops, `tcf_pkt_info`, u32/matchall/BPF offload structs, cookie state, and many qdisc/classifier offload command structs are defined. APIs register classifier/ematch ops, get/put blocks/chains/protos, classify skbs, bind/unbind classes, validate/dump/destroy extensions, execute actions, set up offload callbacks/actions, and manage qevents. Inline helpers validate flags, skip hw/sw, chain 0 offload, indev matching, skb extension allocation, and hardware stats updates.

Control flow: classifier modules validate netlink config into filters/extensions, classification walks blocks/chains/protos, actions execute or offload, qevents trigger blocks, and drivers receive offload command structs through setup callbacks.

State and persistence: runtime TC state lives in blocks, chains, protos, actions, ematch data, cookies, stats, and hardware offload counters; netlink can recreate it but this header stores none.

Dependencies and integration points: integrates qdisc core, act API, flow offload, net namespaces, netdevices, BPF, ematch modules, skb extensions, and netlink extack.

Risks and test signals: risks include class binding on shared blocks, action netns lifetime, skip_hw/skip_sw invalid combos, offload stat double counting, ematch relation logic, and qevent block changes. Test classifier add/delete/replace, shared blocks, action execution, hardware offload flags/stats, ematch AND/OR/invert, BPF/u32/matchall offloads, qevents, and CONFIG_NET_CLS/ACT/EMATCH matrices.

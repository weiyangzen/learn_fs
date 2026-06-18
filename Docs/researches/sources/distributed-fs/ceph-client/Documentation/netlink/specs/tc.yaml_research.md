# sources/distributed-fs/ceph-client/Documentation/netlink/specs/tc.yaml

Purpose: this large raw rtnetlink schema documents traffic-control qdisc, class, filter, chain, action, option, and statistics ABI data over `linux/pkt_cls.h`.

Important APIs, types, and functions: the fixed header `tcmsg` carries family, ifindex, handle, parent, and info. Definitions model qdisc/classifier structs and xstats for CBS, ETF, FIFO, HTB, GRED, HFSC, MQPRIO, MULTIQ, NETEM, PLUG, PRIO, RED, SFB, SFQ, TBF, generic stats, u32 selectors, action timestamps, police, pedit, MPLS, VLAN, and many queue-specific stats. Attribute set `attrs` covers common TCA attributes such as kind, options, stats, xstats, rate, fcnt, stats2, stab, chain, block ids, dump flags, and invisible dump control. Numerous `*-attrs` sets represent action (`act-bpf`, `act-ct`, `act-mirred`, `act-vlan`, etc.), classifier (`flower`, `bpf`, `u32`, `matchall`, `basic`, etc.), and qdisc (`cake`, `fq`, `fq-codel`, `taprio`, `netem`, `red`, `tbf`, etc.) options. Sub-message formats dispatch option parsing based on `kind`, and app stats dispatch by qdisc kind.

Control flow: operations use directional rtnetlink values. `newqdisc` 36 creates qdiscs; `delqdisc` 37 deletes; `getqdisc` 38 retrieves/dumps and replies as 36. Class operations use 40/41/42, filter operations use 44/45/46, and chain operations use 100/101/102. Create-style requests use `kind`, `options`, rate, chain, and block attributes; replies return common stats and option fields. `gettfilter` dump supports chain and dump flags. Multicast group `rtnlgrp-tc` carries traffic-control notifications.

State and persistence: qdiscs, classes, filters, chains, blocks, and actions live in kernel networking state attached to devices or shared blocks. Counters and xstats are mutable runtime state and can be offloaded to hardware depending on flags and driver support.

Dependencies and integration: depends on rtnetlink, `linux/pkt_cls.h`, `linux/rtnetlink.h`, kernel qdisc/classifier/action modules, hardware offload paths, and user tools such as `tc`.

Risks: the schema spans many independent kernel modules and can drift quickly. `options-msg`, `act-options-msg`, and stats sub-message dispatch must align exactly with string `kind` names. Many fixed headers are binary UAPI structs with padding and signedness constraints. Test signals include schema generation, qdisc/filter/class round trips in a netns, representative kind coverage for simple and nested options, dump parsing, action nesting, hardware-skip flag behavior, and UAPI enum/value comparison.

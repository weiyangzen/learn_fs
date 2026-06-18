<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/pkt_cls.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/pkt_cls.h

Purpose: this UAPI header defines Linux traffic-control classifier and action ABI constants used over rtnetlink. It names action result codes, action attributes, classifier-specific netlink attributes, filter flags, and several variable-length structures used by `tc`.

Important APIs/types: generic action definitions include `TCA_ACT_*`, `TC_ACT_*`, extended action opcodes (`TC_ACT_JUMP`, `TC_ACT_GOTO_CHAIN`), `struct tc_police`, `struct tcf_t`, `struct tc_cnt`, and the `tc_gen` macro reused by action headers. Classifier sections cover u32 (`struct tc_u32_key`, `tc_u32_sel`, `tc_u32_mark`, `tc_u32_pcnt`), route4, fw, flow, basic, cgroup, BPF (`TCA_BPF_*`), flower (`TCA_FLOWER_*` and Geneve encapsulation option attributes), matchall, and ematch (`struct tcf_ematch_tree_hdr`, `struct tcf_ematch_hdr`).

Control flow: userspace builds netlink `RTM_NEWTFILTER`/`DELTFFILTER` messages with nested `TCA_*` attributes. Kernel classifier/action modules parse those attributes, install match/action state, and later return stats and flags in dumps.

State and persistence: filter and action state lives in kernel qdisc/classifier instances. Indexes, cookies, refcounts, bind counts, offload flags, timers, and per-filter counters are exposed but not owned by this header.

Dependencies/integration: depends on `linux/types.h` and `linux/pkt_sched.h`; integrated by `iproute2 tc`, hardware offload drivers, BPF tc programs, and rtnetlink `tcmsg` APIs from `rtnetlink.h`.

Risks and test signals: risks include netlink attribute number stability, flexible-array sizing, byte-order fields in u32/flower selectors, hardware offload flag interpretation, and unsupported classifier modules. Test with `tc filter` add/dump/delete for u32, flower, BPF, and actions; verify skip_hw/skip_sw/in_hw/not_in_hw flags and stats round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/pkt_cls.h -->

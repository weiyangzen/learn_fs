<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/tc_act/tc_bpf.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/tc_act/tc_bpf.h

Purpose: this header defines the traffic-control BPF action ABI.

Important APIs/types: `struct tc_act_bpf` expands `tc_gen` from `pkt_cls.h`, providing action index, capability, action result, refcount, and bind count. The `TCA_ACT_BPF_*` enum names nested attributes for timing metadata, parameters, classic BPF op length/ops, eBPF fd, name, padding, program tag, and program ID.

Control flow: userspace installs or dumps a tc action of kind `bpf` through rtnetlink action messages. The kernel parses BPF program attributes, attaches the action to classifier chains, and later reports metadata/stats.

State and persistence: action state and referenced BPF programs persist in kernel tc action tables while referenced. This file only fixes the serialization contract.

Dependencies/integration: includes `linux/pkt_cls.h`; used with `tc action add bpf`, clsact/flower/u32 classifiers, and BPF loaders that pass fds and names.

Risks and test signals: risks include fd lifetime, program type compatibility, tag/ID dump mismatches, and action result semantics. Tests should attach by fd, dump name/tag/id, execute action on traffic, and delete/unbind while checking refcounts and stats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/tc_act/tc_bpf.h -->

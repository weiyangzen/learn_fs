
# sources/distributed-fs/ceph-client/net/netfilter/nf_nat_bpf.c

Purpose: Exposes an unstable BPF kfunc allowing XDP and TC-BPF conntrack allocation paths to attach initial NAT source or destination mapping information before conntrack insertion.

Important APIs and functions: `bpf_ct_set_nat_info()` validates IPv4/IPv6 conntrack objects, builds an `nf_nat_range2` from address and optional positive port, and calls `nf_nat_setup_info()`. `register_nf_nat_bpf()` registers the BTF kfunc ID set for `BPF_PROG_TYPE_XDP` and `BPF_PROG_TYPE_SCHED_CLS`.

Control flow: A BPF program obtains a referenced `nf_conn___init`, calls the kfunc with address/port/manip type, and the kernel initializes NAT state on the unconfirmed conntrack. Registration occurs from NAT core init.

State and persistence: No local runtime state beyond static BTF kfunc descriptors. NAT state is stored in the conntrack extension/status.

Dependencies and integration: Depends on conntrack BPF allocation types, BTF kfunc registration, NAT core, and the fact that the object is not yet confirmed.

Risks: The interface is explicitly unstable, but kernel safety still depends on BTF type restrictions, unconfirmed conntrack state, family validation, and port byte-order handling. Test signals include verifier-accepted XDP/SCHED_CLS programs setting source and destination NAT, invalid family rejection, random-port behavior for non-positive ports, and failure when NAT setup returns drop.

# sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_bpf.h

## Purpose
Defines the traffic-control action ABI for attaching BPF programs as packet actions.

## Important APIs, Types, and Constants
`struct tc_act_bpf` embeds `tc_gen`. Netlink attributes include timing, parameters, classic BPF op length/ops, BPF fd, name, pad, tag, and id through `TCA_ACT_BPF_*`.

## Control Flow, State, and Persistence
Userspace sends netlink action attributes to create/update a TC action. Kernel stores generic action state and references a BPF program by fd/id/name/tag.

## Dependencies and Integration Points
Depends on `<linux/pkt_cls.h>`. Integrates with `tc`, rtnetlink, classifier/action core, and eBPF program management.

## Risks and Test Signals
Risks include fd lifetime/reference mistakes, classic-vs-eBPF attribute confusion, and missing tag/id validation. Test `tc action bpf` add/show/delete, fd-based load, dump attributes, and program execution counters.

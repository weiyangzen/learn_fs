<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_flow_table_bpf.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_flow_table_bpf.c

## Purpose
Exposes an unstable BPF kfunc for XDP programs to look up netfilter flow table entries by a `bpf_fib_lookup` tuple and refresh matching flow offloads.

## Important APIs, Types, and Functions
The BPF-visible kfunc is `bpf_xdp_flow_lookup()`. Internal helper `bpf_xdp_flow_tuple_lookup()` finds a flow table for a device, does `flow_offload_lookup()`, derives the owning `struct flow_offload`, and refreshes it. `nf_flow_register_bpf()` registers the BTF kfunc set for `BPF_PROG_TYPE_XDP`. `struct bpf_flowtable_opts` currently contains only `error`.

## Control Flow
The kfunc validates `opts_len`, builds a `struct flow_offload_tuple` from `bpf_fib_lookup`, copies IPv4 or IPv6 addresses depending on family, and rejects unsupported families. Lookup uses the XDP RX device to find an attached nf flowtable. Errors are returned as NULL with `opts->error`; successful lookups return a `flow_offload_tuple_rhash *` and refresh the flow.

## State and Persistence
This file owns no flow state. It reads flow tables attached to devices and refreshes existing `struct flow_offload` timeout/accounting state through flow table core. The BTF kfunc registration persists after `nf_flow_register_bpf()` succeeds.

## Dependencies and Integration Points
Depends on BPF kfunc/BTF registration, XDP context casting, `bpf_fib_lookup` layout, netfilter flow table core, and `nf_flow_table_core.c`, which calls `nf_flow_register_bpf()`.

## Risks
The interface is explicitly unstable, but verifier-visible struct sizes and return annotations still must match the kernel BTF contract. `opts` is assumed valid when `opts_len` is checked. Flow tuple construction must match flowtable lookup keys exactly, including interface index, family, L4 protocol, ports, and addresses.

## Test Signals
Load XDP programs using the kfunc, test IPv4 and IPv6 flowtable hits/misses, unsupported family, wrong options length, no flowtable on device, timeout refresh on hit, BTF registration failure handling, and verifier behavior around nullable return values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_flow_table_bpf.c -->

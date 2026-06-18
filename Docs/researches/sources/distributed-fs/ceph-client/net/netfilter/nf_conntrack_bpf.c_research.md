# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_bpf.c

## Purpose
`nf_conntrack_bpf.c` exposes unstable conntrack kfuncs to XDP and TC-BPF programs. BPF programs can allocate, look up, insert, release, and modify conntrack entries using typed BTF references and verifier-enforced lifetime rules.

## Important APIs, Types, And Functions
`struct bpf_ct_opts` carries namespace selection, error output, L4 protocol, direction, zone id/direction, and reserved bytes. Tuple conversion is handled by `bpf_nf_ct_tuple_parse()`. Common lookup/allocation lives in `__bpf_nf_ct_lookup()` and `__bpf_nf_ct_alloc_entry()`. Public kfuncs include XDP/SKB alloc and lookup, `bpf_ct_insert_entry()`, `bpf_ct_release()`, timeout setters/changers, and status setters/changers.

Verifier integration uses BTF IDs for `struct nf_conn` and `struct nf_conn___init`, kfunc acquire/release flags, and `_nf_conntrack_btf_struct_access()` to limit writes to supported fields such as `mark` when configured. `register_nf_conntrack_bpf()` registers the set for XDP and SCHED_CLS and installs the BTF access callback.

## Control Flow
Lookup validates options and tuple length, resolves an optional target net namespace by nsid, initializes a conntrack zone, calls `nf_conntrack_find_get()`, stores lookup direction in `opts->dir`, and returns a referenced `nf_conn`. Allocation builds original and reply tuples, resolves namespace/zone, calls `nf_conntrack_alloc()`, clears protocol-private data, and sets an initial timeout. Insert marks the entry confirmed, calls `nf_conntrack_hash_check_insert()`, frees on failure, and returns a normal `nf_conn` reference. Release drops the reference with `nf_ct_put()`.

## State And Persistence
State changes are real conntrack table changes: allocated entries consume per-net conntrack count, inserted entries enter the global hash table, timeout/status mutations affect normal GC and protocol behavior. BPF references are verifier-managed and must be released or transferred.

## Dependencies And Integration Points
This file integrates BPF verifier/kfunc/BTF infrastructure with conntrack core allocation, hash insertion, timeout/status mutation, zones, net namespace nsid lookup, XDP receive-device netns, and TC skb device/socket netns.

## Risks
Option-size compatibility must remain strict because older callers use 12-byte options without zone fields. Namespace references must always be put. Insert failure must free the unconfirmed entry exactly once. Verifier write permissions must not expose mutable internals beyond supported fields. BPF can influence packet state substantially through timeout and status changes.

## Test Signals
Run BPF selftests for XDP/TC lookup, allocation, insert, release, invalid option sizes, reserved bytes, unsupported protocols, IPv4/IPv6 tuple sizes, netns id lookup failure, zone behavior, timeout/status mutation, verifier leak detection, write rejection, and insert clash/table-full paths.

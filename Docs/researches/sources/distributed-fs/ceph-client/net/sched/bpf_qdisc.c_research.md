# sources/distributed-fs/ceph-client/net/sched/bpf_qdisc.c

## Purpose

`bpf_qdisc.c` exposes `struct Qdisc_ops` as a BPF struct-ops target. It lets BPF programs implement qdisc enqueue, dequeue, init, reset, and destroy callbacks with verifier restrictions, helper kfuncs, prologue/epilogue code, and registration through the normal qdisc registry.

## Important APIs, types, and functions

`bpf_Qdisc_ops` is the `struct bpf_struct_ops` descriptor. `bpf_qdisc_verifier_ops` supplies access checks, BTF struct write rules, and generated prologue/epilogue. `bpf_qdisc_is_valid_access()` gives enqueue programs trusted access to a `bpf_sk_buff_ptr` for `to_free`. `bpf_qdisc_btf_struct_access()` limits writable fields in `Qdisc` and `sk_buff`. Kfuncs include `bpf_skb_get_hash()`, `bpf_kfree_skb()`, `bpf_qdisc_skb_drop()`, `bpf_qdisc_watchdog_schedule()`, `bpf_qdisc_bstats_update()`, plus hidden init/reset/destroy hooks. `bpf_qdisc_init_member()` forces `priv_size`, default `peek`, and validates `id`. `bpf_qdisc_reg()` and `bpf_qdisc_unreg()` call `register_qdisc()` and `unregister_qdisc()`.

## Control flow

Late init registers qdisc kfunc IDs, skb destructor kfuncs, and the BPF struct-ops type. Loading a BPF qdisc validates required callbacks, initializes selected members, and registers a qdisc ops instance. The generated init prologue initializes a `qdisc_watchdog` in BPF private data and rejects unsupported parents except root or mq. Reset/destroy epilogues cancel the watchdog. Kfunc filtering restricts enqueue-only helpers, dequeue-only helpers, and common helpers according to the attached `Qdisc_ops` member.

## State and persistence

The kernel-side private data for each BPF qdisc is `struct bpf_sched_data`, currently a `qdisc_watchdog`. The BPF link pins the registered `Qdisc_ops` lifetime; unregister removes it from the qdisc registry. BPF program-owned queue state lives in BPF maps or qdisc private memory exposed through struct ops, while skb drops may be deferred through the qdisc to-free list.

## Dependencies and integration points

It depends on BPF verifier, BTF IDs, struct_ops, qdisc core, qdisc watchdogs, skb dynptr support, kfunc registration, and qdisc registration APIs. It is an integration point between tc/qdisc scheduling and BPF program lifecycle.

## Risks and edge cases

Verifier access boundaries are critical: only selected `Qdisc` and `sk_buff` fields are writable. Kfunc filtering must prevent enqueue/dequeue helpers in the wrong callback. Prologue/epilogue generation must preserve context registers and guarantee watchdog init/cancel even for BPF implementations. Parent qdisc validation prevents unsupported non-root use, with a special case for mq defaults not yet in the qdisc hash.

## Test signals

Build and load BPF struct-ops qdiscs with all required callbacks, missing callbacks, invalid `priv_size`, invalid ids, root and mq parents, and unsupported parents. Exercise enqueue drop/free helpers, dequeue stats updates, watchdog scheduling/canceling, verifier rejection for disallowed field writes and wrong-context kfuncs, and qdisc unregister through BPF link teardown.

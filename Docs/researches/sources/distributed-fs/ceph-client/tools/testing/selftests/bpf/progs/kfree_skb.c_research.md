<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kfree_skb.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kfree_skb.c

Purpose: Tracepoint/fentry/fexit skb test that reads skb/net_device metadata and emits perf samples during free and eth-type paths. The file has 154 source lines and 3654 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `tp_btf/kfree_skb:BPF_PROG, fentry/eth_type_trans:BPF_PROG, fexit/eth_type_trans:BPF_PROG`. Local functions/subprograms: `BPF_PROG, BPF_PROG, BPF_PROG`. Maps: `perf_buf_map`. Types: `callback_head, dev_ifalias, net_device, sk_buff, meta`. BPF helpers/kfuncs/macros used as calls: `bpf_htons, bpf_printk, bpf_probe_read_kernel, bpf_skb_output`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `tp_btf/kfree_skb:BPF_PROG, fentry/eth_type_trans:BPF_PROG, fexit/eth_type_trans:BPF_PROG`. Control flow is centered on helper-mediated memory reads avoid direct unsafe kernel/user access.

State and persistence: Persistent state is held in BPF maps `perf_buf_map` and in globals emitted into BPF data sections.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: memory access tests are sensitive to BTF type layout and helper sleepability rules; symbol names and attachment capabilities can vary with kernel config and inlining.

Test signals: successful attachment/execution of tp_btf/kfree_skb:BPF_PROG, fentry/eth_type_trans:BPF_PROG, fexit/eth_type_trans:BPF_PROG; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kfree_skb.c -->

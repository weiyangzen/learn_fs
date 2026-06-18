<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/test_lwt_bpf.c -->
# sources/distributed-fs/ceph-client/samples/bpf/test_lwt_bpf.c

## Purpose
`test_lwt_bpf.c` provides multiple lightweight tunnel route BPF programs used by the accompanying shell integration test. It validates lwt context access, skb control-buffer clearing, packet data reads, checksum-safe IP rewriting, L2 header push and redirect, intentional corruption, and drops.

## Important APIs, Types, And Functions
Program sections include `nop`, `test_ctx`, `test_cb`, `test_data`, `test_rewrite`, `push_ll_and_redirect_silent`, `push_ll_and_redirect`, `fill_garbage`, `fill_garbage_and_redirect`, and `drop_all`. Helpers include `rewrite()`, `__do_push_ll_and_redirect()`, and `__fill_garbage()`. It uses `bpf_skb_load_bytes()`, `bpf_skb_store_bytes()`, `bpf_l3_csum_replace()`, `bpf_l4_csum_replace()`, `bpf_skb_change_head()`, `bpf_redirect()`, and `bpf_trace_printk()`.

## Control Flow
Each route-attached section returns `BPF_OK`, `BPF_DROP`, or a redirect result. Context tests print skb fields and write `skb->cb[0]`. Data tests parse IPv4 headers. Rewrite tests replace a configured destination IP and update L3/L4 checksums based on protocol. Redirect tests prepend an Ethernet header using compile-time MAC/ifindex constants and redirect to the destination interface.

## State And Persistence
The BPF programs use no maps. State is per-packet skb context and trace output. MAC addresses and destination ifindex are compiled in by the test script.

## Dependencies And Integration Points
It depends on lwt BPF route encap support, kernel networking headers from `vmlinux.h` and `net_shared.h`, and test-provided `SRC_MAC`, `DST_MAC`, and `DST_IFINDEX` defines. It integrates with `ip route encap bpf` in `test_lwt_bpf.sh`.

## Risks And Edge Cases
The programs intentionally corrupt or drop packets in several sections. IPv4 checksum offsets assume no IP options. Compile-time constants must match the generated veth topology. Trace output is part of the test contract and can be affected by tracing configuration.

## Test Signals
The shell harness verifies exact trace strings for context, data, cb, rewrite, redirect, garbage, and drop cases, plus ping/netperf success or failure depending on the installed section.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/test_lwt_bpf.c -->

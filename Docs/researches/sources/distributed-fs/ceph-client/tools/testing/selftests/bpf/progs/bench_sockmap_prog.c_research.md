# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bench_sockmap_prog.c

## Purpose

Benchmark/helper BPF programs for sockmap and sk_msg redirection throughput tests. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`BPF_MAP_TYPE_SOCKMAP` maps `sock_map_rx`/`sock_map_tx`, `bpf_sk_redirect_map()`, `bpf_msg_redirect_map()`, SK_SKB parser/verdict sections, SK_MSG verdict sections, and globals `process_byte`, `verdict_dir`, `dropped`, `pkt_size`.

## Control Flow

The stream parser returns configured `pkt_size`. Verdict programs redirect to map index 1 using `verdict_dir`, count bytes processed, and increment `dropped` on `SK_DROP`. Pass variants only count bytes and return `SK_PASS`.

## State and Persistence Behavior

Sockmap contents are managed by userspace benchmark code. Global counters and configuration variables persist in BSS while the benchmark runs.

## Dependencies and Integration Points

It depends on BPF CO-RE/libbpf helper headers, section annotations, generated skeleton loading from the selftest harness, and kernel verifier support for the program type, map type, helpers, kfuncs, and BTF metadata declared here. It depends on sockmap/sk_skb/sk_msg program support and userspace populating maps/configuration.

## Risks and Edge Cases

Incorrect `verdict_dir` or missing map entries cause drops and skew benchmark results. Parser `pkt_size` controls stream framing and must match benchmark payloads.

## Test Signals

Benchmark harness observes byte counters, drop counter, and redirect/pass behavior under selected parser/verdict modes.

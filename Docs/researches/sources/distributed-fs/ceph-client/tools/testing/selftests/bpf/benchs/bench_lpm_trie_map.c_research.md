# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_lpm_trie_map.c

Purpose: provides LPM trie map benchmarks for no-op, baseline, lookup, insert, update, delete, and free behavior over dense key ranges, including random-access mode for supported operations.

Important APIs and functions: argp options parse `--nr_entries`, `--prefix_len`, and `--random`. `validate_common()` checks consumers, required entries, and prefix capacity; operation-specific validators reject unsupported producer counts or random mode. `attach_prog()` loads `lpm_trie_bench`, configures BSS, allocates key/value arrays, and attaches the skeleton. `fill_map()` and `empty_map()` use batch map APIs. Producers use `bpf_prog_test_run_opts()` or repeatedly load/fill/destroy `lpm_trie_map` to measure free cost.

Control flow: setup selects a BPF operation code in BSS and initializes map state as empty or full. The regular producer repeatedly test-runs `run_bench`, handles BPF return codes, and reinitializes maps for insert/delete when requested. Free benchmark creates a fresh skeleton, fills the map, then destroys it in a loop.

State and persistence: keys and values are heap arrays for the benchmark lifetime. BPF BSS counters track hits and active measured duration; map contents are reset between partial measurement windows for mutating operations.

Dependencies and integration points: depends on generated `lpm_trie_bench` and `lpm_trie_map` skeletons, `progs/lpm_trie.h` operation/return-code constants, libbpf batch APIs, and the common bench reporting helpers.

Risks: `(1UL << args.prefixlen)` can be undefined for oversized prefix lengths on some word sizes; batch update/delete failures abort; mutating operations need careful duration accounting because reset time is excluded; dense key layout measures worst-case behavior, not arbitrary sparse production use.

Test signals: operation summaries report throughput and latency. BPF errors, unexpected return codes, or failed batch updates/deletes are immediate failures.

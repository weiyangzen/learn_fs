# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_lru_map.c

## Research

This standalone C selftest validates kernel LRU hash and LRU per-CPU hash map eviction semantics. It compares LRU maps against expected ordinary hash maps after controlled lookup, update, delete, CPU-affinity, and datapath-reference-bit sequences.

Key helpers include `create_map()`, `bpf_map_lookup_elem_with_ref_bit()`, `map_subset()`, `map_equal()`, `sched_next_online()`, `__tgt_size()`, and `__map_size()`. The special lookup helper loads a tiny SCHED_CLS BPF program that performs `bpf_map_lookup_elem()` from datapath context, which marks the LRU reference bit differently from syscall lookup. The numbered `test_lru_sanity0()` through `test_lru_sanity8()` scenarios cover two-entry eviction, referenced versus unreferenced recycling, active/inactive list rotation, deletion, one-element maps across CPUs, per-CPU `BPF_F_NO_COMMON_LRU` behavior, and syscall versus datapath reference-bit differences.

`main()` sets libbpf strict mode, discovers possible CPUs, then runs all sanity tests for `BPF_MAP_TYPE_LRU_HASH` and `BPF_MAP_TYPE_LRU_PERCPU_HASH` with both common LRU and `BPF_F_NO_COMMON_LRU`. State is transient kernel map/program FDs, CPU affinity changes for child/current processes, and expected-map contents. Cleanup closes FDs after each case.

Dependencies include libbpf, BPF syscall support, SCHED_CLS program load/test-run support, CPU affinity, and possible CPU discovery. Risks are timing/CPU topology sensitivity, changing LRU internals, and reliance on negative libbpf return conventions in assertions. Test signals are printed `Pass` per scenario, assertion failures on unexpected errno or map contents, and final process exit status.

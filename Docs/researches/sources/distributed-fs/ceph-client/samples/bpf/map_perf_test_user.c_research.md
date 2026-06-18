# sources/distributed-fs/ceph-client/samples/bpf/map_perf_test_user.c

Purpose: userspace benchmark driver for BPF map performance tests.

Important APIs/types/functions: time helper `time_get_ns`, enums `test_type` and `map_idx`, globals `map_fd`, `test_flags`, map sizing parameters, `check_test_flags`, `test_hash_prealloc`, `pre_test_lru_hash_lookup`, `do_test_lru`, map-in-map setup, option parsing, and benchmark loops.

Control flow: parses CLI options controlling test selection, entry counts, task count, and iterations; loads the BPF object; collects map FDs; optionally creates inner maps; forks or loops workloads; triggers attached BPF programs through syscalls; times operations; and prints per-test results.

State and persistence: uses BPF maps for benchmark state and process-local timing data. Child processes may be spawned for parallel stress. State ends when the object closes.

Dependencies and integration: pairs with `map_perf_test.bpf.c`; uses libbpf, BPF syscalls, process scheduling/fork APIs, and architecture syscall numbers.

Risks: timing is noisy and not a stable correctness metric. Large map sizes or task counts can consume significant memory/CPU. Some tests depend on CPU count up to `MAX_NR_CPUS` and map-in-map support.

Test signals: selected benchmark modes complete, timings are printed, no verifier/load failures, and repeated runs show roughly plausible relative performance.

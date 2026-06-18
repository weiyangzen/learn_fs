# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_maps.c

## Research

`test_maps.c` is a broad standalone ABI regression suite for BPF map operations. It uses assert-style checks and selected libbpf helpers to exercise hash, per-CPU hash, array, per-CPU array, devmap, queue, stack, sockmap, map-in-map, large maps, parallel update/delete, read-only/write-only maps, reuseport sockarray, and additional map tests included from `map_tests/tests.h`.

Important APIs are `bpf_map_create()`, `bpf_map_update_elem()`, `bpf_map_lookup_elem()`, `bpf_map_lookup_and_delete_elem()`, `bpf_map_delete_elem()`, `bpf_map_get_next_key()`, map ID/info iteration, `bpf_prog_test_load()`, `bpf_prog_attach()`/`detach2()`, libbpf object/map lookup, and socket syscalls. `map_update_retriable()` and `map_delete_retriable()` add retry/backoff for concurrent or no-prealloc races. `__run_parallel()` forks many children to stress shared map FDs.

Control flow is `main()` setting strict libbpf mode, running `run_all_tests()` once with default map flags and again with `BPF_F_NO_PREALLOC`, then invoking generated extra map tests. `run_all_tests()` sequences basic semantics, stress, sockmap, map-in-map, permission flags, reuseport, queue, and stack cases. The sockmap test creates TCP sockets, loads SK_SKB/SK_MSG programs, attaches parser/verdict programs, validates invalid attach/detach paths, sends data, and forks concurrent map mutators.

State includes many transient kernel map/program/object FDs, sockets, forked child processes, global `map_opts`, and skip count `skips`. Dependencies include root/BPF privileges, networking on loopback, object files such as `sockmap_parse_prog.bpf.o`, and support for each map type. Risks are environmental flakiness from port conflicts, resource pressure, high fork counts, unsupported map types, and assert aborts that skip cleanup. Test signals are assertion success, explicit skip count, printed failure context, and final `test_maps: OK`.

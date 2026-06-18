<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/map_kptr_race.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/map_kptr_race.c

Purpose: Race/leak regression tests for map kptr deletion and map-free paths across hash, percpu hash, and sk storage maps. The file has 198 source lines and 4036 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `tc:test_htab_leak, tc:test_percpu_htab_leak, tp_btf/inet_sock_set_state:BPF_PROG, fentry/bpf_map_put:BPF_PROG, fexit/htab_map_free:BPF_PROG, fexit/bpf_sk_storage_map_free:BPF_PROG, syscall:count_ref`. Local functions/subprograms: `test_htab_leak, fill_percpu_kptr, test_percpu_htab_leak, BPF_PROG, BPF_PROG, BPF_PROG, BPF_PROG, count_ref`. Maps: `race_hash_map, race_percpu_hash_map, race_sk_ls_map`. Types: `map_value`. BPF helpers/kfuncs/macros used as calls: `bpf_kfunc_call_test_acquire, bpf_kfunc_call_test_release, bpf_kptr_xchg, bpf_map_delete_elem, bpf_map_lookup_elem, bpf_map_lookup_percpu_elem, bpf_map_update_elem, bpf_sk_storage_delete, bpf_sk_storage_get`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `tc:test_htab_leak, tc:test_percpu_htab_leak, tp_btf/inet_sock_set_state:BPF_PROG, fentry/bpf_map_put:BPF_PROG, fexit/htab_map_free:BPF_PROG, fexit/bpf_sk_storage_map_free:BPF_PROG, syscall:count_ref`. Control flow is centered on map lookups/updates select per-test storage and branch on NULL results; test kfunc calls validate argument typing, reference ownership, and module resolution.

State and persistence: Persistent state is held in BPF maps `race_hash_map, race_percpu_hash_map, race_sk_ls_map` and in globals emitted into BPF data sections. It also manipulates verifier-tracked kernel object references or kptr ownership, so every acquire/exchange/drop path is part of the state contract. Local-storage helper calls persist values on kernel objects such as tasks, sockets, inodes, or cgroups until explicit delete or object teardown.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: reference/kptr ownership mistakes can leak references or allow use-after-drop patterns; symbol names and attachment capabilities can vary with kernel config and inlining.

Test signals: successful attachment/execution of tc:test_htab_leak, tc:test_percpu_htab_leak, tp_btf/inet_sock_set_state:BPF_PROG, fentry/bpf_map_put:BPF_PROG, fexit/htab_map_free:BPF_PROG, fexit/bpf_sk_storage_map_free:BPF_PROG; plus 1 more; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/map_kptr_race.c -->

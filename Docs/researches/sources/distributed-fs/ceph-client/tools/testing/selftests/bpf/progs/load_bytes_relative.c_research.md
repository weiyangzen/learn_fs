<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/load_bytes_relative.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/load_bytes_relative.c

Purpose: Cgroup skb program that validates `bpf_skb_load_bytes_relative` for network-header-relative packet reads. The file has 49 source lines and 1003 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `cgroup_skb/egress:load_bytes_relative`. Local functions/subprograms: `load_bytes_relative`. Maps: `test_result`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_map_update_elem, bpf_skb_load_bytes_relative`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `cgroup_skb/egress:load_bytes_relative`. Control flow is centered on map lookups/updates select per-test storage and branch on NULL results; helper-mediated memory reads avoid direct unsafe kernel/user access.

State and persistence: Persistent state is held in BPF maps `test_result` and in globals emitted into BPF data sections.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: successful attachment/execution of cgroup_skb/egress:load_bytes_relative; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/load_bytes_relative.c -->

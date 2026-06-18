<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/jeq_infer_not_null_fail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/jeq_infer_not_null_fail.c

Purpose: Regression test that prevents equality-branch inference from treating a map lookup result as non-NULL unsafely. The file has 47 source lines and 1174 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `?raw_tp:jeq_infer_not_null_ptr_to_btfid`. Local functions/subprograms: `jeq_infer_not_null_ptr_to_btfid`. Maps: `m_hash`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_map_lookup_elem`. Verifier messages asserted here: `R8 invalid mem access 'map_value_or_null`.

Control flow: Entry points are BPF programs in `?raw_tp:jeq_infer_not_null_ptr_to_btfid`. Control flow is centered on map lookups/updates select per-test storage and branch on NULL results; annotated negative cases assert exact verifier diagnostics.

State and persistence: Persistent state is held in BPF maps `m_hash` and in globals emitted into BPF data sections.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: expected verifier strings are intentionally brittle across verifier diagnostic wording changes.

Test signals: libbpf verifier annotations __failure; expected verifier diagnostics such as `R8 invalid mem access 'map_value_or_null`; successful attachment/execution of ?raw_tp:jeq_infer_not_null_ptr_to_btfid; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/jeq_infer_not_null_fail.c -->

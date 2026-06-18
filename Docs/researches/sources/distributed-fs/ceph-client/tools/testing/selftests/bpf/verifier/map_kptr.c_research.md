# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/map_kptr.c

Purpose: validates verifier rules for kptr fields stored in map values, including allowed zero stores, disallowed stores to referenced kptrs, constant-offset requirements, untrusted pointer propagation, and `bpf_kptr_xchg` behavior.

Important APIs/types/functions: uses `BPF_FUNC_map_lookup_elem`, `BPF_FUNC_kptr_xchg`, `BPF_FUNC_this_cpu_ptr`, `BPF_FUNC_map_delete_elem`, `fixup_map_kptr`, `fixup_kfunc_btf_id`, and scheduler classifier program type.

Control flow: common tests reject nonzero immediate stores to kptrs, non-DW accesses, variable offsets, unaligned offsets, and helper indirect access. Unreferenced pointer tests check type mismatch, untrusted/null loaded pointer access, struct-size bounds, untrusted propagation through struct walking, no reference-state creation, and xchg rejection on unreferenced kptrs. Referenced pointer tests reject unsafe helper use, nonzero offsets, leaked reference after xchg, and raw ST/STX into referenced kptr fields.

State and persistence behavior: harness map values hold kptr fields, but the core state is verifier pointer trust, RCU/reference annotations, constant offset proofs, and reference lifetime tracking. The acquire kfunc case must create a reference that is detected as unreleased.

Dependencies and integration points: requires map-kptr fixture setup and BTF/kfunc fixups. Strongly tied to kernel BTF type names such as `prog_test_ref_kfunc` and `ptr_prog_test`.

Risks: kptr verifier bugs can allow storing arbitrary kernel pointers, bypassing reference tracking, or passing untrusted pointers to helpers.

Test signals: almost all cases reject with precise diagnostics such as `BPF_ST imm must be 0 when storing to kptr`, `kptr access size must be BPF_DW`, `kptr access cannot have variable offset`, `store to referenced kptr disallowed`, and `kptr cannot be accessed indirectly by helper`; one unreferenced no-reference-state case accepts.

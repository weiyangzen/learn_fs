# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_insn_array.c

Purpose: validates `BPF_MAP_TYPE_INSN_ARRAY` program-load integration: original-to-translated instruction offsets, verifier rejection cases, required freezing, single-program ownership, JIT hardening/blinding effects, and disallowed BPF-side lookup.

Important APIs/types/functions: `map_create` creates instruction-array maps; `prog_load` passes an FD array through `bpf_prog_load_opts`; `__check_success` populates `orig_off`, freezes the map, loads a program, then validates `xlated_off`. Subtests cover one-to-one mapping, helper-call expansion, NOP/dead-code deletion, function bodies, out-of-bounds/mid-instruction indices, JIT hardening via `/proc/sys/net/core/bpf_jit_harden`, unfrozen maps, no map reuse, and BPF-side lookup rejection.

Control flow: on supported architectures, `test_bpf_insn_array` runs named subtests. Success cases populate maps and compare translated offsets after verifier/JIT transformations. Negative cases intentionally set bad `orig_off`, omit freeze, reuse a map for a second program, or call `bpf_map_lookup_elem` on an instruction-array map and assert expected load errors. The blinding test temporarily sets JIT hardening to level 2 and restores the old value.

State and persistence behavior: instruction-array maps store `orig_off` before program load and kernel-filled `xlated_off` after load. A map becomes associated with one loaded program and cannot be reused. The JIT hardening sysctl is process-external state and is restored in cleanup if changed.

Dependencies and integration points: gated to x86_64, powerpc, or aarch64. Uses raw BPF instruction macros, libbpf program load options with `fd_array`, map freeze, map update/lookup, and sysctl file access.

Risks: changing `/proc/sys/net/core/bpf_jit_harden` requires permission and affects global kernel behavior briefly. Expected translated offsets are architecture/kernel-codegen sensitive, hence the architecture guard. Cleanup must restore sysctl even on failure.

Test signals: exact `xlated_off` arrays for success cases, `-EINVAL` for incorrect indices/unfrozen map/BPF-side lookup, `-EBUSY` for map reuse, successful normal array-map lookup program as a control, and skip on unsupported architectures.

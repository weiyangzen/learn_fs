# sources/distributed-fs/ceph-client/kernel/bpf/bpf_insn_array.c

Purpose: implements `BPF_MAP_TYPE_INSN_ARRAY`, a read-only-to-BPF jump-table-like map that stores original, translated, and JIT offsets for indirect instruction pointer access.

Important APIs/types/functions: `struct bpf_insn_array` stores an embedded map, single-use `used` flag, `ips` array, and flexible `values`. Map ops include allocation, lookup, update, direct value address, BTF checking, and memory usage. Runtime APIs are `bpf_insn_array_init`, `bpf_insn_array_ready`, `bpf_insn_array_release`, `bpf_insn_array_adjust`, `bpf_insn_array_adjust_after_remove`, and `bpf_prog_update_insn_ptrs`.

Control flow: map creation requires u32 keys, exact value size, no flags, and marks the map `BPF_F_RDONLY_PROG`. Userspace update may only set `orig_off`; `xlated_off` and `jitted_off` must be zero. Verifier initialization requires a frozen map, validates offsets against the program and 64-bit immediate pairs, atomically claims single-program use, and copies original offsets into translated offsets. Later instruction insert/remove adjustments rewrite translated offsets or mark deleted entries. JITs call `bpf_prog_update_insn_ptrs` with offset tables and image base to fill `jitted_off` and executable IPs.

State and persistence: map values persist for map lifetime; `used` serializes ownership by one program at a time; `ips` are populated only after JIT update and cleared only by overwrite/free.

Dependencies and integration: depends on BPF map core, program verifier freeze semantics, JIT offset reporting, direct value address support, and common array next-key helper.

Risks: stale or invalid offsets can jump into wrong instructions. The map must be frozen before program use and exclusive to one program. Offset adjustment must track verifier instruction rewrites exactly. JITs must call pointer update with correct subprogram-relative offsets.

Test signals: selftests for insn arrays should cover map creation validation, frozen-map requirement, invalid offsets into ldimm64 pairs, instruction insertion/removal adjustment, JIT pointer readiness, and single-use `-EBUSY`.

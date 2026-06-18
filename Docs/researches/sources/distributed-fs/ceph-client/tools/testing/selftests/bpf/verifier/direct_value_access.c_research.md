# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/direct_value_access.c

Purpose: validates direct map-value pointer loads via `BPF_PSEUDO_MAP_VALUE`, including bounds, signed offsets, small maps, and invalid `ld_imm64` encodings.

Important APIs/types/functions: uses `BPF_LD_MAP_VALUE`, `BPF_LD_IMM64_RAW_FULL`, map fixups `fixup_map_array_48b` and `fixup_map_array_small`, and memory load/store macros over direct map values.

Control flow: write tests 1-5 accept in-bounds doubleword stores across a 48-byte array value. Tests 6-13 reject out-of-range base or access offsets, including negative and huge offsets. Tests 14-17 check cross-byte/halfword loads and stores at the end of a 48-byte value. Tests 18-20 repeat boundary logic on a small map. Invalid instruction tests mutate reserved fields and pseudo kinds to confirm decoder rejection.

State and persistence behavior: harness-created maps provide backing state, but the test focus is verifier pointer offset metadata. Accepted runtime cases use `.retval` to prove writes and reads hit expected bytes.

Dependencies and integration points: depends on map fixup machinery for direct value pseudo-loads.

Risks: direct map-value access bypasses helper lookup, so offset validation and instruction decoding must be precise. Off-by-one bugs at value-size boundaries are the main risk.

Test signals: accepted cases return `1`, `0xff`, or `0xffff`; rejections include `R1 min value is outside of the allowed memory range`, `invalid access to map value pointer`, `invalid access to map value`, `invalid bpf_ld_imm64 insn`, `BPF_LD_IMM64 uses reserved fields`, and `unrecognized bpf_ld_imm64 insn`.

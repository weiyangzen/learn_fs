# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_gotox.c

Purpose: tests BPF indirect jump (`gotox`) and instruction-array jump-table support generated from C switch statements and manually constructed programs.

Important APIs/types/functions: skeleton `bpf_gotox.skel.h` provides programs for switch/jump-table variants. `check_simple` and `check_simple_fentry` run programs or trigger attached fentry paths and inspect `ret_user`. `check_one_map_two_jumps` inspects program map IDs for exactly one `BPF_MAP_TYPE_INSN_ARRAY`. Manual helpers `create_jt_map`, `prog_load`, `__check_ldimm64_off_prog_load`, `__check_ldimm64_gotox_prog_load`, `allow_offsets`, and `reject_offsets` verify verifier handling of instruction-array map-value offsets.

Control flow: top-level opens/loads skeleton, sets PID, and runs subtests if not skipped by BPF data. Switch tests feed input arrays and compare expected outputs. Other-section tests attach fentry-style programs and trigger with `usleep`. Offset tests create frozen instruction-array maps, load raw BPF programs with map-value references and indirect jumps, then allow or reject combinations based on alignment and bounds.

State and persistence behavior: skeleton BSS carries input/output for fentry-triggered cases. Instruction-array maps are populated with `struct bpf_insn_array_value.orig_off`, frozen, and consumed by program load; map FDs are closed after each check.

Dependencies and integration points: depends on kernel `BPF_MAP_TYPE_INSN_ARRAY`, verifier gotox support, libbpf skeletons, raw BPF instruction macros, and test harness assertions.

Risks: skips when the BPF object reports unsupported gotox. Manual tests assume verifier returns `-EACCES` for invalid offsets. Generated switch behavior is tightly coupled to paired BPF C output and compiler code generation.

Test signals: exact return mapping for switch inputs, exactly one instruction-array map for shared jump table, accepted aligned in-bounds offsets, rejected unaligned/out-of-bounds/negative-first offsets, and successful LLVM nonzero-offset behavior.

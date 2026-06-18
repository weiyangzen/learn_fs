<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_excl.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_excl.c

Purpose: verifies libbpf exclusive-map access enforcement, where a map can be restricted to one designated BPF program.

Important APIs and functions: `test_map_excl_allowed()` calls `bpf_map__set_exclusive_program()` for `excl_map` and autoloads only `should_have_access`, expecting load success. `test_map_excl_denied()` sets the same exclusive program but autoloads `should_not_have_access`, expecting `map_excl__load()` to fail with `-EACCES`.

Control flow: top-level runs allowed and denied subtests independently, opening/destroying a skeleton for each.

State and persistence: exclusive access metadata is attached to the libbpf map before load. No persistent state remains after skeleton destruction.

Dependencies and integration: depends on `map_excl.skel.h` and libbpf exclusive-program support.

Risks and test signals: `0` load for allowed and `-EACCES` for denied are the signals. Risks are changes in libbpf pre-load validation or kernel verifier error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_excl.c -->

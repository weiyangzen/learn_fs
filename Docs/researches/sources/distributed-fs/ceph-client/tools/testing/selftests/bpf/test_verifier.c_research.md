<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_verifier.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_verifier.c

## Purpose
`test_verifier.c` is the standalone eBPF verifier regression test runner. It materializes verifier test cases from `<verifier/tests.h>`, patches map/program/BTF/kfunc placeholders, loads each program with expected verifier options, validates accept/reject behavior and verifier log substrings, optionally runs accepted programs, checks translated instruction rewrites, and executes privileged and unprivileged variants.

## Important APIs, Types, And Functions
- `struct bpf_test` is the central test descriptor: instruction arrays, generated instruction helper, expected/unexpected translated instruction subsequences, fixup indexes for many map types, kfunc BTF ID fixups, expected verifier strings, result modes, flags, runtime data, attach type, func info, and custom BTF.
- Fill helpers such as `bpf_fill_ld_abs_vlan_push_pop()`, `bpf_fill_jump_around_ld_abs()`, `bpf_fill_rand_ld_dw()`, `bpf_fill_scale()`, `bpf_fill_torturous_jumps()`, and `bpf_fill_big_prog_with_loop_1()` generate very large or dynamic programs.
- Fixture creators include `create_map()`, `create_prog_array()`, `create_map_in_map()`, `create_cgroup_storage()`, `create_map_spin_lock()`, `create_sk_storage_map()`, `create_map_timer()`, and `create_map_kptr()`.
- BTF/kfunc support uses `load_btf_spec()`, `load_btf_for_test()`, `btf__load_testmod_btf()`, `fixup_prog_kfuncs()`, and `kfuncs_cleanup()`.
- Core execution is `do_test_fixup()`, `do_test_single()`, `do_prog_test_run()`, `check_xlated_program()`, `cmp_str_seq()`, `test_as_unpriv()`, `do_test()`, and `main()`.

## Control Flow
`main()` parses `-v`/`-vv` and optional test index/range, determines whether the process has `CAP_BPF`, `CAP_NET_ADMIN`, and `CAP_PERFMON`, checks the unprivileged-BPF sysctl and JIT status, enables libbpf strict mode, initializes deterministic-random support, and calls `do_test()`. `do_test()` reloads `bpf_testmod.ko`, iterates selected descriptors, runs applicable unprivileged and privileged forms, and unloads the module. `do_test_single()` applies fixups, loads custom BTF if requested, prepares `bpf_prog_load_opts`, loads the program, compares load result/log with expectations, verifies processed-instruction counts, inspects translated instructions for expected/unexpected subsequences, runs `bpf_prog_test_run_opts()` for accepted programs, updates pass/error counters, and closes all fds.

## State And Persistence
Process-local state includes global verifier log buffer `bpf_vlog`, skip count, JIT/unprivileged flags, cached BTF handles, generated instruction buffers, and map fd arrays. Kernel state includes transient BPF maps/programs/BTF objects, loaded `bpf_testmod.ko`, capability changes, and module BTF fds. The test closes map/program/BTF fds per case, unloads `bpf_testmod`, and frees cached BTF on completion.

## Dependencies And Integration Points
It depends on generated verifier case headers, libbpf BPF/BTF APIs, Linux BPF instruction macros, capability helpers, unprivileged helpers, BPF random helper, test BTF macros, `testing_helpers`, kernel BPF features, `bpf_testmod.ko`, and architecture config such as efficient unaligned access and JIT enablement.

## Risks And Edge Cases
The descriptor ABI is large and easy to misuse: wrong fixup indexes, missing expected strings, or stale BTF type IDs can make tests fail for harness reasons. Capability toggling is sensitive; unprivileged tests must disable admin caps but temporarily re-enable them for `BPF_PROG_TEST_RUN` when needed. Very large generated programs stress allocation and verifier limits. Kernel feature probing can skip tests, so skip counts must be interpreted with environment context. `bpf_vlog` is huge and global; log comparisons depend on stable verifier wording.

## Test Signals
Each case prints `#idx/u` and/or `#idx/p` with `OK`, `SKIP`, or detailed `FAIL` logs. Final output is `Summary: P PASSED, S SKIPPED, F FAILED`, and process exit is failure when any errors occurred. Additional signals include translated-instruction mismatch dumps under verbose mode and expected verifier log substring mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_verifier.c -->

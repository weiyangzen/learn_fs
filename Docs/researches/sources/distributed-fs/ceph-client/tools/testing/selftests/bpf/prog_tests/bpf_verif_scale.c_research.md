# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_verif_scale.c

## Purpose
This file is a verifier scalability harness. It loads a collection of prebuilt BPF object files with selected program types to ensure large programs, loops, subprograms, open-coded iterators, and helper-based loops remain within verifier limits or fail when intentionally invalid.

## Important APIs, Types, And Functions
The core helpers are `libbpf_debug_print()`, `check_load()`, and `scale_test()`. Individual entry points call `scale_test()` for each BPF object, including `test_verif_scale1/2/3`, many `pyperf*` variants, `loop*` variants, `strobemeta*`, sysctl loop tests, XDP, SEG6 local, and `twfw`. It uses `bpf_object__open_file()`, `bpf_object__next_program()`, `bpf_program__set_type()`, `bpf_program__set_flags()`, `bpf_program__set_log_level()`, and `bpf_object__load()`.

## Control Flow
Each exported test function is independent and loads one object file. `check_load()` opens the object, selects the first program, sets the requested program type and testing flags, requests verifier log level 4 plus global extra flags, loads the object, closes it, and returns the load result. `scale_test()` optionally installs a debug print callback when `env.verifier_stats` is enabled, then asserts success or failure.

## State And Persistence Behavior
No BPF object is retained after the load check; `bpf_object__close()` always releases it. Global state touched by this file is limited to optional libbpf print callback replacement and `extra_prog_load_log_flags`. No maps, links, sockets, or pinned paths persist.

## Dependencies And Integration Points
It depends on a large set of `.bpf.o` fixtures, the BPF verifier, libbpf, selftest environment flags, and correct program-type selection for each fixture. It integrates with test harness settings such as `env.verifier_stats` and `testing_prog_flags()`.

## Risks And Edge Cases
The tests are sensitive to verifier complexity accounting, instruction limits, compiler output, object availability, and program type support. `loop3.bpf.o` is intentionally expected to fail; if verifier behavior changes, that failure expectation may need updating. Debug printing has a suspicious `vprintf("%s", args)` pattern that relies on the harness path and is only used for stats logging.

## Test Signals
Passing signals are successful loads for all non-failing fixtures, failure for `loop3.bpf.o`, and optional verifier logs when stats are enabled. Because each object is closed immediately, resource leaks should be minimal.

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/arena_atomics.c

Purpose: validates atomic operations on BPF arena memory, including arithmetic/bitwise atomics, compare-and-exchange, exchange, use-after-free recovery, and optional load-acquire/store-release semantics.

Important APIs/types/functions: uses generated `arena_atomics.skel.h`. Per-operation helpers (`test_add`, `test_sub`, `test_and`, `test_or`, `test_xor`, `test_cmpxchg`, `test_xchg`, `test_uaf`, `test_load_acquire`, `test_store_release`) run individual BPF programs with `bpf_prog_test_run_opts` and inspect `skel->arena`, `skel->data`, and `skel->bss`.

Control flow: `test_arena_atomics` opens the skeleton, skips all tests if the BPF object reports missing compiler/JIT support, loads it, stores the current PID, and dispatches named subtests. Each subtest runs one program directly and asserts exact arena values/results.

State and persistence behavior: arena memory is mapped through the skeleton and mutated by BPF programs, then inspected from userspace. State is per skeleton instance and destroyed at cleanup. Optional support flags in `.data` drive skip behavior.

Dependencies and integration points: relies on libbpf skeleton generation, arena map support, BPF atomics compiler support, `test_progs.h` assertions, and `bpf_prog_test_run_opts`.

Risks: load-acquire/store-release tests are capability-gated and skip if toolchain or JIT lacks support, so they may not exercise on every environment. Return-value and arena-value assertions assume the paired BPF source keeps field names/semantics stable.

Test signals: exact `ASSERT_EQ` checks for every expected arena field, plus skip annotations for unsupported atomics or memory-order operations.

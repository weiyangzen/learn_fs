# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/arena_atomics.c

## Purpose

BPF arena atomic operation test program. It exercises add/sub/bitwise/cmpxchg/xchg atomics, optional use-after-free recovery paths, and load-acquire/store-release instructions on arena globals. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`BPF_MAP_TYPE_ARENA`, `__arena_global`, GCC/C11 atomic builtins, inline encoded `BPF_LOAD_ACQ`/`BPF_STORE_REL`, `bpf_arena_alloc_pages()`, `bpf_arena_free_pages()`, `bpf_get_current_pid_tgid()`, raw tracepoint/syscall sections, and feature macros such as `ENABLE_ATOMICS_TESTS` and `__BPF_FEATURE_ADDR_SPACE_CAST`.

## Control Flow

Raw tracepoint programs filter by `pid`, perform one class of atomic operation, and store old/new values into arena globals for userspace assertions. Unsupported compiler/arch combinations set skip flags. The UAF path allocates and frees an arena page, then tries many atomic operations to verify recovery/fault accounting. Load/store acquire/release paths emit raw instructions when supported.

## State and Persistence Behavior

Arena map pages and many arena global variables carry expected values/results. `skip_all_tests` and `skip_lacq_srel_tests` communicate feature availability to userspace.

## Dependencies and Integration Points

It depends on BPF CO-RE/libbpf helper headers, section annotations, generated skeleton loading from the selftest harness, and kernel verifier support for the program type, map type, helpers, kfuncs, and BTF metadata declared here. It also depends on compiler BPF feature macros and architecture support for arena atomics.

## Risks and Edge Cases

Highly feature-gated; clang version, target architecture, and kernel verifier/JIT atomic support determine coverage. Raw instruction encoding must match kernel opcode definitions.

## Test Signals

Userspace should observe skip flags when unsupported and exact result globals for each atomic operation when enabled; UAF recovery counter behavior is a key safety signal.

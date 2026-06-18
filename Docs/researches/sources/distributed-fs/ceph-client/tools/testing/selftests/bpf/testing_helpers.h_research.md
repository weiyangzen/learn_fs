<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/testing_helpers.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/testing_helpers.h

## Purpose
`testing_helpers.h` declares shared helper APIs implemented by `testing_helpers.c` and provides a small monotonic-time inline for BPF selftest harnesses.

## Important APIs, Types, And Functions
- Stringification macros `TO_STR()` support compile-time macro-to-string conversion.
- Parser declarations cover numeric lists and test/subtest filter lists.
- BPF load helpers include `bpf_prog_test_load()` and `bpf_test_load_program()`.
- Module helpers include `load_bpf_testmod()`, `unload_bpf_testmod()`, generic load/unload functions, and direct syscall declarations.
- `get_time_ns()` returns `CLOCK_MONOTONIC` nanoseconds.
- `get_xlated_program()`, `testing_prog_flags()`, and `is_jit_enabled()` support verifier and runner diagnostics.

## Control Flow
The header has no complex flow; callers invoke helpers to parse inputs, load BPF programs/modules, or query kernel state.

## State And Persistence
No state is owned in the header. The inline time helper reads system monotonic time only.

## Dependencies And Integration Points
It depends on libbpf and BPF headers and forward-declares `struct test_filter_set` and `struct bpf_insn` for consumers.

## Risks And Edge Cases
The declarations are a broad contract used by many tests; signature drift will produce widespread build failures. `get_time_ns()` assumes `clock_gettime()` succeeds and does not report errors.

## Test Signals
Problems appear as build/link errors or runtime failures in consumers that load BPF objects, parse filters, or inspect translated programs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/testing_helpers.h -->

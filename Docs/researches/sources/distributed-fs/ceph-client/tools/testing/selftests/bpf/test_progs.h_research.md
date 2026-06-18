<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_progs.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_progs.h

## Purpose
`test_progs.h` defines the shared user-space API and data model for BPF selftests that run under `test_progs.c`. It centralizes runner state structures, assertion/reporting macros, worker IPC messages, helper declarations, architecture-specific syscall probe names, BPF test module constants, and skeleton test-loader support.

## Important APIs, Types, And Functions
- `enum verbosity`, `struct test_filter`, `struct test_filter_set`, and `struct test_selector` model top-level and subtest filtering.
- `struct subtest_state`, `struct test_state`, and `struct test_env` describe current execution, result counters, log buffers, worker sockets, watchdog settings, and environment flags.
- `enum msg_type` and `struct msg` define parent/worker protocol messages: `MSG_DO_TEST`, `MSG_TEST_DONE`, `MSG_TEST_LOG`, `MSG_SUBTEST_DONE`, and `MSG_EXIT`.
- Assertion/reporting macros `PRINT_FAIL`, `CHECK`, `ASSERT_*`, `SYS`, `SYS_FAIL`, and `SYS_NOFAIL` update runner failure state and emit standardized messages.
- Utility declarations expose runner callbacks, map/stack comparison helpers, sysctl/testmod helpers, `netns_new()`/`netns_free()`, libbpf log capture, ID lookup, and `RUN_TESTS(skel)`.

## Control Flow
Tests call `test__start_subtest()` or `test__start_subtest_with_desc()` before subtest work, then use assertion macros to record failures. The macros evaluate expressions once, preserve `errno`, print PASS/FAIL text, and delegate failure accounting to `test__fail()`. `SYS` wrappers execute shell commands and jump to caller-specified labels on unexpected success/failure. Skeleton tests can use `RUN_TESTS()` to initialize a local `struct test_loader`, run generated ELF bytes, and finalize resources.

## State And Persistence
The header itself owns no persistent storage except extern declarations; it defines how `env` and per-test state are interpreted by all test sources. Assertion macros mutate the global runner state through `test__fail()`. `SYS_NOFAIL` may create or remove external system state depending on its command.

## Dependencies And Integration Points
It pulls in Linux BPF, network, perf, socket, and libbpf headers plus `test_iptunnel_common.h`, `bpf_util.h`, `trace_helpers.h`, and `testing_helpers.h`. It is the contract between individual BPF selftests, helper libraries, and the `test_progs` runner.

## Risks And Edge Cases
Macros evaluate and print typed values as `long long`, which is useful but can be awkward for pointers or unsigned widths. The command execution macros depend on shell command length and environment. `SYS_NANOSLEEP_KPROBE_NAME` is architecture-specific and must match kernel syscall naming. `ASSERT_MEMEQ` always prints hexdumps after checking, so output can be noisy. Worker IPC struct sizes are fixed; mismatches with `test_progs.c` would break parallel execution.

## Test Signals
Good consumers produce standardized `PASS`/`FAIL` messages and update summary counters. Header-level regressions usually appear as build failures, missing prototypes, incorrect subtest counts, broken worker protocol, or runner assertions no longer recording failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_progs.h -->

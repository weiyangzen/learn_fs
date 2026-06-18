
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/kprobe_multi_test.c

## Purpose

`kprobe_multi_test.c` is the main kprobe-multi selftest harness. It validates skeleton attach, raw link creation by symbols and addresses, libbpf attach helpers, invalid option handling, sessions, cookies, unique-match behavior, override-return restrictions, write-context rejection, duplicate symbol resolution, and verifier cases.

## Important APIs, Types, and Functions

It uses `kprobe_multi.skel.h`, empty/override/session/cookie/verifier/write-ctx/sleepable skeletons, `trace_helpers.h`, kallsyms helpers, `bpf_link_create()`, `bpf_program__attach_kprobe_multi_opts()`, `bpf_program__attach_kprobe()`, `bpf_prog_test_run_opts()`, `prctl()`, and `RUN_TESTS(kprobe_multi_verifier)`. Options include symbol arrays, address arrays, wildcard patterns, return probes, cookies, and `unique_match`.

## Control Flow and Data Flow

The test loads kallsyms, then runs subtests. Positive paths attach to `bpf_fentry_test1..8`, trigger a BPF program, and assert entry/return result fields. Negative attach paths exercise conflicting option combinations, nonexistent patterns/names, huge counts, and sleepable programs. Session tests count entry/exit firings and cookie propagation. Override tests check `bpf_override_return` can attach only to error-injection targets and can change `prctl()` return. Bench helpers attach to many kernel/module symbols for timing in a separate serial entry point.

## State, Dependencies, Integration Points, Risks, and Test Signals

State includes kprobe links, skeleton BSS result counters, kallsyms caches, and temporary override hooks. Dependencies are kprobe-multi, ftrace/kallsyms visibility, bpf_testmod for duplicate symbols, error-injection symbol availability, and architecture support for write-context test. Integration is libbpf kprobe-multi option validation and kernel attachment semantics. Risks include symbol availability, swapped subtest labels for addrs/syms in the entry function, exact errno expectations, and global side effects from override probes. Test signals are all result counters equal to expected values, invalid attaches returning expected negative errno, override `prctl()` returning 123 only when attached, and verifier suite passing.

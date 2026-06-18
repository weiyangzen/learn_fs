# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/uprobe_multi_test.c

## Purpose
Large coverage test for uprobe multi attach APIs, link-create APIs, USDT attach through uprobes, pid filtering, consumer combinations, session uprobes, cookies, recursion, verifier cases, and attach/detach benchmark behavior.

## APIs, Types, and Functions
Entry point `test_uprobe_multi_test()` dispatches many subtests. It defines target functions `uprobe_multi_func_[123]`, `usdt_trigger()`, `uprobe_session_recursive()`, child process/thread orchestration helpers, `test_skel_api()`, attach API helpers, negative attach tests, raw `bpf_link_create()` tests, consumer-combination generators, pid-filter tests, session tests, and benchmark tests.

## Control Flow, State, and Persistence
Basic tests attach skeleton-generated or manual uprobe/uretprobe/sleepable links to three functions and optionally a child pid or thread, trigger functions, and assert BSS hit counts and pid/tid filtering. Attach API tests cover pattern matching and explicit symbol lists; link API tests resolve ELF offsets manually. Negative tests exercise invalid counts, pointers, paths, flags, pids, trap instruction attach failure, and refcount offset conflicts. Consumer tests run all 16 before/after combinations of entry, return, and session consumers across threads. Session tests validate entry/return counts, cookies, and recursive cookie lifetimes. Benchmarks attach to many probes in `./uprobe_multi` and count 50000 hits.

## Dependencies and Integration
Depends on many generated skeletons, libbpf internal ELF symbol resolution, `clone`, `fork`, pthreads, `/proc/self/exe`, selftest binary `./uprobe_multi`, USDT macros, and raw `BPF_TRACE_UPROBE_MULTI` link creation.

## Risks and Test Signals
Risks include architecture-specific trap behavior, symbol resolution fragility, child cleanup complexity, high concurrency in consumer tests, and benchmark runtime. Signals are exact BSS hit counters, no bad pid flags, expected kernel errors for invalid link options, `-E2BIG` where limits are exceeded, correct session cookie results, verifier subtests passing, and benchmark counts of 50000.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/test_fprobe.c -->
# sources/distributed-fs/ceph-client/lib/tests/test_fprobe.c

## Purpose
KUnit sanity tests for the fprobe infrastructure, validating entry probes, return probes, symbol-list registration, per-entry data, skipped exits, and multiple fprobes on one target.

## APIs, Types, and Functions
The suite uses `struct fprobe`, `register_fprobe()`, `register_fprobe_syms()`, `unregister_fprobe()`, `ftrace_regs_get_return_value()`, `ftrace_location_range()`, and kallsyms lookup helpers. Target functions `fprobe_selftest_target()` and `fprobe_selftest_target2()` are `noinline` and called through function pointers. Handlers include `fp_entry_handler()`, `fp_exit_handler()`, `entry_only_handler()`, `fprobe_entry_multi_handler()`, and `fprobe_exit_multi_handler()`.

## Control Flow, State, and Persistence
`fprobe_test_init()` seeds `rand1`, installs indirect target pointers, and resolves ftrace locations. Each test sets `current_test`, registers probes for a symbol pattern or symbol list, calls target functions, asserts handler side effects, and unregisters probes. Entry handlers assert non-preemptible execution and correct instruction pointer; exit handlers assert return values and optional `entry_data_size` storage. `test_fprobe_skip()` makes the entry handler return nonzero to suppress the exit handler. Multi-probe tests register two probes in both orders and validate all handlers fire once.

## Dependencies and Integration
Depends on fprobe/ftrace, kallsyms, random number generation, KUnit, and architecture support for function tracing. It integrates with dynamic instrumentation internals and may be built only when fprobe support is available.

## Risks and Test Signals
Risks include target inlining despite safeguards, missing ftrace locations, architecture-specific return register handling, global state shared across tests, and cleanup sensitivity if registration fails partway. Test signals include handler call counts, return-value validation, `fp.nmissed` behavior, data handoff through entry storage, and multi-registration order coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/test_fprobe.c -->

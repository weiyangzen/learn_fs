<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_progs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_progs.c

## Purpose
`test_progs.c` is the main user-space runner for libbpf/BPF program selftests. It discovers test entry points from `<prog_tests/tests.h>`, applies command-line filtering, runs tests serially or through forked workers, captures per-test and per-subtest logs, manages watchdog timeouts, cgroup and network namespace cleanup, optional traffic monitoring, JSON summaries, and final pass/skip/fail accounting.

## Important APIs, Types, And Functions
- Global `struct test_env env` stores filters, verbosity, current test/subtest state, worker metadata, watchdog state, CPU count, JSON output, and BPF test module availability.
- `struct prog_test_def` maps generated test names to weak `test_*` or `serial_test_*` functions and tracks whether each test should run.
- Filtering helpers include `glob_match()`, `should_run()`, `should_run_subtest()`, `should_tmon()`, plus parser calls from `testing_helpers.c`.
- Test lifecycle APIs exported through `test_progs.h` include `test__start_subtest_with_desc()`, `test__end_subtest()`, `test__skip()`, `test__fail()`, `test__join_cgroup()`, `bpf_find_map()`, `compare_map_keys()`, `compare_stack_ips()`, `netns_new()`, `netns_free()`, `trigger_module_test_read()`, `trigger_module_test_write()`, `write_sysctl()`, and BTF trampoline helpers.
- Worker IPC uses `struct msg` from `test_progs.h`, `send_message()`, `recv_message()`, `dispatch_thread()`, `worker_main()`, `worker_main_send_log()`, and `worker_main_send_subtests()`.
- Logging uses `stdio_hijack()`, `stdio_hijack_init()`, `stdio_restore()`, `dump_test_log()`, and libbpf capture helpers `start_libbpf_log_capture()` / `stop_libbpf_log_capture()`.

## Control Flow
`main()` installs crash handling, parses `argp` options, switches into a flavor subdirectory if the executable name has a suffix, initializes watchdog/libbpf/session key/traffic monitor state, detects JIT and CPU count, and conditionally loads `bpf_testmod.ko`. It builds `prog_test_defs[]` from generated weak declarations, validates exactly one normal or serial entry point per test, then either lists/counts tests, forks worker processes, or runs tests in-process. `run_one_test()` saves logs, optionally creates a network namespace for `ns_*` tests, invokes the test function, closes active subtests, restores stdio, resets CPU affinity and network namespace, cleans per-test cgroups, stops libbpf capture, and dumps logs. Parallel mode forks worker children connected by `SOCK_SEQPACKET` socketpairs; dispatcher threads assign non-serial tests and collect logs/subtest results, then serial tests run in the parent before `calculate_summary_and_print_errors()` emits text or JSON results.

## State And Persistence
Most state is process-local: `env`, `test_states[]`, generated `prog_test_defs[]`, worker sockets/pids, current test index, and memory streams. Persistent or kernel state includes loaded `bpf_testmod.ko`, cgroup trees, netns objects, session keyring entries, sysctl writes requested by tests, BPF objects/maps/programs loaded by individual tests, and optional JSON output file. The runner attempts cleanup for module, cgroup, netns, stdio, and dynamically allocated filter/test-state memory at exit.

## Dependencies And Integration Points
The file integrates libbpf (`bpf/bpf.h`, `bpf/libbpf.h`, `bpf/btf.h`), generated BPF test lists, `testing_helpers`, `cgroup_helpers`, `network_helpers`, `traffic_monitor`, `json_writer`, `verification_cert`, kernel keyctl, namespaces, pthreads, timers, and Linux BPF/cgroup/test module infrastructure. Tests include this runner contract through `test_progs.h`.

## Risks And Edge Cases
The runner is sensitive to cleanup ordering after crashes or worker IPC failures; leaked netns/cgroups/modules can affect later tests. `stdio_hijack()` relies on glibc `open_memstream()` and uses global `stdout`/`stderr`, so concurrent output needs locking. Watchdog SIGSEGV termination intentionally turns hangs into crashes but can obscure root causes. Tests that manipulate affinity, namespaces, sysctls, cgroups, or modules can leave global state if they exit early. Parallel mode excludes serial tests but still shares module and process environment assumptions.

## Test Signals
Healthy execution prints per-test lines and a final `Summary: X/Y PASSED, Z SKIPPED, W FAILED`; `--count`, `--list`, `--json-summary`, `--workers`, `--watchdog-timeout`, filters, and traffic-monitor options exercise the runner. Failures are visible as nonzero exit status, forced logs, watchdog messages, protocol errors in worker mode, or JSON `failed=true` entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_progs.c -->

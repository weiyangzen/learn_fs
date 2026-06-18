# Research: subset-b-006822

Grouped research for BPF selftest runner, verifier, sockmap, tracing, USDT, XDP/XSK, and helper sources under `sources/distributed-fs/ceph-client/tools/testing/selftests/bpf`.

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_select_reuseport_common.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_select_reuseport_common.h

## Purpose
This header defines shared constants and wire/data structures for reuseport selection tests. It is consumed by user-space and BPF-side code to agree on test outcomes, control commands, and packet metadata validation fields.

## Important APIs, Types, And Functions
- `enum result` names BPF/user-visible outcomes such as inner-map failure, skb data failure, selection failure, miscellaneous drop, pass, and pass-with-select failure.
- `struct cmd` carries `reuseport_index` and `pass_on_failure` settings into a BPF map or test command path.
- `struct data_check` stores expected IP protocol, skb addresses, ports, Ethernet protocol, bind-in-any flag, length, and hash. The zero-length `equal_check_end` marker separates fields that should be compared for equality from trailing metadata.

## Control Flow
The header has no executable control flow. Test programs populate `struct cmd` to drive selection behavior and compare populated `struct data_check` data against observed skb metadata to decide which `enum result` bucket is incremented.

## State And Persistence
No storage is defined here. State persists only when these structures are embedded in BPF maps or user-space test buffers.

## Dependencies And Integration Points
It depends only on `<linux/types.h>` and integrates with select-reuseport BPF programs and user-space harnesses elsewhere in the BPF selftest tree.

## Risks And Edge Cases
Layout is part of the ABI between BPF and user space; reordering fields, changing widths, or moving `equal_check_end` can silently break map value comparisons. Address array sizing must match IPv4/IPv6 expectations in consuming tests.

## Test Signals
Failures show up as mismatched result counters or data-check comparisons in reuseport tests, commonly mapped to `DROP_ERR_*` or `PASS_ERR_SK_SELECT_REUSEPORT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_select_reuseport_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_sockmap.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_sockmap.c

## Purpose
`test_sockmap.c` is a standalone user-space stress and functional test driver for sockmap/sockhash, SK_SKB, SK_MSG, cgroup sockops, ingress redirection, TLS interaction, and sendmsg/sendpage behavior. It loads `test_sockmap_kern.bpf.o` or `test_sockhash_kern.bpf.o`, attaches BPF programs to maps and cgroups, creates loopback TCP pairs, drives traffic, and validates forwarding, drops, cork/apply/push/pop transformations, and data integrity.

## Important APIs, Types, And Functions
- Global sockets `s1`, `s2`, `c1`, `c2`, `p1`, `p2` model two connected TCP pairs.
- Global flags such as `txmsg_pass`, `txmsg_redir`, `txmsg_drop`, `txmsg_apply`, `txmsg_cork`, `txmsg_start_push`, `txmsg_pop`, `txmsg_ingress`, `txmsg_redir_skb`, `txmsg_ktls_skb`, `ktls`, and `peek_flag` configure BPF behavior.
- `struct sockmap_options` stores verbosity, base/sendpage/data-test mode, expected drop behavior, iovec size/count, rate, map object name, and whitelist/blacklist strings.
- `sockmap_init_sockets()` creates, binds, listens, connects, and accepts the two TCP pairs. `sockmap_init_ktls()` enables TLS ULP and TX/RX crypto info.
- `msg_alloc_iov()`, `msg_loop()`, `msg_loop_sendpage()`, `msg_verify_date_prep()`, and `msg_verify_data()` drive traffic and validate byte streams under push/pop transforms.
- `run_options()` attaches BPF programs, populates BPF maps, runs ping-pong/sendmsg/sendpage/base variants, detaches links, zeroes maps, and closes sockets.
- Test families include `test_txmsg_pass()`, `test_txmsg_redir()`, `test_txmsg_drop()`, `test_txmsg_skb()`, `test_txmsg_apply()`, `test_txmsg_cork()`, `test_txmsg_push()`, `test_txmsg_pull()`, `test_txmsg_pop()`, and `test_txmsg_push_pop()`.

## Control Flow
`main()` parses long options, creates or opens a cgroup, enables libbpf strict mode, and either runs the full selftest suite or one requested traffic mode. Full suite mode calls `test_selftest()`, which runs sockmap, sockhash, and kTLS-prefixed variants. Each suite loads the selected BPF object with `populate_progs()`, filters the test array by whitelist/blacklist, resets global flags per subtest, and calls the selected test function. Each subtest sets global BPF-option flags and delegates through `test_send*()` to `test_exec()` and `run_options()`. Traffic execution forks RX and TX children, uses `sendmsg()`/`sendfile()` and `recvmsg()` with timeouts, then reports child exit status.

## State And Persistence
The file uses extensive process-global state for sockets, BPF map/program/link handles, counters, and current txmsg flags. Kernel state includes cgroups, BPF programs/maps/links, sockmap/sockhash contents, TCP sockets, optional kTLS state, iptables-independent loopback traffic, and socket buffer settings. `run_options()` attempts to detach cgroup sockops, detach all map links, reset map entries to zero, and close all socket fds after each run.

## Dependencies And Integration Points
It depends on libbpf, `bpf/bpf.h`, `cgroup_helpers.h`, `bpf_util.h`, Linux TLS, sockmap attach APIs, cgroup BPF attachment, local BPF objects `test_sockmap_kern.bpf.o` and `test_sockhash_kern.bpf.o`, and root/CAP_NET_ADMIN-capable networking. It complements kernel-side sockmap selftest programs in the same directory.

## Risks And Edge Cases
The driver is highly stateful; missing `test_reset()` or failed cleanup can cross-contaminate later tests. Fixed loopback ports `10000` and `10001` can collide. Forked TX/RX children complicate errno propagation. Data-integrity math for push/pop/cork/apply is subtle and deliberately disables data checking for some cork combinations. kTLS support is kernel/config dependent. BPF program order and map names in `populate_progs()` must match the object exactly.

## Test Signals
The suite prints per-subtest lines of the form `sockmap|sockhash:...:OK/FAIL` and final `Pass: N Fail: M`. A healthy specific run returns zero from `run_options()`. Failures are visible as child nonzero exit, data verification `EDATAINTEGRITY`, select timeouts, map update/attach errors, or unexpected send success/drop behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_sockmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_tag.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_tag.c

## Purpose
`test_tag.c` verifies that kernel-reported BPF program tags match the SHA-256-derived tag computed over the program instruction stream. It exercises both immediate-only programs and programs containing map-FD pseudo instructions.

## Important APIs, Types, And Functions
- Global `prog[BPF_MAXINSNS]` holds generated instruction streams.
- `bpf_gen_imm_prog()` fills programs with random `BPF_MOV` immediates and an exit.
- `bpf_gen_map_prog()` fills alternating `BPF_LD_MAP_FD` instruction pairs and terminates with an exit.
- `bpf_try_load_prog()` loads generated programs with `bpf_test_load_program()`, then regenerates map programs with fd zero to compute the normalized tag.
- `tag_from_fdinfo()` parses `prog_tag:` from `/proc/<pid>/fdinfo/<progfd>`.
- `tag_from_alg()` computes SHA-256 through the kernel AF_ALG hash API and reads the first 8 bytes.
- `do_test()` iterates instruction counts up to `BPF_MAXINSNS` and compares tags.

## Control Flow
`main()` enables libbpf strict mode, creates a small hash map, and repeats two test sweeps five times: immediate programs starting at two instructions and map-FD programs starting at three instructions. Each generated program is loaded, its fdinfo tag is read, the normalized instruction stream is hashed through AF_ALG, and mismatches call `tag_exit_report()` with both tags.

## State And Persistence
State is local to the process except for a transient BPF hash map, loaded BPF programs, AF_ALG sockets, and `/proc` fdinfo reads. Program fds are closed per iteration; the map fd is closed at exit.

## Dependencies And Integration Points
The test uses Linux BPF instruction macros, libbpf/bpf syscalls, `testing_helpers.c`, AF_ALG `sha256`, `/proc/<pid>/fdinfo`, and scheduler yields to avoid monopolizing CPU during large sweeps.

## Risks And Edge Cases
`assert()` is used for expected system support and load success, so unsupported AF_ALG/BPF environments abort rather than report graceful skips. The random immediate stream is seeded with current time, so exact generated programs vary. Map-FD normalization is essential; hashing real fd values would make tags unstable.

## Test Signals
Success prints `test_tag: OK (<count> tests)`. Any tag mismatch prints the instruction count, whether a map was used, fdinfo tag, AF_ALG tag, and exits with failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_tag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_tcp_hdr_options.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_tcp_hdr_options.h

## Purpose
This header provides shared structures, constants, and BPF-side helpers for tests that parse and write experimental TCP header options from `BPF_PROG_TYPE_SOCK_OPS` programs.

## Important APIs, Types, And Functions
- `struct bpf_test_option` is the packed experimental option payload containing flags, max delayed-ACK value, and random byte.
- `OPTION_*` enums and `OPTION_F_*` macros define resend, max-delack, and random test flags.
- `struct hdr_stg` stores per-socket state in `bpf_sk_storage`.
- `struct linum_err` records source line and error code for a local port in `lport_linum_map`.
- TCP flag and option constants define expected header encodings.
- Under `BPF_PROG_TEST_TCP_HDR_OPTIONS`, BPF map `lport_linum_map`, `tcp_hdrlen()`, `skops_tcp_flags()`, callback-flag setters/clearers, and `RET_CG_ERR()` are compiled for BPF programs.

## Control Flow
The header has no standalone entry point. BPF sockops programs include it to enable parse/write header callbacks, inspect `skb_tcp_flags`, update callback flags on `struct bpf_sock_ops`, and return `CG_ERR` through `RET_CG_ERR()` while recording line-specific diagnostics.

## State And Persistence
Shared state lives in BPF maps and socket storage created by consuming programs. `RET_CG_ERR()` persists the first error per local port with `BPF_NOEXIST` and clears header callback flags to avoid repeated processing after an error.

## Dependencies And Integration Points
It depends on BPF sockops context definitions, `SEC(".maps")`, `bpf_map_update_elem()`, `bpf_sock_ops_cb_flags_set()`, and TCP option layout shared with user-space validators.

## Risks And Edge Cases
The packed structs and max header constants must match kernel TCP option limits. Callback flag handling is delicate; leaving parse/write flags enabled after an error can cause noisy follow-on failures. `RET_CG_ERR()` assumes a `skops` variable is in scope.

## Test Signals
Consumers validate map entries, line numbers, and TCP option effects. Failures typically show incorrect option bytes, missing callback invocation, unexpected `CG_ERR`, or entries in `lport_linum_map`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_tcp_hdr_options.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_tcpbpf.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_tcpbpf.h

## Purpose
`test_tcpbpf.h` defines the shared global statistics structure for TCP BPF sockops selftests.

## Important APIs, Types, And Functions
- `struct tcpbpf_globals` records event-map hits, retransmits, data segments in/out, callback return-value test results, received and acknowledged bytes, listen/close counts, saved SYN state, and window-clamp values.

## Control Flow
There is no executable flow. Kernel BPF programs update instances of `struct tcpbpf_globals`, while user-space tests read and validate the fields after TCP traffic.

## State And Persistence
The structure is usually stored as a BPF map value and persists for the lifetime of the loaded test object.

## Dependencies And Integration Points
It is shared by TCP BPF kernel programs and user-space validators to keep map layout consistent.

## Risks And Edge Cases
Any layout change breaks ABI with precompiled BPF objects. Field sizes are fixed `__u32`/`__u64`; counters can wrap in long-running or high-volume tests, though selftests are bounded.

## Test Signals
Passing tests observe expected nonzero counters, callback return values, saved SYN flags, and byte accounting in this structure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_tcpbpf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_tcpnotify.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_tcpnotify.h

## Purpose
`test_tcpnotify.h` defines shared map/perf-event payload structures for the TCP notify sockops test.

## Important APIs, Types, And Functions
- `struct tcpnotify_globals` stores total retransmits and notifier call count.
- `struct tcp_notifier` is a four-byte perf event payload with sentinel fields `type`, `subtype`, `source`, and `hash`.
- `TESTPORT` fixes the TCP destination port used by the user-space test and iptables rule.

## Control Flow
No standalone control flow exists. BPF-side code populates `tcp_notify_globals` and emits `tcp_notifier` events; user-space validates the sentinel payload and compares callback counts.

## State And Persistence
State persists in BPF maps and perf buffers while the test object is loaded.

## Dependencies And Integration Points
It integrates `test_tcpnotify_user.c`, the matching BPF object, cgroup sockops attachment, and local TCP connection attempts.

## Risks And Edge Cases
The fixed port can conflict with other processes or firewall policy. Struct layout is a user/kernel ABI and must remain stable.

## Test Signals
Success requires `ncalls > 0` and a perf-event callback count equal to `ncalls` with sentinel bytes matching `0xde 0xad 0xbe 0xef`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_tcpnotify.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_tcpnotify_user.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_tcpnotify_user.c

## Purpose
`test_tcpnotify_user.c` is the user-space harness for a TCP sockops notification test. It loads `test_tcpnotify_kern.bpf.o`, attaches it to a cgroup, creates a perf buffer for notifications, uses iptables and `nc` to trigger TCP events, and validates that BPF map counters match received perf events.

## Important APIs, Types, And Functions
- `dummyfn()` validates `struct tcp_notifier` sentinel fields and increments `rx_callbacks`.
- `tcp_notifier_poller()` repeatedly calls `perf_buffer__poll()` until `exit_thread` is set.
- `poller_thread()` runs the perf poll loop in a pthread.
- `verify_result()` checks `tcpnotify_globals.ncalls > 0` and equality with `rx_callbacks`.
- `main()` owns cgroup setup, BPF object loading, sockops attach, map discovery, perf-buffer creation, iptables/nc trigger, map lookup, thread shutdown, and cleanup.

## Control Flow
The harness creates and joins cgroup `/foo`, loads the sockops BPF object with `bpf_prog_test_load()`, attaches it with `BPF_CGROUP_SOCK_OPS`, opens `perf_event_map` and `global_map`, then starts a perf polling thread. It installs an iptables drop rule for `TESTPORT`, runs `nc 127.0.0.1 TESTPORT` to induce TCP behavior, removes the drop rule, reads global stats, waits for late perf events, stops the thread, validates counts, prints `PASSED!`, and detaches/cleans resources.

## State And Persistence
External state includes cgroup hierarchy, attached BPF program, perf buffer, iptables INPUT rule, TCP connection attempt, and BPF map values. Cleanup detaches from the cgroup, closes cgroup fd, cleans cgroup environment, and frees the perf buffer; iptables cleanup only happens on the normal path after rule insertion.

## Dependencies And Integration Points
It depends on libbpf, pthreads, cgroup helpers, `testing_helpers`, `test_tcpnotify.h`, `iptables`, `nc`, perf events, and CAP_NET_ADMIN/root privileges.

## Risks And Edge Cases
If the process exits between adding and deleting the iptables rule, firewall state can be left behind. `sprintf()` into an 80-byte buffer is safe for current constants but brittle. The test sleeps 10 seconds for callbacks, making it slow and timing-sensitive. Missing `nc`, iptables backend differences, or insufficient privileges cause failures unrelated to BPF logic.

## Test Signals
Success prints `PASSED!` and returns zero. Failures include load/attach/map lookup errors, perf polling errors, iptables command failures, `pthread_join` failure, or count mismatch between `global_map.ncalls` and `rx_callbacks`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_tcpnotify_user.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_xdp_features.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_xdp_features.sh

## Purpose
This shell script exercises the `xdp_features` binary across a veth pair and network namespace for core XDP actions/features: PASS, DROP, ABORTED, TX, REDIRECT, and NDO_XMIT over IPv4-mapped and IPv6 targets.

## Important APIs, Types, And Functions
- Constants define namespace name and veth IPv4/IPv6 addresses.
- `setup()` creates a namespace, veth pair, addresses, enables links, sets GRO on, and disables TX checksumming.
- `cleanup()` deletes the veth root device, namespace, and any running `xdp_features` process.
- `wait_for_dut_server()` waits until `ss -tlp` sees `xdp_features`.
- `test_xdp_features()` starts a DUT server for each feature and runs the peer client in the namespace.

## Control Flow
The script uses `set -e`, installs cleanup traps, runs `setup`, then for each XDP feature starts `./xdp_features` on `v1` in the root namespace, waits for readiness, and invokes `ip netns exec $NS ./xdp_features -t ... v0` as the peer. Any failing client exits immediately. The final NDO_XMIT result is saved in `ret`, cleanup runs, and the script exits with that status.

## State And Persistence
External state includes a temporary netns, root `v1`, namespace `v0`, IP addresses, ethtool feature changes, and background `xdp_features` processes. Cleanup removes the namespace/device and kills matching processes by `pidof`.

## Dependencies And Integration Points
It depends on `ip`, `ethtool`, `ss`, network namespace support, veth support, the compiled `xdp_features` binary, and privileges for network setup and XDP attachment.

## Risks And Edge Cases
`pidof xdp_features` can kill unrelated instances. The readiness loop has no timeout and can hang if the server never listens. Trap signal `9` is ineffective because SIGKILL cannot be trapped. Device names `v1`/`v0` may collide. Cleanup after intermediate failures relies on traps.

## Test Signals
The script returns zero only when all feature subtests succeed. Any `xdp_features` client nonzero exit aborts. Successful cleanup and final `ret=0` indicate XDP feature support for the tested topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_xdp_features.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_xdping.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_xdping.sh

## Purpose
`test_xdping.sh` sets up a root/netns veth topology and exercises the `xdping` tool in skb and native driver modes, with and without a server, and with default and explicit count options.

## Important APIs, Types, And Functions
- Constants define target namespace, target IP, and local IP.
- `setup()` creates namespace `xdp_ns0`, veth pair, moves `veth0` into the namespace, assigns IPv4 addresses, and brings interfaces up.
- `cleanup()` deletes namespace/device and terminates any background server.
- `test()` optionally starts `xdping` server in the namespace, runs the root client, stops the server, and prints PASS text.

## Control Flow
With `set -e`, the script installs EXIT cleanup, creates topology, loops through no-server and skb server modes for client `-S` runs with and without `-c 10`, then runs native mode `-N` server/client pairs with and without `-c 10`. All `xdping` commands target `10.1.1.100`; any failure aborts before the final success line.

## State And Persistence
The script creates transient namespace, veth devices, IP addresses, XDP programs attached by `xdping`, and optional background server process. Cleanup deletes topology and kills the server pid.

## Dependencies And Integration Points
It depends on `ip`, namespace/veth support, XDP skb/native support on veth, the `xdping` binary, and network privileges.

## Risks And Edge Cases
The server startup uses fixed `sleep 10`, making the test slow and timing-dependent. Interface and namespace names are fixed and can collide. Native driver mode may be unsupported depending on device/kernel behavior.

## Test Signals
Success prints per-case PASS messages and `OK. All tests passed`. Any failed `xdping` invocation exits nonzero due to `set -e`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_xdping.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_xsk.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_xsk.sh

## Purpose
`test_xsk.sh` orchestrates AF_XDP selftests using `xskxceiver` over either generated veth pairs or a user-provided physical interface. It validates prerequisites, creates topology, runs softirq and busy-poll test suites, and reports aggregate status.

## Important APIs, Types, And Functions
- It sources `xsk_prereqs.sh`, which supplies `validate_root_exec`, `validate_veth_support`, `validate_ip_utility`, `exec_xskxceiver`, `cleanup_exit`, `cleanup_iface`, and `test_status`.
- Options support verbose mode, physical interface (`-i`), debug topology-only mode (`-d`), mode selection (`-m skb|drv|zc`), list tests (`-l`), selected test (`-t`), and help (`-h`).
- `setup_vethPairs()` creates randomized veth names, disables IPv6 if present, optionally configures busy-poll sysctls, sets MTU, and brings both links up.
- `ctrl_c()` cleanup handles interrupts.

## Control Flow
The script validates `/dev/urandom`, generates veth names, handles list/help early exits, validates privileges and veth/ip support unless a physical interface is supplied, builds `ARGS`, reports prerequisite status, optionally exits after printing debug interface arguments, runs `exec_xskxceiver` for a softirq pass, cleans up or resets the physical interface, enables busy-poll mode, recreates veths if needed, runs `exec_xskxceiver` again, cleans up, and prints a summary from `statusList`.

## State And Persistence
External state includes veth pairs, physical interface MTU/config changes, busy-poll sysfs knobs, AF_XDP sockets and UMEM created by `xskxceiver`, and arrays populated by prerequisite helpers. Cleanup is split between generated veth and physical interface paths.

## Dependencies And Integration Points
It depends on `xsk_prereqs.sh`, `xskxceiver`, root/CAP_NET_ADMIN, veth or physical NIC support, `/dev/urandom`, `ip`, sysfs network knobs, and kernel AF_XDP support.

## Risks And Edge Cases
Random veth suffix generation can produce collisions, though unlikely. The script assumes helper variables like `busy_poll`, `statusList`, `nameList`, and `XSKOBJ` are defined by the sourced prereq file. Physical-interface mode can disturb a real NIC and needs robust cleanup. The initial `retval=$?` before status reporting reflects the previous setup path, so helper behavior matters.

## Test Signals
Success prints `All tests successful!`; failures are collected in `statusList` and reported through `test_status`, with final nonzero exit when any suite failed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_xsk.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/testing_helpers.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/testing_helpers.c

## Purpose
`testing_helpers.c` implements common user-space helpers for BPF selftests: numeric and test-name filter parsing, BPF object/program loading with test flags, kernel module load/unload wrappers, RCU synchronization trigger, translated-program retrieval, perf sample-rate reading, and BPF JIT detection.

## Important APIs, Types, And Functions
- `parse_num_list()` parses comma/range expressions into boolean selection sets.
- `parse_test_list()` and `parse_test_list_file()` populate `struct test_filter_set`, using `insert_test()` and `do_insert_test()` for test/subtest patterns.
- `link_info_prog_id()` returns the attached program ID for a libbpf link fd.
- `testing_prog_flags()` probes and caches supported test flags `BPF_F_TEST_RND_HI32` and `BPF_F_TEST_REG_INVARIANTS`.
- `bpf_prog_test_load()` opens a BPF object, sets program type/flags, loads it, and returns object plus first program fd.
- `bpf_test_load_program()` wraps `bpf_prog_load()` for raw instruction arrays.
- Module helpers wrap `finit_module`, `delete_module`, load/unload module by path/name, and specifically load/unload `bpf_testmod.ko`.
- `kern_sync_rcu()` uses `membarrier`, `get_xlated_program()` reads rewritten BPF instructions, and `is_jit_enabled()` reads `/proc/sys/net/core/bpf_jit_enable`.

## Control Flow
Parsing helpers allocate or grow arrays as they consume comma-separated input or file lines. Loading helpers configure libbpf options, probe flags once, then propagate errors to callers. Module unload first triggers kernel-side RCU synchronization and retries `delete_module()` on `EAGAIN`. Translated program retrieval performs a two-step `bpf_prog_get_info_by_fd()` to get size then fetch instructions.

## State And Persistence
The file maintains global `extra_prog_load_log_flags` and a static cached flag mask in `testing_prog_flags()`. Kernel-persistent effects include loaded BPF programs, loaded/unloaded modules, and membarrier-triggered synchronization. Allocated filter strings are owned by the caller's selector cleanup.

## Dependencies And Integration Points
It depends on libbpf, `test_progs.h`, `disasm.h`, Linux membarrier, module syscalls, and BPF syscall APIs. It is used by `test_progs.c`, `test_verifier.c`, and many standalone BPF test harnesses.

## Risks And Edge Cases
`parse_num_list()` uses `realloc(set, new_len)` for bool bytes, which relies on `sizeof(bool)==1`. `parse_test_list_file()` treats a line with only one nonspace character carefully; parser bugs can affect runner filtering. Module load/unload requires privileges and can fail if the module is absent or busy. Cached test flags assume support does not change during the process.

## Test Signals
Helper regressions show as filter parse errors, missing selected tests, BPF object load failures, verifier translated-program checks failing, inability to load `bpf_testmod.ko`, or incorrect skip behavior when JIT/test flags are unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/testing_helpers.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/trace_helpers.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/trace_helpers.c

## Purpose
`trace_helpers.c` provides tracing-related utilities for BPF selftests: loading and searching kallsyms, resolving uprobe offsets and relative offsets, reading ELF build IDs, reading trace_pipe, and enumerating ftrace-attachable symbols or addresses.

## Important APIs, Types, And Functions
- Kallsyms support: `load_kallsyms_local_common()`, `load_kallsyms_local()`, `load_kallsyms_custom_local()`, `load_kallsyms()`, `ksym_search_local()`, `search_kallsyms_custom_local()`, `ksym_search()`, `ksym_get_addr_local()`, `ksym_get_addr()`, and `kallsyms_find()`.
- Uprobe helpers: `get_uprobe_offset()` and `get_rel_offset()` parse `/proc/self/maps` or use optional `PROCMAP_QUERY`.
- Build ID helpers: `parse_build_id_buf()` and `read_build_id()` parse ELF PT_NOTE GNU build-id notes.
- Trace pipe helpers: `read_trace_pipe_iter()` and `read_trace_pipe()`.
- Attachable symbol enumeration: `bpf_get_ksyms()` returns filtered names, while `bpf_get_addrs()` returns filtered addresses.
- Filtering helpers skip invalid kernel/module entries and known risky symbols such as idle, RCU, migration, preempt count, and BPF dispatcher functions.

## Control Flow
Kallsyms loaders read `/proc/kallsyms`, allocate symbol arrays with `libbpf_ensure_mem()`, add names, and sort by address or custom comparator. Search functions use binary search. Uprobe offset resolution first tries `PROCMAP_QUERY` and falls back to scanning `/proc/self/maps`; PPC64 ABIv2 adjusts for global entry-point stubs. Build-ID reading opens an ELF file, scans program headers for PT_NOTE, and extracts GNU notes. `bpf_get_ksyms()` cross-references `available_filter_functions` with kallsyms, deduplicates names through libbpf hashmap, and stores filtered symbols in the returned `struct ksyms`.

## State And Persistence
Global `ksyms` caches process-wide kallsyms behind `ksyms_mutex`. Local `struct ksyms` instances own dynamically allocated names, symbol arrays, and filtered symbol lists. Trace and proc reads do not persist state. Returned arrays must be freed through `free_kallsyms_local()` or caller-managed frees as documented by usage.

## Dependencies And Integration Points
It depends on procfs, tracefs/debugfs, libelf/gelf, libbpf internal hashmap/memory helpers, Linux perf/build-id constants, optional `PROCMAP_QUERY`, and architecture-specific uprobe semantics. It is used by kprobe/fentry/uprobe/fprobe tests and stack-symbolization helpers.

## Risks And Edge Cases
Kernel symbol visibility can be restricted by `kptr_restrict`, lockdown, or permissions. `ksym_search_local()` can read `syms[start]` when the key is above the last symbol if not carefully bounded by inputs. Tracefs paths differ by mount. `read_trace_pipe_iter()` has subtle precedence in `getline()` assignment and can spin on `EAGAIN`. Build-ID parsing trusts ELF note sizing and requires `BPF_BUILD_ID_SIZE`.

## Test Signals
Consumers fail with missing symbols, unresolved uprobe offsets, absent build IDs, inability to open tracefs files, or attach failures against filtered symbol sets. Verbose `PROCMAP_QUERY` output can help diagnose offset resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/trace_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/trace_helpers.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/trace_helpers.h

## Purpose
`trace_helpers.h` declares tracing helper data structures and APIs for kernel symbol lookup, trace-pipe reading, uprobe offset resolution, build-ID extraction, and ftrace symbol/address enumeration.

## Important APIs, Types, And Functions
- `SYS_PREFIX` maps architectures to syscall symbol prefixes.
- `ALIGN()` and `__ALIGN_MASK()` support ELF note parsing and other aligned metadata handling.
- `struct ksym` and `struct ksyms` model symbol address/name arrays plus filtered symbol lists.
- Function pointer typedefs allow custom sorting/searching comparators.
- Declarations cover kallsyms load/search, `kallsyms_find()`, trace-pipe readers, `get_uprobe_offset()`, `get_rel_offset()`, `read_build_id()`, `bpf_get_ksyms()`, and `bpf_get_addrs()`.

## Control Flow
No standalone flow exists; consumers call the declared helpers when preparing trace targets or decoding kernel/user addresses.

## State And Persistence
The header owns no state but defines ownership-bearing structures that implementations allocate and free.

## Dependencies And Integration Points
It includes libbpf for build ID sizing and integrates with `trace_helpers.c` and many BPF tracing tests.

## Risks And Edge Cases
`SYS_PREFIX` must track kernel symbol naming by architecture. Structure layout changes affect all consumers. Consumers must free `struct ksyms` correctly to avoid leaks.

## Test Signals
Regressions show as compile errors, inability to resolve syscall/kallsyms names, bad uprobe offsets, or trace attach failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/trace_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/unpriv_helpers.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/unpriv_helpers.c

## Purpose
`unpriv_helpers.c` decides whether unprivileged BPF verifier tests should be disabled. It considers the kernel `unprivileged_bpf_disabled` sysctl and CPU mitigation status, because some unprivileged tests rely on Spectre mitigations being enabled.

## Important APIs, Types, And Functions
- `open_config()` tries `/boot/config-$(uname -r)` then `/proc/config.gz`.
- `config_contains()` scans compressed kernel config for an exact option line.
- `cmdline_contains()` scans `/proc/cmdline` for a boot parameter.
- `get_mitigations_off()` returns true for `mitigations=off` or missing `CONFIG_CPU_MITIGATIONS=y`.
- `get_unpriv_disabled()` is the exported decision function.

## Control Flow
`get_unpriv_disabled()` first reads `/proc/sys/kernel/unprivileged_bpf_disabled`; if nonzero or unreadable, it disables unpriv tests. If sysctl permits unprivileged BPF, it calls `get_mitigations_off()` and disables unpriv tests if mitigations are off or cannot be determined.

## State And Persistence
No mutable persistent state exists. The helper reads procfs/boot config files and closes them.

## Dependencies And Integration Points
It depends on zlib `gzFile`, `uname`, procfs sysctl/cmdline, kernel config availability, and `unpriv_helpers.h`. `test_verifier.c` uses it to decide unprivileged test execution.

## Risks And Edge Cases
If kernel config is unavailable, the helper conservatively disables unprivileged tests. `cmdline_contains()` uses the token length in `strncmp(c, pat, strlen(c))`, which can match prefixes in a surprising way. Config scanning returns `-1` on EOF without a match, so absence and read errors are both treated as unknown/off.

## Test Signals
Verifier output will print that unprivileged execution cannot run when sysctl disables BPF. Otherwise skipped `/u` cases due to mitigation uncertainty indicate this helper returned disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/unpriv_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/unpriv_helpers.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/unpriv_helpers.h

## Purpose
`unpriv_helpers.h` exposes the unprivileged-BPF disablement check used by verifier-style tests.

## Important APIs, Types, And Functions
- `UNPRIV_SYSCTL` names `kernel/unprivileged_bpf_disabled`.
- `get_unpriv_disabled()` returns whether unprivileged tests should be treated as disabled.

## Control Flow
No flow exists in the header.

## State And Persistence
No state is defined.

## Dependencies And Integration Points
It includes `<stdbool.h>` and is consumed by `test_verifier.c`.

## Risks And Edge Cases
The sysctl macro omits `/proc/sys/` by design; callers that need a full path must prepend it.

## Test Signals
Compile-time consumers rely on this declaration; runtime behavior is in `unpriv_helpers.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/unpriv_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/uprobe_multi.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/uprobe_multi.c

## Purpose
`uprobe_multi.c` is a target executable for uprobe_multi and USDT tests. It defines one weak `uprobe()` function, many generated weak functions for bulk multi-uprobe attachment, many USDT probes for stress testing, and build-ID residency triggers.

## Important APIs, Types, And Functions
- Macro families `F10`, `F100`, `F1000`, and `F10000` generate definitions and calls for large numbers of weak functions.
- `bench()` calls 50,000 generated functions to trigger attached uprobes.
- `usdt()` fires 50,000 `STAP_PROBE(test, usdt)` probes.
- `trigger_uprobe(bool build_id_resident)` uses `madvise(MADV_POPULATE_READ/MADV_PAGEOUT)`, `mincore()`, and `uprobe()` to test build-ID page resident and paged-out cases.
- `main()` dispatches `bench`, `usdt`, `uprobe-paged-out`, and `uprobe-paged-in`.

## Control Flow
The selected mode runs one of the generated trigger loops or build-ID preparation path. For paged-out mode, it page-aligns `build_id_start`, populates it, repeatedly attempts to page it out and checks residency with `mincore()`, then calls `uprobe()`. Invalid arguments print usage and return `-1`.

## State And Persistence
State is limited to executable text, build-id mapped pages, and generated weak symbols. `madvise()` changes page residency but not persistent data.

## Dependencies And Integration Points
It depends on `<sdt.h>`, linker-provided `build_id_start`/`build_id_end`, Linux `madvise` constants, and BPF tests that attach uprobes/USDT probes to this executable.

## Risks And Edge Cases
The generated symbol count is huge and affects compile/link time and binary size. `MADV_PAGEOUT` is best-effort; the loop may not evict the page within 500 attempts. Usage text omits the paged-in/paged-out modes even though they are supported. Weak symbols can be overridden by link context.

## Test Signals
Consumers expect mode exit status zero and BPF-side counters matching the number of triggered functions/probes or one `uprobe()` call. Build-ID tests distinguish successful attach when build-id memory is resident versus paged out.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/uprobe_multi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/uptr_test_common.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/uptr_test_common.h

## Purpose
`uptr_test_common.h` defines shared BTF-visible data structures for tests of user pointers (`__uptr`) and kernel pointers (`__kptr`) in BPF map values.

## Important APIs, Types, And Functions
- Constants `MAGIC_VALUE` and `PAGE_SIZE` support validation and large-object sizing.
- Under `__BPF__`, dummy pointer globals force or suppress specific forward BTF type generation behavior.
- For non-BPF builds, `__uptr` and `__kptr` are empty macros to keep user-space compilation valid.
- Structures include `user_data`, `nested_udata`, `value_type`, `value_lock_type`, `large_data`, `large_uptr`, `empty_data`, `empty_uptr`, and `kstruct_uptr`.

## Control Flow
The header defines types only. BPF programs use these types in maps and helper calls; user space allocates or inspects compatible data.

## State And Persistence
No storage persists except dummy BPF globals under `__BPF__` and map values in consuming tests.

## Dependencies And Integration Points
It integrates BPF-side C compilation, BTF type emission, map value layout, spin locks, cgroup kptr/uptr tests, and user-space validation code elsewhere.

## Risks And Edge Cases
The empty `struct empty_data` and one-page `large_data` are intentional edge cases for verifier/BTF handling. Layout and annotations are the core test ABI; changing them invalidates expected verifier behavior.

## Test Signals
Consumers should observe correct verifier acceptance/rejection and expected data reads/writes through uptr/kptr fields, including nested, locked, large, empty, and kernel-struct pointer cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/uptr_test_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/urandom_read.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/urandom_read.c

## Purpose
`urandom_read.c` is a USDT target executable. It reads `/dev/urandom`, fires semaphore and non-semaphore USDT probes from the main executable and shared libraries, and calls versioned library APIs for symbol-versioning attach tests.

## Important APIs, Types, And Functions
- `urandom_read()` reads `BUF_SIZE` chunks, calls `urand_read_without_sema()`, fires `STAP_PROBE3(urand, read_with_sema, ...)`, then calls shared-library probe functions.
- `urand_read_with_sema_semaphore` is placed in `.probes` for semaphore-backed USDT.
- `COMPAT_VERSION(urandlib_api_old, urandlib_api, LIBURANDOM_READ_1.0.0)` declares access to an older symbol version.
- `handle_sigpipe()` marks `parent_ready` when a supervising parent closes stdout.
- `main()` optionally reports its PID until parent synchronization, then runs probe loops and versioned API calls.

## Control Flow
The program opens `/dev/urandom`, parses optional count and parent-sync mode, repeatedly prints its PID until SIGPIPE indicates the parent is ready, performs `count` random reads and USDT triggers, calls library APIs, closes the fd, and exits.

## State And Persistence
State is process-local: `/dev/urandom` fd, `parent_ready`, and USDT semaphore variable. USDT metadata and semaphores live in ELF sections for tracing tools; no disk state is modified.

## Dependencies And Integration Points
It depends on `sdt.h`, libbpf internal symbol-version macros, shared objects built from `urandom_read_lib1.c` and `urandom_read_lib2.c`, and BPF USDT/uprobe tests that attach to executable and shared-library probes.

## Risks And Edge Cases
Parent synchronization intentionally uses SIGPIPE from a closed stdout pipe, which is unusual but useful for trace attach ordering. Missing shared libraries or symbol versions break link/runtime behavior. `/dev/urandom` open failure exits early.

## Test Signals
BPF-side tests expect probe hit counts equal to read iterations for executable and library USDTs, correct semaphore handling, and successful attachment to default/compat/same-offset versioned symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/urandom_read.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/urandom_read_aux.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/urandom_read_aux.c

## Purpose
`urandom_read_aux.c` provides the executable-local semaphore-less USDT function used by `urandom_read.c`.

## Important APIs, Types, And Functions
- `urand_read_without_sema()` fires `STAP_PROBE3(urand, read_without_sema, iter_num, iter_cnt, read_sz)`.

## Control Flow
The function has a single probe invocation and returns to the caller.

## State And Persistence
No state is stored. USDT metadata is emitted into the object at build time.

## Dependencies And Integration Points
It depends on `sdt.h` and is linked into the `urandom_read` executable so USDT tests can attach to `urand:read_without_sema`.

## Risks And Edge Cases
Probe argument order and group/name strings are ABI for tests; changing them breaks attach expectations.

## Test Signals
Each call from `urandom_read()` should produce one semaphore-less executable USDT hit with three integer arguments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/urandom_read_aux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/urandom_read_lib1.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/urandom_read_lib1.c

## Purpose
`urandom_read_lib1.c` implements the semaphore-backed shared-library USDT probe and versioned library API symbols used by USDT/uprobe attachment tests.

## Important APIs, Types, And Functions
- `urandlib_read_with_sema_semaphore` is exported in `.probes`.
- `urandlib_read_with_sema()` fires `STAP_PROBE3(urandlib, read_with_sema, ...)`.
- `urandlib_api_v1()` is a compat version for `urandlib_api` at `LIBURANDOM_READ_1.0.0`.
- `urandlib_api_v2()` is the default version for `urandlib_api` at `LIBURANDOM_READ_2.0.0`.
- `urandlib_api_sameoffset()` is declared as both compat and default symbol version for same-offset symbol-version tests.

## Control Flow
The probe function fires a USDT and returns. Versioned APIs return constants `1`, `2`, and `3` to distinguish attach targets and symbol versions.

## State And Persistence
The semaphore variable is ELF section state in the shared object. No mutable runtime state is otherwise kept.

## Dependencies And Integration Points
It depends on `sdt.h` and libbpf internal version macros. It is linked as a shared library for `urandom_read.c`.

## Risks And Edge Cases
Symbol version directives are linker-sensitive; build scripts must preserve versioned aliases. The same-offset version case intentionally stresses resolver behavior.

## Test Signals
USDT tests expect library `urandlib:read_with_sema` hits and successful attachment to old/default/same-offset symbol versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/urandom_read_lib1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/urandom_read_lib2.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/urandom_read_lib2.c

## Purpose
`urandom_read_lib2.c` implements the semaphore-less shared-library USDT probe for `urandom_read` USDT tests.

## Important APIs, Types, And Functions
- `urandlib_read_without_sema()` fires `STAP_PROBE3(urandlib, read_without_sema, iter_num, iter_cnt, read_sz)`.

## Control Flow
The function simply emits the USDT probe with three arguments and returns.

## State And Persistence
No runtime state is stored; USDT note metadata is emitted into the shared object.

## Dependencies And Integration Points
It depends on `sdt.h` and is linked into the shared-library side of `urandom_read`.

## Risks And Edge Cases
Group/name and argument ordering are the test ABI. If built into the wrong object, tests expecting shared-library USDTs will not attach.

## Test Signals
Each `urandom_read()` iteration should produce one `urandlib:read_without_sema` hit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/urandom_read_lib2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/usdt.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/usdt.h

## Purpose
`usdt.h` is a single-header USDT macro library for defining user statically-defined tracepoints with no semaphore, implicit semaphore, or explicit user-defined semaphore. It emits NOP probe sites, `.note.stapsdt` metadata, optional `.probes` semaphore storage, and architecture-aware argument descriptors.

## Important APIs, Types, And Functions
- Public macros include `USDT(group, name, ...)`, `USDT_WITH_SEMA(group, name, ...)`, `USDT_IS_ACTIVE(group, name)`, `USDT_DEFINE_SEMA(sema)`, `USDT_DECLARE_SEMA(sema)`, `USDT_SEMA_IS_ACTIVE(sema)`, `USDT_WITH_EXPLICIT_SEMA(sema, group, name, ...)`, and `USDT_SEMA(sema)`.
- `struct usdt_sema { volatile unsigned short active; }` is the semaphore storage type.
- Implementation macros create semaphore names, count variadic arguments up to 12, stringify assembly, choose address directive size, emit `.note.stapsdt`, and build operand metadata.
- Architecture macros customize `USDT_NOP`, `USDT_ARG_CONSTRAINT`, and operand references for PPC, ARM, LoongArch, x86, s390, and others.

## Control Flow
Public probe macros expand to a `do { ... } while (0)` block that optionally defines or references semaphore storage, then emits inline assembly containing a probe-site NOP, STAPSDT note fields for provider/name/location/base/semaphore, argument descriptors, and `.stapsdt.base`. `USDT_IS_ACTIVE()` and `USDT_SEMA_IS_ACTIVE()` read semaphore activity counters so callers can avoid expensive argument preparation.

## State And Persistence
Implicit and explicit semaphores are ELF/global variables in `.probes`; note metadata persists in the binary for tracing tools. Runtime mutable state is limited to semaphore counters updated by tracing infrastructure.

## Dependencies And Integration Points
It is a local alternative to system `sdt.h` and integrates with BPF/libbpf USDT tests, ELF note parsers, uprobes, and application test binaries such as `usdt_1.c`, `usdt_2.c`, and `urandom_read*`.

## Risks And Edge Cases
Inline assembly and operand metadata are architecture/compiler-sensitive. The header supports up to 12 arguments; more will fail macro expansion. Semaphore sharing across shared libraries is explicitly constrained because STAPSDT note relocations are limited. C++ signedness detection uses templates while C uses compiler builtins, so behavior must be maintained in both languages.

## Test Signals
Passing tests can discover probes by provider/name, attach with or without semaphores, observe active semaphore counters, decode argument descriptors correctly, and patch NOP sites for optimized attach cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/usdt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/usdt_1.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/usdt_1.c

## Purpose
`usdt_1.c` defines an x86_64-only optimized-attach USDT target that uses a single-byte NOP at an aligned function.

## Important APIs, Types, And Functions
- `USDT_NOP` is overridden as `.byte 0x90` before including `usdt.h`.
- `usdt_1()` is 16-byte aligned and fires `USDT(optimized_attach, usdt_1)`.

## Control Flow
Calling `usdt_1()` executes the single-byte NOP probe site and returns.

## State And Persistence
USDT metadata is embedded in ELF notes; no runtime data is kept.

## Dependencies And Integration Points
It depends on x86_64 assembly encoding and `usdt.h`. Optimized attach tests compare this one-byte NOP case with the default multi-byte NOP case in `usdt_2.c`.

## Risks And Edge Cases
The source compiles to no probe on non-x86_64 due to the preprocessor guard. Alignment and exact NOP size are the purpose of the test and should not be changed casually.

## Test Signals
Attach tests should discover provider `optimized_attach`, probe `usdt_1`, and patch/trigger the single-byte NOP site correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/usdt_1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/usdt_2.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/usdt_2.c

## Purpose
`usdt_2.c` defines an x86_64-only optimized-attach USDT target using the default NOP sequence from `usdt.h`.

## Important APIs, Types, And Functions
- `usdt_2()` is 16-byte aligned and fires `USDT(optimized_attach, usdt_2)`.
- Unlike `usdt_1.c`, it does not override `USDT_NOP`, so x86_64 uses the default combined NOP sequence.

## Control Flow
Calling `usdt_2()` executes the default probe-site NOP sequence and returns.

## State And Persistence
USDT note metadata is embedded in the object; no mutable runtime state exists.

## Dependencies And Integration Points
It depends on `usdt.h` and x86_64 compilation. It pairs with `usdt_1.c` to test optimized attach handling for different NOP encodings.

## Risks And Edge Cases
No probe is emitted on non-x86_64. The default NOP sequence length is central to the test and affects attach patching expectations.

## Test Signals
Attach tests should discover provider `optimized_attach`, probe `usdt_2`, and correctly patch/trigger the default NOP sequence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/usdt_2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/atomic_and.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/atomic_and.c

## Purpose
This verifier test fragment defines test cases for `BPF_ATOMIC_AND` semantics with and without `BPF_FETCH`, including 64-bit, 32-bit, and `r0` source-register cases.

## Important APIs, Types, And Functions
- Each fragment entry is a `struct bpf_test` initializer consumed by `test_verifier.c`.
- Instructions use `BPF_ST_MEM`, `BPF_MOV64_IMM`, `BPF_MOV32_IMM`, `BPF_ATOMIC_OP(BPF_DW/W, BPF_AND | optional BPF_FETCH, ...)`, loads, jumps, and exits.
- Expected `.result = ACCEPT` verifies the verifier allows these atomic operations.

## Control Flow
The programs store initial stack values, perform atomic AND, check returned old values when `BPF_FETCH` is set, check memory now contains the AND result, and exit with nonzero codes on semantic mismatch. The non-fetch case also verifies the source register is not clobbered. The fetch cases verify old-value return and `r0` preservation/source-register behavior.

## State And Persistence
State is confined to BPF stack slots and registers during `BPF_PROG_TEST_RUN`. No maps or external fixtures are used.

## Dependencies And Integration Points
The file is included into generated verifier tests via `<verifier/tests.h>` and executed by `test_verifier.c`.

## Risks And Edge Cases
Atomic register clobber semantics are JIT-sensitive, especially the explicit `r0` checks. The 32-bit case relies on correct zero/sign behavior around a starting `-1` in `r0`.

## Test Signals
Verifier load must accept each case, and runtime return value must be zero. Nonzero exits indicate incorrect atomic result, incorrect fetched old value, or unintended register clobbering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/atomic_and.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/atomic_bounds.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/atomic_bounds.c

## Purpose
This verifier fragment tests bounds propagation through `BPF_ATOMIC_ADD | BPF_FETCH` from memory to register, ensuring the verifier can prove an apparent infinite loop is unreachable after fetching a known zero.

## Important APIs, Types, And Functions
- The single `struct bpf_test` initializer is named `BPF_ATOMIC bounds propagation, mem->reg`.
- Instructions initialize a stack slot to zero using register store, perform atomic fetch-add of one, branch backward if fetched value is nonzero, and exit.
- Expected privileged result is `ACCEPT`; expected unprivileged result is `REJECT` with log substring `back-edge`.

## Control Flow
At runtime, the fetched old value should be zero, so the `if (b) while(true)` back edge is unreachable. The privileged verifier should propagate bounds precisely enough to accept the program; the unprivileged path rejects due to back-edge policy.

## State And Persistence
State is limited to BPF registers and one stack slot. No maps or external resources are used.

## Dependencies And Integration Points
The fragment is included by verifier generated tests and executed by `test_verifier.c` in privileged and unprivileged modes.

## Risks And Edge Cases
The comment notes that immediate stack stores do not set stack slot type as needed, so changing initialization to a single `BPF_ST_MEM` can invalidate the test. Verifier precision around atomics and loop reachability is the core behavior under test.

## Test Signals
Privileged load should accept and runtime exit zero. Unprivileged load should reject with `back-edge`; a different message or acceptance indicates verifier policy/analysis drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/atomic_bounds.c -->

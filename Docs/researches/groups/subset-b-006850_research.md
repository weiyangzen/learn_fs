# subset-b-006850 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/net_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/net_test.c

## Purpose

`net_test.c` is the Landlock network selftest matrix for TCP bind/connect rules, protocol filtering, port semantics, layered rulesets, combined filesystem/network rules, and audit output. It verifies that only TCP over IPv4/IPv6 is governed by `LANDLOCK_ACCESS_NET_BIND_TCP` and `LANDLOCK_ACCESS_NET_CONNECT_TCP`, while UDP, MPTCP variants, AF_UNIX sockets, and invalid address-family combinations keep kernel-native behavior.

## Important APIs, Types, and Functions

The file uses kselftest fixtures, `struct service_fixture` and `struct protocol_variant` from `common.h`, Landlock syscalls through `landlock_create_ruleset()`, `landlock_add_rule()`, and `enforce_ruleset()`, and socket APIs including `socket()`, `bind()`, `listen()`, `connect()`, `accept()`, `getsockname()`, and AF_UNSPEC disconnects. Helpers such as `set_service()`, `socket_variant()`, `get_addrlen()`, `bind_variant_addrlen()`, `connect_variant_addrlen()`, and `test_bind_and_connect()` normalize protocol-specific setup.

## Control Flow and State

Fixture variants cover no-sandbox and TCP-sandbox modes across IPv4, IPv6, TCP, MPTCP, UDP, and UNIX sockets. Each test creates a private network namespace, raises loopback, builds one or more ruleset layers, forks clients when needed, and compares expected success, `EACCES`, `EINVAL`, `EAFNOSUPPORT`, `ECONNREFUSED`, or `EISCONN`. State is mainly per-process Landlock domain state, per-socket bound/connected state, selected port numbers, audit records, and temporary capabilities used for namespace setup or low-port binding.

## Dependencies and Integration Points

It depends on Landlock ABI network rights, Linux socket semantics, kselftest harness macros, audit helpers, loopback setup via `ip link`, and capability helpers. It integrates with `common.h`, `audit.h`, and the Landlock selftest Makefile.

## Risks and Test Signals

Regression risks include host-vs-network byte-order confusion, incorrect AF_UNSPEC handling, accidental restriction of UDP/MPTCP/UNIX paths, layer union/intersection mistakes, mishandling of port 0 or `UINT16_MAX`, and audit format drift. Strong signals are exact errno assertions, successful client/server byte transfer, audit records matching `net.bind_tcp` or `net.connect_tcp`, and absence of unexpected access records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/net_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/ptrace_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/ptrace_test.c

## Purpose

`ptrace_test.c` verifies Landlock's ptrace containment model between parent and child processes with no domain, inherited domains, nested domains, parent-only domains, child-only domains, and sibling domains. It also validates audit records emitted when Landlock blocks ptrace-related access.

## Important APIs, Types, and Functions

The test creates a minimal filesystem-handling Landlock domain with `landlock_create_ruleset()` and `landlock_restrict_self()`. It probes read-style ptrace checks by opening `/proc/<pid>/environ`, probes active tracing with `ptrace(PTRACE_ATTACH)`, `PTRACE_DETACH`, and `PTRACE_TRACEME`, and reads Yama policy from `/proc/sys/kernel/yama/ptrace_scope`. It reuses `scoped_base_variants.h` for the domain topology matrix and `audit.h` for log matching.

## Control Flow and State

Parent and child synchronize through close-on-exec pipes so each side enters its intended Landlock domain before testing. Expected access booleans combine Landlock ancestry with Yama: parents can read or trace children only when not isolated from them, and children can trace parents only when not isolated and Yama permits it. The audit fixture forces a blocking domain and checks denied `PTRACE_TRACEME` and `PTRACE_ATTACH` records.

## Dependencies and Integration Points

The file depends on kselftest, Landlock's domain ancestry checks, Linux ptrace permission hooks, procfs, optional Yama policy, capabilities being dropped, and audit filtering by executable.

## Risks and Test Signals

The biggest risk is confusing Landlock denial with Yama denial; the test logs incomplete coverage when Yama is restrictive. Other risks are pipe races around stopped traced tasks and audit regex drift. Success signals are exact `EACCES` for `/proc` reads, `EPERM` for denied ptrace operations, correct wait/stop/detach transitions, and expected `blockers=ptrace opid=...` audit records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/ptrace_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/sandbox-and-launch.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/sandbox-and-launch.c

## Purpose

`sandbox-and-launch.c` is a helper executable used by mount/layout Landlock tests. It sandboxes itself with `LANDLOCK_SCOPE_SIGNAL`, reports readiness through a pipe, waits for the parent test to exercise mount behavior, and then `execve()`s another supplied program with the pipe arguments shifted forward.

## Important APIs, Types, and Functions

It uses `struct landlock_ruleset_attr.scoped`, `landlock_create_ruleset()`, `landlock_restrict_self()`, `prctl(PR_SET_NO_NEW_PRIVS)`, `write()`, `read()`, `close()`, `atoi()`, and `execve()`. `wrappers.h` supplies direct syscall wrappers for Landlock on systems whose libc headers do not expose them.

## Control Flow and State

The program expects exactly three logical arguments after its name: target binary and two pipe file descriptors. It creates the scoped domain, closes the ruleset FD, writes one byte to the child pipe, blocks on the parent pipe, mutates `argv` in place, and replaces itself with the target executable. Persistent state is only the process's Landlock domain and inherited open pipe descriptors.

## Dependencies and Integration Points

It integrates with Landlock filesystem tests that need a process to cross an exec boundary after entering a signal-scoped sandbox. It depends on valid inherited file descriptors and on the parent having already set up the expected synchronization protocol.

## Risks and Test Signals

Risks are argument-order mistakes, leaked ruleset FDs, lost synchronization bytes, and accidental environment inheritance expectations because `execve()` passes `NULL` environment. Useful signals are error messages on failed Landlock setup, pipe read/write failures, and the downstream target executing only after the parent's synchronization byte.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/sandbox-and-launch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/scoped_abstract_unix_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/scoped_abstract_unix_test.c

## Purpose

`scoped_abstract_unix_test.c` validates `LANDLOCK_SCOPE_ABSTRACT_UNIX_SOCKET`. It tests abstract UNIX stream and datagram communication across parent, child, and grandchild domains, contrasts scoped domains with unrelated filesystem-only domains, verifies audit logging, and proves pathname and unnamed UNIX sockets are not incorrectly governed by abstract-socket scoping.

## Important APIs, Types, and Functions

The file uses `create_scoped_domain()` from `scoped_common.h`, `create_fs_domain()` for non-scope control domains, `set_unix_address()`, `send_fd()`/`recv_fd()`, AF_UNIX `socket()`, `bind()`, `listen()`, `connect()`, `accept()`, `send()`, `sendto()`, `socketpair()`, pipes, fork/wait, and audit helpers. It includes both `scoped_base_variants.h` and `scoped_multiple_domain_variants.h`.

## Control Flow and State

Tests build deterministic abstract addresses, create server sockets in parent or child domains, synchronize process ordering with pipes, and assert whether domain ancestry allows connection or datagram sends. Additional fixtures test sockets created in one domain and used in another via FD passing, pathname sockets under `TMP_DIR`, connected datagram sockets after later scoping, and inherited self-bound datagram sockets. State includes socket creator domain, process domain, connected datagram peer state, abstract socket names, and audit counters.

## Dependencies and Integration Points

It depends on Landlock's scoped-domain checks in UNIX socket connect/send paths, kselftest helpers, audit filtering, temporary directory cleanup, and common Landlock socket fixture helpers.

## Risks and Test Signals

Risks include confusing process domain with socket creation domain, over-blocking pathname or unnamed sockets, allowing unconnected datagram sends out of scope, and audit path encoding drift for abstract socket names. Success signals include `EPERM` only for out-of-scope abstract operations, data bytes arriving on allowed streams/datagrams, correct FD-passing behavior, and audit regex matches for `scope.abstract_unix_socket`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/scoped_abstract_unix_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/scoped_base_variants.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/scoped_base_variants.h

## Purpose

`scoped_base_variants.h` is a shared fixture-variant header for two-process Landlock scope tests. It defines all parent/child domain topologies needed to reason about whether access from P1 to P2 or P2 to P1 should be allowed.

## Important APIs, Types, and Functions

The header defines `FIXTURE_VARIANT(scoped_domains)` with `domain_both`, `domain_parent`, and `domain_child` booleans, plus eight `FIXTURE_VARIANT_ADD()` cases: `without_domain`, `child_domain`, `parent_domain`, `sibling_domain`, `inherited_domain`, `nested_domain`, `nested_and_parent_domain`, and `forked_domains`.

## Control Flow and State

It contains no executable runtime logic, but the booleans drive test control flow in ptrace, signal, and abstract UNIX socket tests. `domain_both` means a ruleset is applied before fork and inherited, while `domain_parent` or `domain_child` adds extra domains after fork in the corresponding process.

## Dependencies and Integration Points

It must be included after a fixture named `scoped_domains` is declared. It depends on kselftest harness macros and is source-included by several Landlock scope tests.

## Risks and Test Signals

The key risk is semantic drift between the diagrams and the booleans, which would invert expected allow/deny decisions across multiple tests. Test signals are the downstream fixture matrix expanding to all eight domain ancestry cases and producing consistent access results for ptrace, signals, and abstract sockets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/scoped_base_variants.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/scoped_common.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/scoped_common.h

## Purpose

`scoped_common.h` provides the common helper for creating a Landlock scoped domain in scope-specific selftests. It avoids duplicating the ruleset creation and enforcement sequence for signal and abstract UNIX socket scopes.

## Important APIs, Types, and Functions

The single helper `create_scoped_domain(struct __test_metadata *, __u16 scope)` initializes `struct landlock_ruleset_attr` with `.scoped = scope`, calls `landlock_create_ruleset()`, enforces it through `enforce_ruleset()`, and closes the ruleset FD with kselftest assertions.

## Control Flow and State

The helper has straight-line control flow: create ruleset, fail the current kselftest on error, restrict the calling thread/process, and close. The persistent effect is the new Landlock domain layer attached to the caller; no file state is written.

## Dependencies and Integration Points

It depends on `common.h` for `enforce_ruleset()` and kselftest metadata, `<linux/landlock.h>` via including tests, and Landlock kernels that support `.scoped`.

## Risks and Test Signals

Risks are failing to close ruleset FDs, using the wrong scope bit, or calling it in a process after synchronization expectations have changed. Signals are downstream tests seeing `EPERM` only after this helper is called and `_metadata` capturing setup failures cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/scoped_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/scoped_multiple_domain_variants.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/scoped_multiple_domain_variants.h

## Purpose

`scoped_multiple_domain_variants.h` defines the three-process domain matrices used to test scoped access across parent, child, and grandchild processes. It distinguishes actual scope sandboxes from unrelated Landlock domains so tests can prove only scoped domains affect scoped resources.

## Important APIs, Types, and Functions

The header defines `enum sandbox_type` with `NO_SANDBOX`, `SCOPE_SANDBOX`, and `OTHER_SANDBOX`, then defines `FIXTURE_VARIANT(scoped_vs_unscoped)` with `domain_all`, `domain_parent`, `domain_children`, `domain_child`, and `domain_grand_child`. Seven variants encode allow/deny diagrams such as `deny_scoped`, `all_scoped`, `allow_with_other_domain`, and `deny_with_self_and_grandparent_domain`.

## Control Flow and State

There is no standalone execution. Consuming tests use each field to decide whether to create a scope ruleset, a filesystem-only domain, or no domain before/after forks. The resulting ancestry state determines whether a grandchild may reach child or parent sockets.

## Dependencies and Integration Points

It must be included by a test that declares `FIXTURE(scoped_vs_unscoped)` and supplies functions for scope and other-domain creation.

## Risks and Test Signals

Risks include conflating `OTHER_SANDBOX` with scope enforcement or misplacing domain creation before the wrong fork. Downstream test signals are matching P3-to-P2 and P3-to-P1 allow/deny outcomes for abstract UNIX socket operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/scoped_multiple_domain_variants.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/scoped_signal_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/scoped_signal_test.c

## Purpose

`scoped_signal_test.c` validates `LANDLOCK_SCOPE_SIGNAL` for normal signals, permission probes with signal 0, process-thread interactions, credential updates through `setuid()`, and `SIGURG` delivery through `F_SETOWN` on sockets.

## Important APIs, Types, and Functions

It uses `create_scoped_domain()`, kselftest fixtures, `sigaction()`, `kill()`, `raise()`, `pthread_create()`, `pthread_kill()`, `pthread_join()`, `setuid()`, UNIX stream sockets, `fcntl(F_SETOWN)`, `send(MSG_OOB)`, and pipe/fork synchronization. It reuses `scoped_base_variants.h` and common UNIX address helpers.

## Control Flow and State

Tests first prove a child can signal a parent before scoping and cannot afterward, then run the full parent/child domain topology matrix for `kill(pid, 0)`. Thread tests show same-process threads remain signalable regardless of whether scoping is applied before or after thread creation, and that libc `setuid()` still propagates credentials across threads. The `fown` fixture changes whether scoping happens before fork, before `F_SETOWN`, or after it, then checks whether OOB socket delivery can signal the child.

## Dependencies and Integration Points

It depends on Landlock signal scope enforcement, POSIX signal behavior, pthreads, capability handling for `setuid`, and UNIX socket ownership semantics.

## Risks and Test Signals

Risks include races around asynchronous signal delivery, treating same-thread-group signals as out-of-scope, breaking credential synchronization, and mishandling `F_SETOWN` when ownership predates scoping. Signals are `EPERM` on denied `kill`, unchanged `is_signaled` in parents, successful `pthread_kill`, successful thread credential checks, and variant-specific `SIGURG` receipt.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/scoped_signal_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/scoped_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/scoped_test.c

## Purpose

`scoped_test.c` is a minimal validation test for the `.scoped` field of `struct landlock_ruleset_attr`. It checks that unknown high-order scope bits are rejected rather than silently accepted.

## Important APIs, Types, and Functions

The test uses `landlock_create_ruleset()` directly with `.scoped = scoped_mask`, kselftest `TEST()`/`ASSERT_EQ`, and `LANDLOCK_SCOPE_SIGNAL` as the highest known scope bit boundary.

## Control Flow and State

The loop starts at bit 63 and shifts down until it reaches `LANDLOCK_SCOPE_SIGNAL`, expecting every unknown bit to make `landlock_create_ruleset()` fail with `EINVAL`. It creates no persistent Landlock domain because all calls are expected to fail.

## Dependencies and Integration Points

It depends on the local Landlock UAPI header defining known scope bits and on the kernel rejecting unknown scope masks.

## Risks and Test Signals

The main risk is ABI laxness: accepting unknown bits would make future scope semantics ambiguous. The signal is strict `-1` plus `errno == EINVAL` for every unknown mask.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/scoped_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/true.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/true.c

## Purpose

`true.c` is a tiny helper binary for Landlock tests that need an executable which succeeds without side effects.

## Important APIs, Types, and Functions

It defines only `int main(void)` and returns `0`. There are no external APIs, no Landlock calls, and no filesystem or process manipulation.

## Control Flow and State

The control flow is a single return statement. It creates no state and persists nothing.

## Dependencies and Integration Points

It integrates with tests that exec a known-success program, often to check behavior around exec transitions, mount layouts, or sandbox helper orchestration.

## Risks and Test Signals

The only meaningful risk is build or path failure. A successful invocation exits with status 0 and produces no output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/true.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/tsync_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/tsync_test.c

## Purpose

`tsync_test.c` tests `LANDLOCK_RESTRICT_SELF_TSYNC`, which applies Landlock restrictions consistently across all threads in a process. It covers single-thread success, multi-thread synchronization, diverged thread domains, concurrent enablement, interruption/restart paths, and special no-ruleset flag combinations.

## Important APIs, Types, and Functions

The file creates a filesystem ruleset with `LANDLOCK_ACCESS_FS_WRITE_FILE | LANDLOCK_ACCESS_FS_TRUNCATE`, then uses `prctl(PR_SET_NO_NEW_PRIVS)`, `landlock_restrict_self(..., LANDLOCK_RESTRICT_SELF_TSYNC)`, pthread creation/cancel/join, cleanup handlers, `pthread_kill()`, `sigaction()`, and flag variants including logging flags.

## Control Flow and State

Idle threads sleep until canceled, storing their `no_new_privs` state through cleanup handlers. Tests enforce rulesets with TSYNC while sibling threads are live, intentionally diverge the main thread domain and resynchronize, and run two threads racing the same TSYNC call. The interruption test starts 200 idle threads plus a tight signaler thread to hit kernel cancellation/restart paths; userspace should still see success.

## Dependencies and Integration Points

It depends on Landlock TSYNC kernel support, pthreads, signal restart behavior, and kselftest metadata. It also exercises interactions with logging-related `landlock_restrict_self()` flags when `ruleset_fd == -1`.

## Risks and Test Signals

Risks include partial thread updates, missing implicit `no_new_privs`, deadlocks under signal interruption, or wrong errno for flag-only calls. Signals are all threads joining cleanly, cleanup handlers observing `no_new_privs`, both competing calls returning 0, interrupted TSYNC still succeeding, and expected `EBADF` or success for no-ruleset variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/tsync_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/wait-pipe-sandbox.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/wait-pipe-sandbox.c

## Purpose

`wait-pipe-sandbox.c` is a synchronized helper for Landlock audit-exec tests. It waits with a parent, verifies inherited signal scoping, adds additional filesystem and signal-scoped Landlock layers, and verifies each layer blocks the expected operation.

## Important APIs, Types, and Functions

It uses `sync_with()` for one-byte pipe handshakes, `landlock_create_ruleset()`, `landlock_restrict_self()`, `kill(getppid(), 0)`, `open("/")`, `close()`, and `atoi()`. `wrappers.h` supplies direct Landlock syscalls.

## Control Flow and State

The program expects child and parent pipe FDs. It first synchronizes and checks a parent-provided layer blocks signaling the parent, then synchronizes again, adds a filesystem `READ_DIR` handling layer that denies opening `/`, synchronizes a third time, adds `LANDLOCK_SCOPE_SIGNAL`, and checks both filesystem and signal denials. The persistent state is the process's accumulated Landlock layers.

## Dependencies and Integration Points

It depends on the parent test having already set `PR_SET_NO_NEW_PRIVS`, inherited pipe descriptors, Landlock filesystem and signal-scope support, and audit tests that observe behavior across exec.

## Risks and Test Signals

Risks are desynchronization, wrong inherited no-new-privs assumptions, or adding layers in the wrong order. Signals are nonzero exit on any unexpected successful `kill()` or `open("/")`, plus stderr messages identifying the violated restriction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/wait-pipe-sandbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/wait-pipe.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/wait-pipe.c

## Purpose

`wait-pipe.c` is a simple synchronization helper for Landlock tests that need a child process to announce readiness and then block until the parent completes its assertion.

## Important APIs, Types, and Functions

It uses `atoi()` to parse two pipe FDs, `write()` to send a one-byte ready marker, and `read()` to wait for the parent. It reports errors with `fprintf()` and `perror()`.

## Control Flow and State

The program requires exactly two arguments after its name. It writes `"."` to the child pipe, reads one byte from the parent pipe, then exits 0. It does not create Landlock domains or persistent files.

## Dependencies and Integration Points

It integrates with Landlock filesystem layout tests, especially cases that need a stable child process while the parent manipulates mounts or checks sandbox behavior.

## Risks and Test Signals

Risks are invalid FD arguments or broken pipes. Success is silent exit 0 after both synchronization events; failure exits 1 with a diagnostic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/wait-pipe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/wrappers.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/wrappers.h

## Purpose

`wrappers.h` provides direct syscall wrappers for Landlock operations and `gettid`, letting selftests build and run even when libc lacks Landlock wrapper functions.

## Important APIs, Types, and Functions

It conditionally defines inline `landlock_create_ruleset()`, `landlock_add_rule()`, and `landlock_restrict_self()` around `syscall(__NR_landlock_*)`. It also defines `sys_gettid()` as `syscall(__NR_gettid)`.

## Control Flow and State

Each wrapper is a straight pass-through to the kernel syscall with the supplied arguments. It stores no state and performs no errno translation beyond the normal syscall behavior.

## Dependencies and Integration Points

It depends on `<linux/landlock.h>`, syscall numbers, and unistd/syscall headers. It is included by standalone helper programs and can coexist with environments that already provide Landlock symbols because each wrapper is guarded by `#ifndef`.

## Risks and Test Signals

Risks include mismatched syscall numbers on unsupported architectures or accidental signature drift from UAPI. Test signals are successful compilation without libc prototypes and expected syscall return/errno behavior in all helper programs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/wrappers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/lib.mk -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/lib.mk

## Purpose

`lib.mk` is the common build, run, install, clean, and header-generation include for kernel selftests. It lets individual selftest directories declare programs, scripts, generated files, modules, headers, flags, and install assets while sharing consistent kselftest behavior.

## Important APIs, Types, and Functions

The Makefile variables include `TEST_GEN_PROGS`, `TEST_GEN_PROGS_EXTENDED`, `TEST_GEN_FILES`, `TEST_PROGS`, `TEST_CUSTOM_PROGS`, `TEST_FILES`, `TEST_INCLUDES`, `TEST_GEN_MODS_DIR`, `OUTPUT`, `INSTALL_PATH`, `KHDR_INCLUDES`, `TOOLS_INCLUDES`, `USERCFLAGS`, and `USERLDFLAGS`. It defines `RUN_TESTS`, install macros, build pattern rules for C and assembly, `gen_mods_dir`, `clean_mods_dir`, `emit_tests`, and `headers`.

## Control Flow and State

It selects clang or gcc based on `LLVM`/`CROSS_COMPILE`, derives target triples, initializes `OUTPUT` for standalone builds, rewrites generated test targets into output paths, builds generated programs/files, optionally builds module directories, runs tests through `kselftest/runner.sh`, installs artifacts with `rsync`, and cleans generated outputs. Persistent state is limited to build products under `OUTPUT` and installed files under `INSTALL_PATH`.

## Dependencies and Integration Points

It depends on GNU make, compiler toolchains, kselftest harness headers, optional kernel headers, `runner.sh`, `rsync`, and module sub-Makefiles.

## Risks and Test Signals

Risks include wrong output-path rewriting, cross-compile target mismatch, missing kernel headers, incomplete install lists, and module directories silently skipped when `KDIR` is absent. Signals are successful `make`, correct `run_tests` behavior in in-tree and out-of-tree builds, populated install trees, and `emit_tests` listing runnable tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/lib.mk -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/lib/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/lib/Makefile

## Purpose

`lib/Makefile` wires the selftests `lib` collection into the shared kselftest build system. It deliberately avoids building binaries for the default `all` target while registering the bitmap module shell test.

## Important APIs, Types, and Functions

It defines an empty `all:` target, sets `TEST_PROGS := bitmap.sh`, and includes `../lib.mk`.

## Control Flow and State

Running `make` without a target hits the empty `all` target, preventing automatic test execution. `run_tests` and install behavior come from `lib.mk` and include `bitmap.sh` as the runnable program.

## Dependencies and Integration Points

It depends on the sibling `bitmap.sh` script and the common `lib.mk` include. It integrates the bitmap kernel module test into kselftest enumeration.

## Risks and Test Signals

The main risk is accidentally removing the empty `all` target and changing no-argument behavior. Signals are `make` doing no build work and kselftest still discovering `bitmap.sh`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/lib/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/lib/bitmap.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/lib/bitmap.sh

## Purpose

`bitmap.sh` is the kselftest wrapper for the kernel bitmap library test module.

## Important APIs, Types, and Functions

It invokes `../kselftest/module.sh "bitmap" test_bitmap`, delegating module loading, result interpretation, and skip/fail handling to the shared module test helper.

## Control Flow and State

The script has no branching of its own. It executes `module.sh` with the human-readable test name and module name. Runtime state is whatever `module.sh` creates while loading and unloading `test_bitmap`.

## Dependencies and Integration Points

It depends on `test_bitmap` being buildable/loadable as a kernel module and on `module.sh` existing in the selftests tree.

## Risks and Test Signals

Risks are missing module support or stale module names. Signals come from `module.sh`: pass when the module test completes successfully, skip when prerequisites are absent, and fail on module test errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/lib/bitmap.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/lib/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/lib/config

## Purpose

`lib/config` declares kernel configuration dependencies for the selftests under `tools/testing/selftests/lib`.

## Important APIs, Types, and Functions

It lists `CONFIG_TEST_BITMAP=m`, `CONFIG_PRIME_NUMBERS=m`, and `CONFIG_TEST_BITOPS=m`. These are Kconfig symbols rather than executable code.

## Control Flow and State

There is no control flow. The file is consumed by kselftest tooling to determine required kernel features or modules.

## Dependencies and Integration Points

It integrates with config-check tooling and with `bitmap.sh`, whose module depends on these symbols.

## Risks and Test Signals

Risks are missing or wrong symbols causing false skips or build/load failures. Signals are config check output and successful loading of the bitmap-related test module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/lib/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/Makefile

## Purpose

`livepatch/Makefile` registers the livepatch selftest scripts, helper binary, module build directory, settings file, and common build behavior.

## Important APIs, Types, and Functions

It sets `TEST_GEN_FILES := test_klp-call_getpid`, `TEST_GEN_MODS_DIR := test_modules`, `TEST_PROGS_EXTENDED := functions.sh`, `TEST_PROGS` for the livepatch shell tests, `TEST_FILES := settings`, and includes `../lib.mk`.

## Control Flow and State

The common `lib.mk` rules compile `test_klp-call_getpid`, build kernel modules by recursing into `test_modules`, and expose each shell script to kselftest. Generated state is the helper binary and `.ko` files.

## Dependencies and Integration Points

It depends on a configured kernel build tree for modules, the livepatch scripts, `functions.sh`, and the test modules directory.

## Risks and Test Signals

Risks include omitting a script or module directory from the build graph, breaking install of `settings`, or running scripts without compiled modules. Signals are `make` producing helper/module artifacts and kselftest enumerating all listed scripts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/config

## Purpose

`livepatch/config` declares the minimum kernel configuration expected by the livepatch selftests.

## Important APIs, Types, and Functions

It lists `CONFIG_LIVEPATCH=y` and `CONFIG_DYNAMIC_DEBUG=y`.

## Control Flow and State

The file contains declarative config requirements only. It does not execute and writes no state.

## Dependencies and Integration Points

It integrates with kselftest config checking and with the shell harness, which needs livepatch sysfs/debug output and dynamic debug controls.

## Risks and Test Signals

Risks are missing prerequisites causing confusing runtime skips or failures. Signals are config checks passing and `functions.sh` being able to manipulate dynamic debug and livepatch sysfs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/functions.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/functions.sh

## Purpose

`functions.sh` is the livepatch selftest harness library. It handles prerequisite checks, sysfs/debugfs/tracing state save and restore, module load/unload, livepatch transition waiting, dmesg canarying, exact log comparison, sysfs assertions, and ftrace setup.

## Important APIs, Types, and Functions

Key functions are `setup_config()`, `push_config()`, `pop_config()`, `set_dynamic_debug()`, `set_ftrace_enabled()`, `load_mod()`, `load_lp_nowait()`, `load_lp()`, `load_failing_mod()`, `unload_mod()`, `disable_lp()`, `set_pre_patch_ret()`, `start_test()`, `check_result()`, `check_sysfs_rights()`, `check_sysfs_value()`, `trace_function()`, and `check_traced_functions()`.

## Control Flow and State

Each script sources this file, calls `setup_config()`, and then sequences module operations. The harness writes markers to `/dev/kmsg`, waits for `/sys/module` and `/sys/kernel/livepatch` state, polls livepatch `transition`, snapshots current debug/tracing/sysctl state, and restores it on exit through a trap. `check_result()` treats filtered dmesg text as an exact test oracle.

## Dependencies and Integration Points

It depends on root, `KDIR`, livepatch sysfs, debugfs/tracing paths, kprobes control, dynamic debug, `insmod`, `rmmod`, `modinfo`, `dmesg`, `sysctl`, and standard shell tools.

## Risks and Test Signals

Risks include unbounded waits, dmesg buffer overrun, path differences between tracefs/debugfs, not restoring global kernel state, and brittle exact-output comparisons. Signals are clean skips for missing root/KDIR, completed transition polling, exact `check_result()` matches, and restored sysfs/tracing state on exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/functions.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test-callbacks.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test-callbacks.sh

## Purpose

`test-callbacks.sh` validates livepatch object callbacks for vmlinux and target modules across load order, unload order, failed pre-patch callbacks, busy transitions, multiple livepatches, and atomic replacement.

## Important APIs, Types, and Functions

It uses harness functions from `functions.sh` and modules `test_klp_callbacks_demo`, `test_klp_callbacks_demo2`, `test_klp_callbacks_mod`, and `test_klp_callbacks_busy`. It manipulates `pre_patch_ret`, `block_transition`, and `replace` module parameters.

## Control Flow and State

The script runs named scenarios with `start_test()`, then loads/unloads target modules and livepatches in precise orders. It expects callback log lines for module states `COMING`, `LIVE`, and `GOING`, intentionally stalls a transition with a busy worker, and verifies which pre/post patch or unpatch callbacks are skipped or executed.

## Dependencies and Integration Points

It depends on the callback demo modules, livepatch transition machinery, module notifier handling, dmesg filtering, and sysfs `transition`/`enabled`.

## Risks and Test Signals

Risks include callback ordering regressions, failure cleanup leaks, stalled transition reversal bugs, and atomic replace executing callbacks it should bypass. Signals are exact dmesg transcripts for each scenario and successful module reference cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test-callbacks.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test-ftrace.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test-ftrace.sh

## Purpose

`test-ftrace.sh` checks livepatch interaction with the global `kernel.ftrace_enabled` sysctl and with function tracing on original and patched functions.

## Important APIs, Types, and Functions

It uses `set_ftrace_enabled()`, `load_lp()`, `load_failing_mod()`, `trace_function()`, `check_traced_functions()`, `/proc/cmdline`, and module `test_klp_livepatch`.

## Control Flow and State

The first scenario disables ftrace, expects livepatch load failure, reenables ftrace, verifies a patch affects `/proc/cmdline`, and expects attempts to disable ftrace while patched to fail. Later scenarios trace the patched replacement function and the original target function while confirming livepatch behavior remains active.

## Dependencies and Integration Points

It depends on ftrace, tracefs/debugfs, livepatch ftrace registration, sysctl writes, and dmesg checking.

## Risks and Test Signals

Risks are allowing livepatch registration when ftrace is disabled, allowing ftrace to be disabled under active livepatches, or tracing breaking patch dispatch. Signals are expected `-EBUSY`-style load/sysctl failures, `/proc/cmdline` showing patched text, and traced functions appearing in the trace buffer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test-ftrace.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test-kprobe.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test-kprobe.sh

## Purpose

`test-kprobe.sh` validates livepatch interaction with kprobes on the same target function. It distinguishes kprobes with a post handler, which use IPMODIFY and conflict with livepatch ftrace registration, from kprobes without a post handler.

## Important APIs, Types, and Functions

The script checks `/proc/kallsyms` for `kprobe_ftrace_ops`, toggles `/sys/kernel/debug/kprobes/enabled`, loads `test_klp_kprobe` with `has_post_handler=true/false`, and loads or fails `test_klp_livepatch`.

## Control Flow and State

It first skips if the kernel lacks kprobes-on-ftrace support. With post handler enabled, livepatch load must fail with handler-registration errors. Without the post handler, the livepatch should load, then the kprobe and livepatch are removed in order.

## Dependencies and Integration Points

It depends on kprobe-on-ftrace support, kprobes debugfs, the kprobe test module, the livepatch test module, and exact dmesg matching.

## Risks and Test Signals

Risks are allowing multiple IPMODIFY users on the same function or over-rejecting non-conflicting kprobes. Signals are load failure with `Device or resource busy` in the post-handler case and successful patch/unpatch in the no-post-handler case.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test-kprobe.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test-livepatch.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test-livepatch.sh

## Purpose

`test-livepatch.sh` is the broad functional livepatch script. It validates vmlinux function patching, multiple livepatch stacking, atomic replacement, patching functions in a separately loaded module, and loading a module-targeting livepatch before its target module appears.

## Important APIs, Types, and Functions

It uses harness module helpers, `/proc/cmdline`, `/proc/meminfo`, `/proc/test_klp_mod_target`, livepatch sysfs module counts, and modules `test_klp_livepatch`, `test_klp_syscall`, `test_klp_callbacks_demo`, `test_klp_atomic_replace`, `test_klp_mod_target`, and `test_klp_mod_patch`.

## Control Flow and State

Each scenario loads livepatch modules, reads proc files to prove redirection, disables patches through sysfs, unloads modules, and compares dmesg. Atomic replacement verifies old patches disappear from livepatch sysfs while the replacement remains active. Module patching scenarios check both target-before-patch and patch-before-target ordering.

## Dependencies and Integration Points

It depends on livepatch stacking and replace semantics, procfs show functions, module notifier patching, and exact dmesg checking.

## Risks and Test Signals

Risks include stale patches remaining after disable, wrong stack behavior, atomic replace not disabling old patches, and module patching not applying at module load. Signals are proc file contents switching between original and patched strings and exact transition logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test-livepatch.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test-shadow-vars.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test-shadow-vars.sh

## Purpose

`test-shadow-vars.sh` validates the livepatch shadow variable API by loading a module that allocates, retrieves, and frees shadow variables for several simulated objects.

## Important APIs, Types, and Functions

The shell script uses `load_mod()`, `unload_mod()`, and `check_result()` with module `test_klp_shadow_vars`. The module exercises `klp_shadow_get()`, `klp_shadow_alloc()`, `klp_shadow_get_or_alloc()`, `klp_shadow_free()`, and `klp_shadow_free_all()`.

## Control Flow and State

The script delegates behavior to module init, then checks a long normalized dmesg transcript using pointer placeholders such as `PTR1`. The module creates shadow state for multiple object/id pairs, confirms lookups, frees one ID per object, verifies the other ID remains, and frees all remaining entries.

## Dependencies and Integration Points

It depends on the livepatch shadow variable API, deterministic module logging, and harness dmesg filtering.

## Risks and Test Signals

Risks are duplicate allocation, missing constructor/destructor calls, freeing wrong object/id pairs, and pointer-address nondeterminism. Signals are exact ordered log lines showing expected NULL lookups, stable pointer aliases, destructor calls for single frees, and NULL results after `free_all`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test-shadow-vars.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test-state.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test-state.sh

## Purpose

`test-state.sh` validates livepatch system-state storage and migration across cumulative livepatches. It uses console loglevel changes as the stateful side effect.

## Important APIs, Types, and Functions

It uses `load_lp()`, `load_failing_mod()`, `disable_lp()`, and modules `test_klp_state`, `test_klp_state2`, and `test_klp_state3`. The modules use `klp_state`, `klp_get_state()`, and `klp_get_prev_state()`.

## Control Flow and State

The script tests basic allocation/fix/restore/free of console loglevel state, then loads a compatible cumulative patch that takes over the existing state, unloads/reloads compatible versions, and finally attempts an incompatible version mismatch that must fail. State persists inside livepatch state records while patches are stacked.

## Dependencies and Integration Points

It depends on livepatch replace/cumulative behavior, state version compatibility, console loglevel globals, and exact callback logs.

## Risks and Test Signals

Risks include leaking state data, restoring console loglevel too early, incompatible cumulative patches loading, or compatible patches failing to take over state. Signals are exact logs for allocation, takeover, restore, free, and an `Invalid parameters` failure for incompatible versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test-state.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test-syscall.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test-syscall.sh

## Purpose

`test-syscall.sh` stresses livepatching of the `getpid` syscall while many processes are actively executing it. It checks that all selected tasks transition into the patched state.

## Important APIs, Types, and Functions

It starts multiple `test_klp-call_getpid` helpers, passes their PIDs through the `klp_pids` module parameter to `test_klp_syscall`, polls `/sys/kernel/test_klp_syscall/npids`, and uses harness livepatch load/unload functions.

## Control Flow and State

The script starts up to min(online CPUs, 128) busy helper processes, joins their PIDs into a comma-separated module parameter, loads the livepatch, waits until `npids` reaches zero, logs the remaining count, kills helpers, then disables and unloads the livepatch.

## Dependencies and Integration Points

It depends on syscall wrapper naming by architecture, livepatch transition mechanics, a custom sysfs counter exposed by the module, and process management.

## Risks and Test Signals

Risks are tasks never reaching a safe transition point, wrong syscall symbol names, sysfs counter races, or leaked helper processes. Signals are `npids` becoming 0, dmesg logging `Remaining not livepatched processes: 0`, and clean unpatching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test-syscall.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test-sysfs.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test-sysfs.sh

## Purpose

`test-sysfs.sh` validates the livepatch sysfs interface: permissions, values, object patched state, replace flag, transition state, and stack-order updates as patches are loaded and removed.

## Important APIs, Types, and Functions

It uses `check_sysfs_rights()`, `check_sysfs_value()`, `load_lp()`, `load_mod()`, `disable_lp()`, and modules `test_klp_livepatch`, `test_klp_callbacks_demo`, `test_klp_syscall`, and `test_klp_atomic_replace`.

## Control Flow and State

The script first checks base livepatch directory and file modes/values, then verifies a target module's `patched` file flips from 0 to 1 to 0 across module load/unload. It separately validates `replace=1`, `replace=0`, and stack order renumbering after removing a middle patch.

## Dependencies and Integration Points

It depends on livepatch sysfs layout under `/sys/kernel/livepatch`, module notifier state, `stat`, and exact dmesg checking.

## Risks and Test Signals

Risks include sysfs ABI permission regressions, stale object `patched` values, wrong replace reporting, and stack-order gaps after unload. Signals are exact mode strings, expected file contents, and matching dmesg transcripts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test-sysfs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_klp-call_getpid.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_klp-call_getpid.c

## Purpose

`test_klp-call_getpid.c` is a user-space load generator for the livepatch syscall test. It repeatedly invokes `SYS_getpid` until signaled.

## Important APIs, Types, and Functions

It installs `SIGHUP` and `SIGINT` handlers with `signal()`, calls `syscall(SYS_getpid)` in a loop, tracks an iteration counter, and optionally prints the count when stopped by SIGINT.

## Control Flow and State

The main loop runs while `stop` is false. `hup_handler()` sets `stop`; `int_handler()` sets both `stop` and `sig_int`. State is limited to process-local static flags and the iteration counter.

## Dependencies and Integration Points

It integrates with `test-syscall.sh`, which launches many instances and later kills them after the livepatch module observes their PIDs.

## Risks and Test Signals

Risks are signal handlers not stopping promptly or the compiler optimizing away loop behavior. Signals are processes staying busy until killed and exiting cleanly when signaled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_klp-call_getpid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/Makefile

## Purpose

`test_modules/Makefile` builds and cleans all kernel modules used by the livepatch selftests.

## Important APIs, Types, and Functions

It defines `TESTMODS_DIR`, default `KDIR`, an `obj-m` list covering all `test_klp_*` modules, and `modules`/`clean` targets that recurse into the kernel build tree with `KBUILD_EXTMOD=$(TESTMODS_DIR)`.

## Control Flow and State

If `KDIR` exists, `make modules` builds the modules and `make clean` removes generated module artifacts. If `KDIR` is missing, both targets skip the kernel recursion instead of failing.

## Dependencies and Integration Points

It depends on a configured kernel build directory, kbuild module infrastructure, and the parent livepatch Makefile's `TEST_GEN_MODS_DIR`.

## Risks and Test Signals

Risks include silent missing modules when `KDIR` does not exist and stale module lists. Signals are generated `.ko` files for every listed module and clean removal through kbuild.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_atomic_replace.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_atomic_replace.c

## Purpose

`test_klp_atomic_replace.c` is a livepatch test module that patches `meminfo_proc_show` and optionally sets `.replace` to exercise atomic-replace semantics.

## Important APIs, Types, and Functions

It defines module parameter `replace`, replacement `livepatch_meminfo_proc_show()`, `struct klp_func`, `struct klp_object`, `struct klp_patch`, and init/exit functions using `klp_enable_patch()`.

## Control Flow and State

On module load, `test_klp_atomic_replace_init()` copies the parameter into `patch.replace` and enables the patch. The patched proc show function prints a module-specific live-patched string. Module exit has no cleanup logic beyond livepatch core handling.

## Dependencies and Integration Points

It depends on livepatch core, procfs `meminfo_proc_show`, and the livepatch scripts that read `/proc/meminfo` and inspect replace behavior.

## Risks and Test Signals

Risks include target symbol name drift and incorrect replace-flag propagation. Signals are `/proc/meminfo` returning the live-patched string and sysfs `replace` reporting the requested value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_atomic_replace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_callbacks_busy.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_callbacks_busy.c

## Purpose

`test_klp_callbacks_busy.c` is a target module that can keep execution inside a function livepatch wants to replace, forcing a livepatch transition to stall.

## Important APIs, Types, and Functions

It defines bool module parameter `block_transition`, work item `busymod_work_func`, completion `busymod_work_started`, and init/exit functions using `schedule_work()`, `wait_for_completion()`, `flush_work()`, `msleep()`, `READ_ONCE()`, and `WRITE_ONCE()`.

## Control Flow and State

On load, it schedules work and waits until the work function logs entry. If `block_transition` is false, init flushes the work so logs are serialized. If true, the worker sleeps in a loop until exit clears the flag, leaving a task inside a patch target.

## Dependencies and Integration Points

It is targeted by `test_klp_callbacks_demo` and driven by `test-callbacks.sh`.

## Risks and Test Signals

Risks are deadlock if `block_transition` is never cleared or failure to stall long enough. Signals are ordered `busymod_work_func enter/exit` logs and livepatch transition staying at 1 while blocked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_callbacks_busy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_callbacks_demo.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_callbacks_demo.c

## Purpose

`test_klp_callbacks_demo.c` is the main callback livepatch module. It patches no-op objects for vmlinux and `test_klp_callbacks_mod`, patches `busymod_work_func` in `test_klp_callbacks_busy`, and logs every callback.

## Important APIs, Types, and Functions

It defines parameter `pre_patch_ret`, callback helpers `pre_patch_callback()`, `post_patch_callback()`, `pre_unpatch_callback()`, `post_unpatch_callback()`, replacement `patched_work_func()`, and `klp_object` entries with callbacks.

## Control Flow and State

On load it enables a patch. Each callback logs object identity and module state; `pre_patch_callback()` can fail with the configured return code. For the busy module, the function replacement participates in transition-stall tests.

## Dependencies and Integration Points

It depends on livepatch callbacks, target modules named in `klp_object.name`, and scripts that compare exact logs across notifier paths.

## Risks and Test Signals

Risks include wrong callback ordering, missing callbacks for module coming/going, and incorrect failure propagation. Signals are exact logs with `MODULE_STATE_*` text and expected `insmod` failure when `pre_patch_ret` is negative.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_callbacks_demo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_callbacks_demo2.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_callbacks_demo2.c

## Purpose

`test_klp_callbacks_demo2.c` is a second callback livepatch module used to test multiple livepatches and atomic replace without external module targets.

## Important APIs, Types, and Functions

It defines parameter `replace`, callback logging functions, a no-function vmlinux `klp_object`, `struct klp_patch`, and init logic that sets `patch.replace` before `klp_enable_patch()`.

## Control Flow and State

On load it applies a vmlinux-only livepatch whose callbacks log patch and unpatch phases. On unload it relies on livepatch core state; there is no custom exit cleanup.

## Dependencies and Integration Points

It integrates with `test-callbacks.sh` scenarios for multiple livepatches and replace behavior.

## Risks and Test Signals

Risks are replace parameter not reflected in the patch or callbacks firing when atomic replacement should skip older patch unpatch callbacks. Signals are exact callback logs and sysfs replace/stack behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_callbacks_demo2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_callbacks_mod.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_callbacks_mod.c

## Purpose

`test_klp_callbacks_mod.c` is a simple target module for livepatch callback tests.

## Important APIs, Types, and Functions

It defines `test_klp_callbacks_mod_init()` and `_exit()` that log their function names with `pr_info()`, plus standard `module_init()` and `module_exit()`.

## Control Flow and State

The module creates no special state. Loading emits an init log, unloading emits an exit log, and livepatch core can attach callbacks to the module object while it transitions through COMING, LIVE, and GOING states.

## Dependencies and Integration Points

It is named by `test_klp_callbacks_demo` and loaded/unloaded by callback and sysfs scripts.

## Risks and Test Signals

Risks are module name drift or missing logs breaking exact dmesg expectations. Signals are init/exit lines surrounding livepatch callback logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_callbacks_mod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_kprobe.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_kprobe.c

## Purpose

`test_klp_kprobe.c` registers a kprobe on `cmdline_proc_show` so livepatch tests can verify conflict behavior with kprobes that do or do not use a post handler.

## Important APIs, Types, and Functions

It defines bool parameter `has_post_handler`, an optional `post_handler()`, `struct kprobe kp` with `.symbol_name = "cmdline_proc_show"`, and init/exit functions calling `register_kprobe()` and `unregister_kprobe()`.

## Control Flow and State

On load, the module conditionally assigns `kp.post_handler` then registers the kprobe. On unload it unregisters the probe. The persistent state is the active kprobe registration.

## Dependencies and Integration Points

It depends on kprobes, the target symbol, and `test-kprobe.sh`.

## Risks and Test Signals

Risks are symbol drift or post-handler semantics changing. Signals are livepatch load failure only when `has_post_handler=true` and success when false.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_kprobe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_livepatch.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_livepatch.c

## Purpose

`test_klp_livepatch.c` is the basic vmlinux livepatch module. It replaces `cmdline_proc_show` so `/proc/cmdline` reports a live-patched string.

## Important APIs, Types, and Functions

It defines replacement `livepatch_cmdline_proc_show()`, a `klp_func` mapping old name `cmdline_proc_show` to the replacement, a vmlinux `klp_object`, `struct klp_patch`, and init/exit functions.

## Control Flow and State

On load, `klp_enable_patch()` activates the replacement. Reads of `/proc/cmdline` flow through the replacement until the patch is disabled and unloaded. The module itself stores only static patch descriptors.

## Dependencies and Integration Points

It is used by most livepatch scripts, depends on the `cmdline_proc_show` symbol and livepatch core, and integrates with ftrace/kprobe/sysfs tests.

## Risks and Test Signals

Risks are symbol rename, livepatch registration failure, or stale replacement after disable. Signals are `/proc/cmdline` showing and then no longer showing `test_klp_livepatch: this has been live patched`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_livepatch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_mod_patch.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_mod_patch.c

## Purpose

`test_klp_mod_patch.c` livepatches a function supplied by the separate `test_klp_mod_target` module.

## Important APIs, Types, and Functions

It defines replacement `livepatch_mod_target_show()`, maps old function name `test_klp_mod_target_show`, targets `klp_object.name = "test_klp_mod_target"`, and enables the patch in module init.

## Control Flow and State

The livepatch can be loaded before or after the target module. When both are present, reads from `/proc/test_klp_mod_target` call the replacement and show the livepatch module name.

## Dependencies and Integration Points

It depends on livepatch module-object matching and the target module's non-inlined show function.

## Risks and Test Signals

Risks include target function inlining/renaming and module notifier failures. Signals are the proc entry switching from original output to patched output and back.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_mod_patch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_mod_target.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_mod_target.c

## Purpose

`test_klp_mod_target.c` is a target module that exposes a proc file backed by a patchable show function.

## Important APIs, Types, and Functions

It defines `static noinline int test_klp_mod_target_show()`, creates `/proc/test_klp_mod_target` with `proc_create_single()`, removes it with `proc_remove()`, and logs init/exit.

## Control Flow and State

On load, it creates the proc entry. Reads return `"test_klp_mod_target: original output"` unless `test_klp_mod_patch` redirects the show function. On unload, it removes the proc entry.

## Dependencies and Integration Points

It depends on procfs and is the named target for `test_klp_mod_patch`.

## Risks and Test Signals

Risks are proc entry allocation failure, missing `noinline`, or stale proc entry removal. Signals are original proc output before/after patching and init/exit dmesg lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_mod_target.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_shadow_vars.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_shadow_vars.c

## Purpose

`test_klp_shadow_vars.c` is a kernel module that exercises the livepatch shadow-variable API over multiple objects and IDs, while producing address-independent log output for shell verification.

## Important APIs, Types, and Functions

It wraps `klp_shadow_get()`, `klp_shadow_alloc()`, `klp_shadow_get_or_alloc()`, `klp_shadow_free()`, and `klp_shadow_free_all()`. It defines `shadow_ctor()`, `shadow_dtor()`, pointer aliasing helpers using a list, constants `NUM_OBJS`, `SV_ID1`, and `SV_ID2`, and a local `struct test_object`.

## Control Flow and State

Module init registers pointer IDs, verifies initial NULL lookup, allocates char and int shadow variables for three objects, verifies retrieval, confirms get-or-alloc returns existing entries, frees all `SV_ID1` entries with destructors, verifies `SV_ID2` remains, then frees all `SV_ID2` entries. Error cleanup frees all known IDs and pointer alias records.

## Dependencies and Integration Points

It depends on livepatch shadow-variable internals, slab allocation, kernel lists, and `test-shadow-vars.sh`.

## Risks and Test Signals

Risks are memory leaks, constructor data mishandling, nondeterministic destructor ordering, and raw pointer logs making tests unstable. Signals are normalized `PTRn` logs matching allocation, lookup, destructor, and final NULL expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_shadow_vars.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_state.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_state.c

## Purpose

`test_klp_state.c` is a livepatch module that modifies global console loglevel state and stores the old value through livepatch state records. Version 1 intentionally does not support migration.

## Important APIs, Types, and Functions

It defines `CONSOLE_LOGLEVEL_STATE`, version 1, `struct klp_state states[]`, callbacks that call `klp_get_state()`, allocate/free state with `kzalloc()`/`kfree()`, and change `console_loglevel` to `CONSOLE_LOGLEVEL_MOTORMOUTH`.

## Control Flow and State

Pre-patch allocates storage, post-patch saves and modifies `console_loglevel`, pre-unpatch restores it, and post-unpatch frees storage. The patch is `.replace = true`.

## Dependencies and Integration Points

It depends on livepatch state API, printk globals, and `test-state.sh`.

## Risks and Test Signals

Risks are state allocation failure, leaked state, incorrect restore ordering, and incompatibility handling. Signals are exact callback logs for allocate, fix, restore, and free, plus expected rejection when stacked after version 2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_state.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_state2.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_state2.c

## Purpose

`test_klp_state2.c` is the migration-capable version of the console loglevel livepatch state test. Version 2 can take over state from compatible previous patches and pass it back when needed.

## Important APIs, Types, and Functions

It uses `klp_get_state()`, `klp_get_prev_state()`, `kzalloc()`, `kfree()`, callback hooks, `struct klp_state` version 2, and `.replace = true`.

## Control Flow and State

Pre-patch allocates storage only if no previous compatible state exists. Post-patch either takes over previous `data` or saves/modifies `console_loglevel`. Pre-unpatch restores only when no previous compatible state exists, otherwise passes ownership back. Post-unpatch frees only when it owns the final state.

## Dependencies and Integration Points

It depends on livepatch cumulative state compatibility and is used by `test-state.sh` with `test_klp_state3`.

## Risks and Test Signals

Risks include double-free, lost state ownership, restoring state while another compatible patch remains, or failing to detect previous state. Signals are logs stating already allocated, taking over, passing back, keeping, restoring, and freeing in the expected scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_state2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_state3.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_state3.c

## Purpose

`test_klp_state3.c` creates another compatible cumulative state livepatch by directly including the implementation of `test_klp_state2.c`.

## Important APIs, Types, and Functions

The file has no independent functions beyond including `"test_klp_state2.c"`. Module identity comes from the build object name even though the code is shared.

## Control Flow and State

Its runtime control flow is identical to `test_klp_state2.c`: allocate or take over console loglevel state on patch, restore or pass back on unpatch, and use state version 2.

## Dependencies and Integration Points

It depends on the included source file and kbuild compiling it as a distinct module. It is used by `test-state.sh` to test multiple compatible cumulative patches.

## Risks and Test Signals

Risks are include-file coupling and accidental divergence if state2 changes incompatibly. Signals are the same logs as state2 but with module name `test_klp_state3`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_state3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_syscall.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_syscall.c

## Purpose

`test_klp_syscall.c` livepatches the architecture-specific `sys_getpid` wrapper and tracks a configured set of PIDs until each has executed the patched function.

## Important APIs, Types, and Functions

It defines architecture-dependent `FN_PREFIX`, mutex `kpid_mutex`, module parameter array `klp_pids`, sysfs read-only attribute `npids`, replacement `lp_sys_getpid()`, `klp_func` for `sys_getpid`, and init/exit functions that create/remove a kobject.

## Control Flow and State

On load, it creates `/sys/kernel/test_klp_syscall/npids`, records the initial PID count, and enables the patch. Each patched `getpid` call locks the mutex, checks whether the current PID is pending, clears its slot, decrements `npids_pending`, and returns `task_tgid_vnr(current)`. Exit drops the kobject.

## Dependencies and Integration Points

It depends on livepatch syscall symbol naming, sysfs, module parameter arrays, and `test-syscall.sh`.

## Risks and Test Signals

Risks include wrong symbol prefix for an architecture, `NR_CPUS` limiting parameter count, mutex contention, or sysfs lifetime bugs on load failure. Signals are `npids` reaching 0 and helpers continuing to receive valid getpid results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_syscall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/liveupdate/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/liveupdate/Makefile

## Purpose

`liveupdate/Makefile` builds liveupdate selftest binaries and shared utility objects, registers the kexec helper script, and tracks generated dependency files.

## Important APIs, Types, and Functions

It sets `LIB_C += luo_test_utils.c`, `TEST_GEN_PROGS += liveupdate`, `TEST_GEN_PROGS_EXTENDED += luo_kexec_simple luo_multi_session`, `TEST_FILES += do_kexec.sh`, includes `../lib.mk`, adds kernel header includes and warning flags, builds `LIB_O`, `TEST_O`, and dependency `.d` files, and defines custom link rules.

## Control Flow and State

The Makefile compiles library objects into `OUTPUT`, compiles each test object, links test binaries with the shared utility object, includes generated dependency files, and extends `EXTRA_CLEAN` so object and dependency files are removed.

## Dependencies and Integration Points

It depends on `lib.mk`, kernel UAPI headers, liveupdate C sources outside this subset, and standard compiler dependency generation.

## Risks and Test Signals

Risks include stale `.d` files, missing shared object linkage, and divergence from common `lib.mk` pattern rules. Signals are successful builds of `liveupdate`, `luo_kexec_simple`, and `luo_multi_session`, plus clean removing generated objects/deps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/liveupdate/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/liveupdate/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/liveupdate/config

## Purpose

`liveupdate/config` lists kernel features required by the liveupdate selftests and their kexec handover path.

## Important APIs, Types, and Functions

It declares `CONFIG_BLK_DEV_INITRD`, `CONFIG_KEXEC_FILE`, `CONFIG_KEXEC_HANDOVER`, `CONFIG_KEXEC_HANDOVER_ENABLE_DEFAULT`, `CONFIG_KEXEC_HANDOVER_DEBUGFS`, `CONFIG_KEXEC_HANDOVER_DEBUG`, `CONFIG_LIVEUPDATE`, `CONFIG_LIVEUPDATE_TEST`, `CONFIG_MEMFD_CREATE`, `CONFIG_TMPFS`, and `CONFIG_SHMEM`.

## Control Flow and State

There is no executable flow. The file is consumed by selftest config checking to flag missing prerequisites.

## Dependencies and Integration Points

It integrates with the liveupdate test binaries and `do_kexec.sh`, which need kexec, initramfs, memfd, tmpfs/shmem, and liveupdate debug/test support.

## Risks and Test Signals

Risks are stale symbols causing false capability assumptions. Signals are config-check output and runtime tests finding the required debugfs/kexec/liveupdate facilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/liveupdate/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/liveupdate/do_kexec.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/liveupdate/do_kexec.sh

## Purpose

`do_kexec.sh` is a helper that loads and executes a replacement kernel for liveupdate tests using kexec file loading and command-line reuse.

## Important APIs, Types, and Functions

It uses `/bin/sh`, `set -e`, environment variables `KERNEL` and `INITRAMFS`, default paths `/boot/bzImage` and `/boot/initramfs`, and commands `kexec -l -s --reuse-cmdline`, optional `--initrd=...`, and `kexec -e`.

## Control Flow and State

The script builds the `kexec` argument vector with `set --`, conditionally appends an initrd if the file exists, loads the kernel, then immediately executes it. State changes are system-wide: a kernel image is loaded into kexec state and then booted.

## Dependencies and Integration Points

It depends on root privileges, kexec tooling, a valid kernel image, optional initramfs, and kernel support declared in `liveupdate/config`.

## Risks and Test Signals

Risks are destructive by design: successful `kexec -e` replaces the running kernel. Other risks are wrong default paths and missing initrd. Signals are shell exit on failed load and actual transition to the new kernel on success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/liveupdate/do_kexec.sh -->

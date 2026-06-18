<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/keyctl.c -->
# sources/security-integrity/keyutils/keyctl.c

## Purpose

`keyctl.c` is the command-line frontend for Linux kernel key retention service operations. It maps subcommands to libkeyutils wrappers and syscalls for creating keys, keyrings, reading payloads, changing ownership and permissions, searching, linking, unlinking, instantiating requested keys, Diffie-Hellman computation, public-key operations, keyring restriction, moving keys, capability probing, recursive cleanup, and watch/test extension entry points.

## Important APIs, Types, and Functions

The central command table binds names such as `add`, `padd`, `request`, `request2`, `update`, `newring`, `revoke`, `clear`, `link`, `unlink`, `search`, `read`, `pipe`, `print`, `list`, `describe`, `session`, `instantiate`, `negate`, `reject`, `purge`, `invalidate`, `dh_compute`, `dh_compute_kdf`, `restrict_keyring`, `pkey_*`, `move`, `supports`, `watch*`, and `--test` to noreturn action functions. Shared helpers include `do_command()` for prefix/exact command dispatch, `format()` for usage, `error()` for perror-and-exit, `get_key_id()` for numeric/special/name lookup parsing, `hex2bin()` for optional hex payload conversion, `grab_stdin()` for pipe payloads, `calc_perms()` for effective permission display, `read_file()` for pkey inputs, and `dump_key_tree()`/`dump_key_tree_aux()` for recursive keyring rendering.

## Control Flow

`main()` delegates to `do_command()`, which consumes the program name, finds an unambiguous command match, and invokes the action. Each action validates argument count, converts key IDs with `get_key_id()`, invokes the relevant libkeyutils function, prints IDs or formatted payloads where appropriate, and exits. Recursive commands use `recursive_session_key_scan()` callbacks to unlink, reap, or purge keys. DH and pkey commands allocate output buffers based on kernel-reported lengths or pkey query limits before emitting hex/binary output. `session` and `new_session` change process/session keyring state and then exec a shell or target program.

## State and Persistence Behavior

The file has no durable storage of its own; it mutates kernel keyrings through `add_key()`, `request_key()`, and `keyctl()` operations. Key material can be read from argv, stdin, or files; sensitive buffers are wiped where explicit conversions or DH outputs are handled. Process state includes cached effective UID/GID/group data for permission display, the `verbose` flag, and command-local allocations. Kernel state changes include key creation/update/revocation/invalidation, keyring links, ownership/permission changes, restriction application, persistent keyring retrieval, and session keyring joins.

## Dependencies and Integration Points

The program depends on `keyutils.h` for kernel constants and wrappers, `keyctl.h` for command declarations shared with watch/testing modules, Linux syscall availability, `/proc/keys` lookup via library helper code, and libc process/file APIs. It integrates with `keyctl_watch.c` through watch subcommands and `keyctl_testing.c` through `--test`. It is the primary executable exercised by the shell tests under `tests/keyctl`.

## Risks and Edge Cases

Command prefix matching is convenient but can become ambiguous when new names share prefixes. `grab_stdin()` hard-limits stdin payloads to 1 MiB, while request-key pipe handling elsewhere has a smaller payload buffer. Some numeric parsing uses `strtoul()` without full range validation beyond trailing characters. Pkey encrypt/decrypt allocate buffers using query fields that must match kernel semantics; a mismatch can truncate or fail operations. Recursive traversal depth limits prevent unbounded recursion but may hide deeper trees. Name lookup via `%type:desc` ultimately depends on `/proc/keys` visibility and description parsing.

## Test Signals

The mapped tests cover bad/no-arg handling, add/padd/pupdate payload paths, keyring clear/list/describe/read, ID parsing, instantiation failures, invalidation, link and move recursion, duplicate link semantics, request-key callouts, keyring restrictions, and revoke errors. Feature tests exercise DH vectors, built-in trusted keyrings, and kernel limit probes.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/keyctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/keyctl.h -->
# sources/security-integrity/keyutils/keyctl.h

## Purpose

`keyctl.h` is the shared internal interface for the `keyctl` executable modules. It defines the command dispatch structure and declares common frontend helpers plus the watch and built-in test action entry points.

## Important APIs, Types, and Functions

`struct command` carries a noreturn action pointer, command name, and usage format. The `nr` macro applies `__attribute__((noreturn))`. Exported internal declarations include `do_command()`, `format()`, `error()`, `get_key_id()`, `act_keyctl_test()`, `act_keyctl_watch()`, `act_keyctl_watch_add()`, `act_keyctl_watch_rm()`, `act_keyctl_watch_session()`, and `act_keyctl_watch_sync()`.

## Control Flow

This header has no runtime control flow. It lets `keyctl.c` dispatch commands implemented in `keyctl_testing.c` and `keyctl_watch.c` through one command table.

## State and Persistence Behavior

No state is stored here. The declarations expose functions that mutate process or kernel keyring state elsewhere.

## Dependencies and Integration Points

It depends on `key_serial_t` being visible from `keyutils.h` before inclusion. It is included by `keyctl.c`, `keyctl_testing.c`, and `keyctl_watch.c`, making it the coupling point for command-line module integration.

## Risks and Edge Cases

The header omits include guards, so duplicate inclusion would redeclare symbols if translation units include it more than once. The noreturn function pointer type must stay consistent with all action implementations or compiler diagnostics and undefined assumptions can follow.

## Test Signals

Successful compilation of the three `keyctl` modules and use of `--test` plus `watch*` commands confirms this shared dispatch contract.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/keyctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/keyctl_testing.c -->
# sources/security-integrity/keyutils/keyctl_testing.c

## Purpose

`keyctl_testing.c` adds hidden `keyctl --test` subcommands for probing kernel key type, description, and user payload limits. These routines are used by the feature limit tests rather than by normal users.

## Important APIs, Types, and Functions

`test_commands[]` maps `limits` and `limits2` to `act_keyctl_test_limits()` and `act_keyctl_test_limits2()`. `act_keyctl_test()` delegates through shared `do_command()`. `act_keyctl_test_limits()` varies key type and description lengths, expecting invalid type errors or valid user-key creation within size limits. `act_keyctl_test_limits2()` iterates payload sizes up to just over 1 MiB, expecting user-type payload acceptance only for 1..32767 bytes while tolerating transient `EDQUOT`.

## Control Flow

The top-level test command validates a subcommand and dispatches it. Each limit test runs a loop, prints progress markers to stdout, creates keys on the thread keyring, unlinks any successful temporary key, counts unexpected outcomes, and aborts early after too many failures.

## State and Persistence Behavior

Temporary keys are created in `KEY_SPEC_THREAD_KEYRING` and unlinked immediately when creation succeeds. Local buffers carry candidate type/description/payload content. No filesystem state is written by this module.

## Dependencies and Integration Points

The file uses `add_key()` and `keyctl_unlink()` from libkeyutils, `KEY_SPEC_THREAD_KEYRING`, and command dispatch declarations from `keyctl.h`. `tests/features/limits/runtest.sh` is the main integration point.

## Risks and Edge Cases

The loops are intentionally heavy and can hit quota races; `limits2` treats `EDQUOT` as acceptable for fast key creation. Kernel-version behavior differs on older MIPS kernels, so external tests gate part of the run. The static payload buffer is large and stack-allocated.

## Test Signals

Pass signals are zero exit status from `keyctl --test limits` and `keyctl --test limits2`, with no unexpected errno values and no leaked temporary keys in the thread keyring.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/keyctl_testing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/keyctl_watch.c -->
# sources/security-integrity/keyutils/keyctl_watch.c

## Purpose

`keyctl_watch.c` implements `keyctl` watch-queue subcommands for observing Linux key notifications. It can watch one key directly, add/remove watches to an inherited monitor, run a command in a watched session keyring, and synchronize pending notifications.

## Important APIs, Types, and Functions

The module uses `watch_queue.h` structures such as `watch_notification`, `key_notification`, `watch_notification_filter`, and notification subtype constants. `open_watch()` creates an `O_NOTIFICATION_PIPE` pipe and configures queue size/filter ioctls. `consumer()` polls/reads notification records, validates lengths, and dispatches to `saw_key_change()` or `saw_removal_notification()`. `parse_watch_filter()` converts one-letter subtype filters. Action functions are `act_keyctl_watch()`, `act_keyctl_watch_add()`, `act_keyctl_watch_rm()`, `act_keyctl_watch_session()`, and `act_keyctl_watch_sync()`.

## Control Flow

Direct watch mode parses optional filters, opens a watch queue, attaches watch ID 1 to the target key, and enters the consumer loop. Watch-session mode opens and optionally dup2s the watch fd, clears close-on-exec, forks a notification consumer, joins a new session keyring, watches it, exports `KEYCTL_WATCH_FD` to the child command, then waits for child/consumer termination and propagates status. Add/remove commands call `keyctl_watch_key()` with watch ID 2 or `-1`. Sync uses `PIPE_IOC_SYNC` when available or waits until `FIONREAD` reports no queued bytes.

## State and Persistence Behavior

State is process-local: global child PIDs, current session keyring ID, watch fd, debug flag, and notification filter. Persistent kernel changes are limited to watch registrations and a temporary/new session keyring. Log and GC files are appended by `watch_session`; direct watch writes to stdout.

## Dependencies and Integration Points

The module depends on Linux watch queues, notification pipes, `KEYCTL_WATCH_KEY`, `ioctl()` constants, `poll()`, `fork()/exec()`, and shared `keyctl` helpers. It integrates with command scripts through inherited fd `KEYCTL_WATCH_FD`.

## Risks and Edge Cases

Kernel support is required; unsupported notification pipes or watch ioctls fail at startup. The consumer exits on malformed or short records. `exit_cleanup()` kills child processes from the parent only, so PID bookkeeping must remain correct across forks. Filter parsing silently reserves one filter slot and only supports known key notification letters. Watch-session requires target fds 3..9.

## Test Signals

Relevant tests would assert event lines for instantiate/update/link/unlink/clear/revoke/invalidate/setattr, GC removal behavior, filter selection, inherited fd use, and sync fallback on kernels without `PIPE_IOC_SYNC`.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/keyctl_watch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/keyutils.c -->
# sources/security-integrity/keyutils/keyutils.c

## Purpose

`keyutils.c` is the libkeyutils implementation layer. It exposes weak syscall wrappers for `add_key`, `request_key`, and `keyctl`, typed wrappers for individual keyctl commands, allocated-buffer convenience helpers, recursive keyring traversal, type/description lookup, capability emulation for older kernels, and optional key-specific strerror/perror overrides.

## Important APIs, Types, and Functions

Weak wrappers call `__NR_add_key`, `__NR_request_key`, and `__NR_keyctl`. Typed wrappers cover keyring ID/session join, update, revoke, chown, setperm, describe, clear, link/unlink, search, read, instantiate/negate/reject, request-key defaults, timeout, authority, security label, parent-session installation, invalidate, persistent keyrings, DH/KDF, restrict, pkey query/encrypt/decrypt/sign/verify, move, capabilities, and watch. Allocation helpers are `keyctl_describe_alloc()`, `keyctl_read_alloc()`, `keyctl_get_security_alloc()`, and `keyctl_dh_compute_alloc()`. Traversal helpers are `recursive_key_scan()`, `recursive_session_key_scan()`, and `find_key_by_type_and_desc()`.

## Control Flow

Most wrappers are thin one-line `keyctl()` calls. Compatibility paths fall back from `KEYCTL_REJECT` to negate and from `KEYCTL_INSTANTIATE_IOV` to a concatenated buffer when the kernel returns `EOPNOTSUPP`. Capability emulation probes individual operations when `KEYCTL_CAPABILITIES` is not available. Alloc helpers first query required length, allocate, retry, and loop if a variable-sized result grows. Recursive scanning describes a key, reads child IDs for keyrings, depth-first scans children, then calls the user callback for the current key. Name lookup first tries `request_key()` and then scans `/proc/keys` with a confirming `keyctl_describe()`.

## State and Persistence Behavior

The library does not persist data itself, but it mutates kernel keyring state through syscall wrappers. Alloc helpers return heap buffers owned by callers. Recursive scans and lookup read key descriptions and keyring payloads from the kernel. Optional error override mode keeps function pointers resolved from `RTLD_NEXT`.

## Dependencies and Integration Points

The file depends on Linux keyring syscalls, `sys/uio.h` for instantiate-iov, `/proc/keys` for fallback lookup, `dlfcn.h` under `NO_GLIBC_KEYERR`, and `keyutils.h` ABI definitions. It backs the `keyctl` executable, request-key helper, tests, and external applications linking `libkeyutils`.

## Risks and Edge Cases

Thin syscall wrappers trust caller-provided pointers and lengths. IOV fallback can overflow `size_t` if a malicious caller passes huge segment lengths. Alloc helpers can race with changing key contents and must retry; callers must free results. `/proc/keys` fallback depends on procfs format and visibility. Capability emulation probes with invalid IDs and infers support from errno, which can be imperfect under policy restrictions. The optional `strerror_r()` override contains a debug `printf("hello")`, making that build mode noisy.

## Test Signals

The shell suite exercises most wrappers through `keyctl`. Direct library validation should compile/link consumers, test fallback behavior on older kernels, verify allocated-buffer growth races, scan recursive keyrings, and compare `supports` output with expected kernel capabilities.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/keyutils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/keyutils.h -->
# sources/security-integrity/keyutils/keyutils.h

## Purpose

`keyutils.h` is the public C API and ABI definition for libkeyutils. It defines key serial and permission types, special keyring IDs, keyctl command numbers, request-key defaults, DH/KDF/pkey structures, capability flags, move flags, syscall wrappers, typed keyctl wrappers, and utility helpers.

## Important APIs, Types, and Functions

Core types are `key_serial_t` and `key_perm_t`. Constants include `KEY_SPEC_*`, `KEY_REQKEY_DEFL_*`, permission masks for possessor/user/group/other classes, `KEYCTL_*` command numbers 0..32, `KEYCTL_SUPPORTS_*`, `KEYCTL_MOVE_EXCL`, and `KEYCTL_CAPS*`. Structures include `keyctl_dh_params`, `keyctl_kdf_params`, `keyctl_pkey_query`, and `keyctl_pkey_params`. Function prototypes expose `add_key()`, `request_key()`, variadic `keyctl()`, all typed wrappers, allocation helpers, recursive scanning, and `find_key_by_type_and_desc()`.

## Control Flow

This header has no runtime control flow. It establishes the binary/source contract consumed by `keyutils.c`, `keyctl.c`, request-key, and outside callers.

## State and Persistence Behavior

No state is stored here. The declared APIs operate on kernel-retained key state and may allocate caller-owned buffers when using `_alloc` helpers.

## Dependencies and Integration Points

The header is C/C++ compatible via `extern "C"`. It includes `sys/types.h` and `stdint.h`, forward-declares `struct iovec`, and must match kernel UAPI command numbers and structure layouts.

## Risks and Edge Cases

ABI drift is the primary risk: command numbers, structure padding, and integer widths must remain compatible with kernel expectations and existing applications. The variadic `keyctl()` prototype exposes weak type checking, so typed wrappers are safer for callers. Public constants require careful extension to avoid reusing bits or command numbers.

## Test Signals

Build tests should compile C and C++ users, verify structure sizes/layouts where ABI matters, and exercise each public wrapper against a kernel with matching keyring support.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/keyutils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/libkeyutils.pc.in -->
# sources/security-integrity/keyutils/libkeyutils.pc.in

## Purpose

`libkeyutils.pc.in` is the pkg-config template for consumers of libkeyutils. Build substitution fills `@libdir@`, `@includedir@`, and `@VERSION@`.

## Important APIs, Types, and Functions

It exports package metadata `Name`, `Description`, `Version`, compile flags `-I${includedir}`, and link flags `-L${libdir} -lkeyutils`.

## Control Flow

There is no runtime control flow; it is transformed by the build/install process into `libkeyutils.pc`.

## State and Persistence Behavior

Installed pkg-config metadata persists in the target pkg-config directory and guides downstream builds.

## Dependencies and Integration Points

It integrates with pkg-config, the project Makefile/configure substitution path, and applications using `pkg-config --cflags --libs libkeyutils`.

## Risks and Edge Cases

Incorrect substitution paths produce broken downstream compile/link flags. Missing extra private libs would affect static linking if future code adds dependencies.

## Test Signals

After install, `pkg-config --modversion libkeyutils` and `pkg-config --libs --cflags libkeyutils` should return the substituted version and usable flags.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/libkeyutils.pc.in -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/request-key-debug.sh -->
# sources/security-integrity/keyutils/request-key-debug.sh

## Purpose

`request-key-debug.sh` is a simple debug helper invoked from `request-key.conf` for user keys with `debug:*` descriptions. It instantiates requested keys with a predictable payload or negates them when the callout info asks for `neg`.

## Important APIs, Types, and Functions

The script expects positional arguments `<keyid> <desc> <callout> <session-keyring>`. It uses the `keyctl instantiate` and `keyctl negate` CLI operations and prints diagnostic context.

## Control Flow

It echoes the request parameters. If the callout string is not `neg`, it instantiates the in-progress key with payload `Debug <callout>` into the supplied session keyring. If the callout is `neg`, it dumps `/proc/keys`, prints the negate command, and negates the key for 30 seconds.

## State and Persistence Behavior

The script mutates kernel key state by instantiating or negating the requested key. It reads `/proc/keys` only for debug output and writes diagnostics to stdout.

## Dependencies and Integration Points

It is referenced by `request-key.conf` and depends on `/bin/sh`, `keyctl`, and `/proc/keys`. It is part of request-key callout testing for debug user keys.

## Risks and Edge Cases

Arguments are unquoted in echo output and the script assumes `keyctl` is in PATH. It is intentionally diagnostic and should not be used as a privileged general-purpose production resolver.

## Test Signals

Requesting `user debug:<name>` with arbitrary callout should instantiate a key readable as `Debug <callout>`; callout `neg` should produce a negatively instantiated key.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/request-key-debug.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/request-key.c -->
# sources/security-integrity/keyutils/request-key.c

## Purpose

`request-key.c` is the `/sbin/request-key` helper that the kernel invokes to resolve, instantiate, negate, or reject keys. It parses kernel-provided request parameters, discovers the requested key type/description/callout info, selects the best matching action from request-key configuration files, expands macros, and executes or pipes data through the chosen program.

## Important APIs, Types, and Functions

`struct parameters` stores key ID, operation, requestor IDs/keyrings, key type/description, callout info, and cached string lengths. Main helpers are `lookup_action()`, `scan_conf_dir()`, `scan_conf_file()`, wildcard `match()`, `execute_program()`, and `pipe_to_program()`. Diagnostic helpers are `debug()`, `error()`, and signal handler `oops()`. It uses `keyctl_assume_authority()`, `keyctl_describe_alloc()`, `keyctl_read_alloc()`, and `keyctl_instantiate()`.

## Control Flow

`main()` handles `--version` and debug/local/no-log/verbose options, validates seven or eight kernel arguments, ensures stdio fds are open, optionally assumes authority over the requested key, describes the key, retrieves callout info if omitted, and calls `lookup_action()`. Lookup scans `/etc/request-key.d/*.conf` before `/etc/request-key.conf` unless local-dir mode is selected. Each config line matches operation, type, description, and callout info with one `*` wildcard per field; the least-wild match wins. `execute_program()` tokenizes the command, expands `%` macros and `%{type:desc}` keysub reads, then either `execv()`s or invokes `pipe_to_program()` for `|` commands. Pipe mode concurrently writes callout info to child stdin, collects payload from stdout, logs stderr, and instantiates the key; child failure recursively switches to `negate`.

## State and Persistence Behavior

Global state tracks verbosity, local-dir/no-log/debug flags, current config file/line, recursion guard, selected command, and wildcard score. Kernel state changes include assuming request authority, reading the authorization key, instantiating successful payloads, or delegating negate/reject actions. Filesystem reads are config files/directories and executed helper programs; syslog receives debug/errors unless disabled.

## Dependencies and Integration Points

The helper integrates with kernel request-key upcalls, `/etc/request-key.d`, `/etc/request-key.conf`, `request-key-debug.sh`, key resolver programs such as `key.dns_resolver`, syslog, and libkeyutils. It relies on trusted configuration because commands execute with helper privileges and receive kernel/requestor context.

## Risks and Edge Cases

Config parsing is whitespace-token based with no shell quoting. Command and line buffers are fixed at about 4096 bytes; pipe payload is capped at 32768 bytes. Macro expansion passes arguments directly to `execv()` but keysub macro data must be printable. Wildcard scoring prefers less wildcard consumption but ties keep the first selected command. Recursive negation is guarded by `norecurse` but misconfigured negate actions can still fail the request. Local-dir debug mode changes config search roots.

## Test Signals

Requesting tests exercise invalid type/description/callout bounds, direct callouts, piped callouts, attachment to destination/session keyrings, negative results, and config-driven debug helper behavior. Additional validation should include directory precedence, wildcard specificity, keysub macros, stderr logging, and child failure recursion.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/request-key.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/request-key.conf -->
# sources/security-integrity/keyutils/request-key.conf

## Purpose

`request-key.conf` is the default request-key policy file. It maps key request operations, key types, descriptions, and callout-info patterns to resolver programs.

## Important APIs, Types, and Functions

The file documents supported macros: `%%`, `%o`, `%k`, `%t`, `%d`, `%c`, `%u`, `%g`, `%T`, `%P`, and `%S`. Active rules resolve `dns_resolver` through `/sbin/key.dns_resolver`, debug user keys through `keyctl negate`, `keyctl reject`, a piped `/bin/cat`, or `request-key-debug.sh`, and generic negate through `/bin/keyctl negate`.

## Control Flow

At runtime `request-key.c` scans these rules, matches fields with wildcard support, chooses the least-wild matching line, expands macros, and executes the command. Lines beginning with `|` run in pipe mode where callout info is stdin and stdout becomes key payload.

## State and Persistence Behavior

The file itself is static configuration. Its actions can instantiate, reject, revoke, expire, or negate kernel keys depending on matched requests.

## Dependencies and Integration Points

It integrates with `/sbin/request-key`, `/sbin/key.dns_resolver`, `/bin/keyctl`, `/bin/cat`, and `/usr/share/keyutils/request-key-debug.sh`. It is part of system key resolver policy and test setup.

## Risks and Edge Cases

Rule order and wildcard specificity affect resolver selection. Hard-coded binary paths must match installation layout. Piped debug rules can echo arbitrary callout data into key payloads and are suitable for tests/debugging, not broad trust decisions.

## Test Signals

Request-key valid and piped tests should resolve `user debug:*` requests, attach results to expected keyrings, and exercise negate/reject/expired/revoked callout forms.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/request-key.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/Makefile -->
# sources/security-integrity/keyutils/tests/Makefile

## Purpose

`tests/Makefile` is the RHTS-style test harness entry point for the keyutils testsuite. It discovers all `runtest.sh` files and runs them through the top-level test runner.

## Important APIs, Types, and Functions

Variables define namespace/package metadata, `TESTVERSION`, `TEST`, discovered `TESTS`, `FILES`, and optional `METADATA` generation when Red Hat test harness includes are available. Targets include `run`, `build`, and `clean`.

## Control Flow

`run` depends on files/build and invokes `bash runtest.sh $(TESTS)`. `TESTS` is produced with `find` and path cleanup. `clean` removes temporary files and nested `test.out` artifacts. Under `/usr/share/rhts/lib/rhts-make.include`, metadata is generated and linted.

## State and Persistence Behavior

The Makefile writes test metadata only in RHTS environments and deletes `test.out` files on clean. Test scripts themselves mutate kernel keyrings during execution.

## Dependencies and Integration Points

It depends on bash, find, sed, optional RHTS make include/lint tooling, and the sibling `runtest.sh` orchestrator plus all nested test directories.

## Risks and Edge Cases

Discovery includes every nested `runtest.sh`, so newly added tests run automatically. Environment-specific RHTS metadata generation can fail if support tools are partially installed. Clean uses `find *`, so it assumes a populated tests directory.

## Test Signals

`make run` should invoke the full test list, and `make clean` should remove transient outputs without deleting test sources.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/bugzillas/bz1031154/runtest.sh -->
# sources/security-integrity/keyutils/tests/bugzillas/bz1031154/runtest.sh

## Purpose

This shell test provides regression coverage for Red Hat Bugzilla bz1031154, focused on kernel keyring behavior that previously regressed. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../prepare.inc.sh, ../../toolbox.inc.sh. Important helper/API calls observed in the source include: cat, export, failed, load_policy, marker, pcreate_key_by_size, require_command, require_selinux, sleep, toolbox_report_result, toolbox_skip_test. Expected errno assertions are: none explicitly asserted. Capability or environment gates are: have_big_key_type.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: ENTER SELINUX PERMISSIVE MODE, CREATE BIG KEY, CHECK BIG KEY, ACCESS INTERCONTEXT, EXAMINE AUDIT LOGS, RESTORE SELINUX MODE.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/bugzillas/bz1031154/runtest.sh` preserves the expected behavior for regression coverage for Red Hat Bugzilla bz1031154, focused on kernel keyring behavior that previously regressed. The explicit expected errors (`none explicitly asserted`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/bugzillas/bz1031154/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/bugzillas/bz1033467/runtest.sh -->
# sources/security-integrity/keyutils/tests/bugzillas/bz1033467/runtest.sh

## Purpose

This shell test provides regression coverage for Red Hat Bugzilla bz1033467, focused on kernel keyring behavior that previously regressed. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../prepare.inc.sh, ../../toolbox.inc.sh. Important helper/API calls observed in the source include: create_key, create_keyring, expect_error, failed, marker, search_for_key, toolbox_report_result. Expected errno assertions are: ENOKEY. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: ADD SANDBOX KEYRING, ADD NESTED KEYRINGS, ADD KEYS, SEARCH KEYS, COMPARE KEY LISTS, SEARCH MISSES.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/bugzillas/bz1033467/runtest.sh` preserves the expected behavior for regression coverage for Red Hat Bugzilla bz1033467, focused on kernel keyring behavior that previously regressed. The explicit expected errors (`ENOKEY`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/bugzillas/bz1033467/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/bugzillas/bz1071346/runtest.sh -->
# sources/security-integrity/keyutils/tests/bugzillas/bz1071346/runtest.sh

## Purpose

This shell test provides regression coverage for Red Hat Bugzilla bz1071346, focused on kernel keyring behavior that previously regressed. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../prepare.inc.sh, ../../toolbox.inc.sh. Important helper/API calls observed in the source include: create_keyring, expect_error, link_key, marker, toolbox_report_result, unlink_key. Expected errno assertions are: EDEADLK. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: ADD SANDBOX KEYRING, ADD SECOND SANDBOX KEYRING, CHECK NO LINK SESSION TO SECOND, CHECK NO LINK SANDBOX TO SECOND, CHECK NO LINK SECOND TO SECOND, ADD SIDE KEYRING, ADD THIRD SANDBOX KEYRING, CHECK NO LINK SESSION TO THIRD, CHECK NO LINK SANDBOX TO THIRD, CHECK NO LINK SIDE TO THIRD, CHECK NO LINK THIRD TO THIRD, CHECK LINK SECOND TO THIRD, CHECK NO LINK THIRD TO SECOND, UNLINK SECOND FROM THIRD, and 2 additional markers.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/bugzillas/bz1071346/runtest.sh` preserves the expected behavior for regression coverage for Red Hat Bugzilla bz1071346, focused on kernel keyring behavior that previously regressed. The explicit expected errors (`EDEADLK`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/bugzillas/bz1071346/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/features/builtin_trusted/runtest.sh -->
# sources/security-integrity/keyutils/tests/features/builtin_trusted/runtest.sh

## Purpose

This shell test provides feature coverage for the `builtin_trusted` keyutils/kernel capability. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../prepare.inc.sh, ../../toolbox.inc.sh. Important helper/API calls observed in the source include: a4aadc8d, a9293377, ac4306b7, bc38ae82, be30f90c, create_key, d0e9cbce, d4e93686, d867638a, d976c1b4, da73b7cd, e8ab87d0, eeca00ec, expect_error, expect_keyring_rlist, f589d945, f6fae4b5, f70d0101, and 5 more helpers. Expected errno assertions are: EACCES, ENOKEY, EOPNOTSUPP. Capability or environment gates are: have_public_key.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: FIND BUILTIN TRUSTED KEYRINGS, TRY ADDING USER KEYS, TRY ADDING ASYMMETRIC KEYS.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/features/builtin_trusted/runtest.sh` preserves the expected behavior for feature coverage for the `builtin_trusted` keyutils/kernel capability. The explicit expected errors (`EACCES, ENOKEY, EOPNOTSUPP`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/features/builtin_trusted/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/features/limits/runtest.sh -->
# sources/security-integrity/keyutils/tests/features/limits/runtest.sh

## Purpose

This shell test provides feature coverage for the `limits` keyutils/kernel capability. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../prepare.inc.sh, ../../toolbox.inc.sh. Important helper/API calls observed in the source include: failed, marker, toolbox_report_result. Expected errno assertions are: none explicitly asserted. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: TEST TYPE AND DESC LIMITS, TEST PAYLOAD LIMIT.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/features/limits/runtest.sh` preserves the expected behavior for feature coverage for the `limits` keyutils/kernel capability. The explicit expected errors (`none explicitly asserted`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/features/limits/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/add/bad-args/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/add/bad-args/runtest.sh

## Purpose

This shell test provides `keyctl add` bad-args coverage for key creation with inline payloads and optional hex decoding. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: clear_keyring, create_key, expect_error, marker, toolbox_report_result. Expected errno assertions are: EDQUOT, EINVAL, ENODEV, EPERM. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: CHECK EMPTY KEY TYPE, CHECK UNSUPPORTED KEY TYPE, CHECK INVALID KEY TYPE, CHECK MAXLEN KEY TYPE, CHECK OVERLONG KEY TYPE, CHECK ADD KEYRING WITH PAYLOAD, CHECK MAXLEN DESC, CHECK MAXLEN DESC FAILS WITH EDQUOT, CHECK OVERLONG DESC, CHECK BAD KEY ID.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/add/bad-args/runtest.sh` preserves the expected behavior for `keyctl add` bad-args coverage for key creation with inline payloads and optional hex decoding. The explicit expected errors (`EDQUOT, EINVAL, ENODEV, EPERM`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/add/bad-args/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/add/noargs/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/add/noargs/runtest.sh

## Purpose

This shell test provides `keyctl add` noargs coverage for key creation with inline payloads and optional hex decoding. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: expect_args_error, marker, toolbox_report_result. Expected errno assertions are: none explicitly asserted. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: ADD NO ARGS, ADD ONE ARG, ADD TWO ARGS, ADD THREE ARGS, ADD FIVE ARGS.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/add/noargs/runtest.sh` preserves the expected behavior for `keyctl add` noargs coverage for key creation with inline payloads and optional hex decoding. The explicit expected errors (`none explicitly asserted`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/add/noargs/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/add/useradd/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/add/useradd/runtest.sh

## Purpose

This shell test provides `keyctl add` useradd coverage for key creation with inline payloads and optional hex decoding. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: create_key, expect_error, expect_payload, keyctl, marker, print_key, toolbox_report_result, unlink_key. Expected errno assertions are: ENOTDIR. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: ADD USER KEY, PRINT PAYLOAD, ADD HEX USER KEY, PRINT PAYLOAD, UPDATE USER KEY, PRINT UPDATED PAYLOAD, ADD KEY TO NON-KEYRING, UNLINK KEY.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/add/useradd/runtest.sh` preserves the expected behavior for `keyctl add` useradd coverage for key creation with inline payloads and optional hex decoding. The explicit expected errors (`ENOTDIR`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/add/useradd/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/clear/bad-args/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/clear/bad-args/runtest.sh

## Purpose

This shell test provides `keyctl clear` bad-args coverage for keyring clearing semantics. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: clear_keyring, create_key, expect_error, marker, toolbox_report_result, unlink_key. Expected errno assertions are: EINVAL, ENOKEY, ENOTDIR. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: CHECK CLEAR BAD KEY ID, CREATE KEY, CHECK CLEAR NON-KEYRING KEY, UNLINK KEY, CHECK CLEAR NON-EXISTENT KEY ID.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/clear/bad-args/runtest.sh` preserves the expected behavior for `keyctl clear` bad-args coverage for keyring clearing semantics. The explicit expected errors (`EINVAL, ENOKEY, ENOTDIR`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/clear/bad-args/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/clear/noargs/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/clear/noargs/runtest.sh

## Purpose

This shell test provides `keyctl clear` noargs coverage for keyring clearing semantics. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: expect_args_error, marker, toolbox_report_result. Expected errno assertions are: none explicitly asserted. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: NO ARGS, TWO ARGS.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/clear/noargs/runtest.sh` preserves the expected behavior for `keyctl clear` noargs coverage for keyring clearing semantics. The explicit expected errors (`none explicitly asserted`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/clear/noargs/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/clear/valid/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/clear/valid/runtest.sh

## Purpose

This shell test provides `keyctl clear` valid coverage for keyring clearing semantics. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: clear_keyring, create_key, create_keyring, describe_key, expect_key_rdesc, expect_keyring_rlist, failed, list_keyring, marker, toolbox_report_result, unlink_key. Expected errno assertions are: none explicitly asserted. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: ADD KEYRING, VALIDATE KEYRING, LIST KEYRING, CLEAR EMPTY KEYRING, LIST KEYRING 2, ADD KEY, LIST KEYRING WITH ONE, CLEAR KEYRING WITH ONE, LIST KEYRING 3, ADD FORTY KEYS, CHECK KEYRING CONTENTS, SHOW KEYRING, CLEAR KEYRING WITH MANY, LIST KEYRING 4, and 1 additional markers.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/clear/valid/runtest.sh` preserves the expected behavior for `keyctl clear` valid coverage for keyring clearing semantics. The explicit expected errors (`none explicitly asserted`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/clear/valid/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/describing/bad-args/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/describing/bad-args/runtest.sh

## Purpose

This shell test provides `keyctl describing` bad-args coverage for raw and pretty key description output. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: create_key, describe_key, expect_error, marker, pretty_describe_key, toolbox_report_result, unlink_key. Expected errno assertions are: EINVAL, ENOKEY. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: CHECK BAD KEY ID, CREATE KEY, UNLINK KEY, CHECK NON-EXISTENT KEY ID.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/describing/bad-args/runtest.sh` preserves the expected behavior for `keyctl describing` bad-args coverage for raw and pretty key description output. The explicit expected errors (`EINVAL, ENOKEY`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/describing/bad-args/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/describing/noargs/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/describing/noargs/runtest.sh

## Purpose

This shell test provides `keyctl describing` noargs coverage for raw and pretty key description output. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: expect_args_error, marker, toolbox_report_result. Expected errno assertions are: none explicitly asserted. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: NO ARGS, TWO ARGS, THREE ARGS.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/describing/noargs/runtest.sh` preserves the expected behavior for `keyctl describing` noargs coverage for raw and pretty key description output. The explicit expected errors (`none explicitly asserted`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/describing/noargs/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/describing/valid/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/describing/valid/runtest.sh

## Purpose

This shell test provides `keyctl describing` valid coverage for raw and pretty key description output. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: create_key, create_keyring, describe_key, expect_error, expect_key_rdesc, expect_keyring_rlist, list_keyring, marker, pretty_describe_key, revoke_key, set_key_perm, toolbox_report_result, unlink_key. Expected errno assertions are: EACCES, EKEYREVOKED. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: ADD KEYRING, VALIDATE KEYRING, VALIDATE PRETTY KEYRING, LIST KEYRING, ADD KEY, VALIDATE KEY, VALIDATE PRETTY KEY, DISABLE VIEW PERM, REINSTATE VIEW PERM, REVOKE KEY, UNLINK KEY.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/describing/valid/runtest.sh` preserves the expected behavior for `keyctl describing` valid coverage for raw and pretty key description output. The explicit expected errors (`EACCES, EKEYREVOKED`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/describing/valid/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/dh_compute/bad-args/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/dh_compute/bad-args/runtest.sh

## Purpose

This shell test provides `keyctl dh_compute` bad-args coverage for Diffie-Hellman and KDF keyctl operations. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: create_key, dh_compute, expect_error, marker, toolbox_report_result, toolbox_skip_test, unlink_key. Expected errno assertions are: ENOKEY, EOPNOTSUPP. Capability or environment gates are: have_dh_compute.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: CHECK WRONG KEY TYPE, CHECK MISSING KEY.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/dh_compute/bad-args/runtest.sh` preserves the expected behavior for `keyctl dh_compute` bad-args coverage for Diffie-Hellman and KDF keyctl operations. The explicit expected errors (`ENOKEY, EOPNOTSUPP`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/dh_compute/bad-args/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/dh_compute/noargs/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/dh_compute/noargs/runtest.sh

## Purpose

This shell test provides `keyctl dh_compute` noargs coverage for Diffie-Hellman and KDF keyctl operations. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: expect_args_error, marker, toolbox_report_result, toolbox_skip_test. Expected errno assertions are: none explicitly asserted. Capability or environment gates are: have_dh_compute.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: NO ARGS, TWO ARGS, FOUR ARGS.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/dh_compute/noargs/runtest.sh` preserves the expected behavior for `keyctl dh_compute` noargs coverage for Diffie-Hellman and KDF keyctl operations. The explicit expected errors (`none explicitly asserted`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/dh_compute/noargs/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/dh_compute/valid/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/dh_compute/valid/runtest.sh

## Purpose

This shell test provides `keyctl dh_compute` valid coverage for Diffie-Hellman and KDF keyctl operations. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: EOF, a328e894, a4cf1f93, b9059987, bdbf880b, c218396f, cc4624d5, cff8538c, create_key, dh_compute, e0b7f6c4, eb47c1a4, ebb82aeb, expect_multiline, f55b9a89, faa3b17c, marker, toolbox_report_result, and 1 more helpers. Expected errno assertions are: none explicitly asserted. Capability or environment gates are: have_dh_compute.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: LOAD SOURCE KEYS, COMPUTE DH PUBLIC KEY, LOAD SHA-256 SOURCE KEYS, COMPUTE DH SHARED SECRET, COMPUTE DERIVED KEY FROM DH SHARED SECRET (SHA-256), COMPUTE DERIVED KEY WITH LEADING ZEROS, LOAD SHA-224 SOURCE KEYS, COMPUTE DH SHARED SECRET, COMPUTE DERIVED KEY FROM DH SHARED SECRET (SHA-224).

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/dh_compute/valid/runtest.sh` preserves the expected behavior for `keyctl dh_compute` valid coverage for Diffie-Hellman and KDF keyctl operations. The explicit expected errors (`none explicitly asserted`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/dh_compute/valid/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/id/bad-args/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/id/bad-args/runtest.sh

## Purpose

This shell test provides `keyctl id` bad-args coverage for key ID lookup and special-name parsing. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: expect_error, id_key, marker, toolbox_report_result. Expected errno assertions are: EINVAL. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: CHECK BAD KEY ID, CHECK BAD IDS.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/id/bad-args/runtest.sh` preserves the expected behavior for `keyctl id` bad-args coverage for key ID lookup and special-name parsing. The explicit expected errors (`EINVAL`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/id/bad-args/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/id/noargs/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/id/noargs/runtest.sh

## Purpose

This shell test provides `keyctl id` noargs coverage for key ID lookup and special-name parsing. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: expect_args_error, marker, toolbox_report_result. Expected errno assertions are: none explicitly asserted. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: NO ARGS, TWO ARGS.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/id/noargs/runtest.sh` preserves the expected behavior for `keyctl id` noargs coverage for key ID lookup and special-name parsing. The explicit expected errors (`none explicitly asserted`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/id/noargs/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/id/valid/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/id/valid/runtest.sh

## Purpose

This shell test provides `keyctl id` valid coverage for key ID lookup and special-name parsing. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: create_key, create_keyring, expect_error, id_key, marker, toolbox_report_result, unlink_key. Expected errno assertions are: EINVAL, ENOKEY. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: CHECK STD IDS, CREATE KEYRING, CHECK NON-KEYRING KEY, UNLINK KEYRING, CHECK NON-EXISTENT KEYRING ID, CREATE KEY, CHECK NON-KEYRING KEY, UNLINK KEY, CHECK NON-EXISTENT KEY ID.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/id/valid/runtest.sh` preserves the expected behavior for `keyctl id` valid coverage for key ID lookup and special-name parsing. The explicit expected errors (`EINVAL, ENOKEY`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/id/valid/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/instantiating/bad-args/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/instantiating/bad-args/runtest.sh

## Purpose

This shell test provides `keyctl instantiating` bad-args coverage for instantiation of under-construction keys. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: create_key, expect_args_error, expect_error, instantiate_key, marker, negate_key, pinstantiate_key, reject_key, toolbox_report_result, unlink_key. Expected errno assertions are: EPERM. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: CHECK BAD KEY ID, CREATE KEY, CHECK ALREADY INSTANTIATED KEY, CHECK REJECT TIMEOUT, CHECK REJECT ERRORS, CHECK NEGATE TIMEOUT, UNLINK KEY, CHECK NON-EXISTENT KEY ID.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/instantiating/bad-args/runtest.sh` preserves the expected behavior for `keyctl instantiating` bad-args coverage for instantiation of under-construction keys. The explicit expected errors (`EPERM`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/instantiating/bad-args/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/instantiating/noargs/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/instantiating/noargs/runtest.sh

## Purpose

This shell test provides `keyctl instantiating` noargs coverage for instantiation of under-construction keys. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: expect_args_error, marker, toolbox_report_result. Expected errno assertions are: none explicitly asserted. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: NO ARGS, ONE ARG, TWO ARGS, THREE ARGS, FOUR ARGS.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/instantiating/noargs/runtest.sh` preserves the expected behavior for `keyctl instantiating` noargs coverage for instantiation of under-construction keys. The explicit expected errors (`none explicitly asserted`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/instantiating/noargs/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/invalidate/bad-args/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/invalidate/bad-args/runtest.sh

## Purpose

This shell test provides `keyctl invalidate` bad-args coverage for key invalidation behavior. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: create_key, expect_error, invalidate_key, marker, toolbox_report_result, toolbox_skip_test, unlink_key. Expected errno assertions are: EINVAL, ENOKEY. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: CHECK INVALIDATE BAD KEY ID, CREATE KEY, UNLINK KEY, CHECK INVALIDATE NON-EXISTENT KEY ID.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/invalidate/bad-args/runtest.sh` preserves the expected behavior for `keyctl invalidate` bad-args coverage for key invalidation behavior. The explicit expected errors (`EINVAL, ENOKEY`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/invalidate/bad-args/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/invalidate/noargs/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/invalidate/noargs/runtest.sh

## Purpose

This shell test provides `keyctl invalidate` noargs coverage for key invalidation behavior. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: expect_args_error, marker, toolbox_report_result, toolbox_skip_test. Expected errno assertions are: none explicitly asserted. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: NO ARGS, TWO ARGS.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/invalidate/noargs/runtest.sh` preserves the expected behavior for `keyctl invalidate` noargs coverage for key invalidation behavior. The explicit expected errors (`none explicitly asserted`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/invalidate/noargs/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/invalidate/valid/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/invalidate/valid/runtest.sh

## Purpose

This shell test provides `keyctl invalidate` valid coverage for key invalidation behavior. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: create_key, create_keyring, describe_key, expect_error, expect_keyring_rlist, invalidate_key, list_keyring, marker, sleep, toolbox_report_result, toolbox_skip_test. Expected errno assertions are: ENOKEY. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: ADD KEYRING, LIST KEYRING, ADD KEY, LIST KEYRING 2, INVALIDATE KEY, LIST KEYRING 3, ADD KEY, LIST KEYRING 4, INVALIDATE KEYRING, CHECK KEYRING, CHECK KEY.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/invalidate/valid/runtest.sh` preserves the expected behavior for `keyctl invalidate` valid coverage for key invalidation behavior. The explicit expected errors (`ENOKEY`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/invalidate/valid/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/link/bad-args/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/link/bad-args/runtest.sh

## Purpose

This shell test provides `keyctl link` bad-args coverage for link/unlink and keyring recursion behavior. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: create_key, expect_error, link_key, marker, toolbox_report_result, unlink_key. Expected errno assertions are: EINVAL, ENOKEY, ENOTDIR. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: CHECK LINK FROM BAD KEY ID, CHECK LINK TO BAD KEY ID, CREATE KEY, CHECK LINK TO NON-KEYRING KEY, UNLINK KEY, CHECK LINK TO NON-EXISTENT KEY ID, CHECK LINK FROM NON-EXISTENT KEY ID.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/link/bad-args/runtest.sh` preserves the expected behavior for `keyctl link` bad-args coverage for link/unlink and keyring recursion behavior. The explicit expected errors (`EINVAL, ENOKEY, ENOTDIR`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/link/bad-args/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/link/noargs/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/link/noargs/runtest.sh

## Purpose

This shell test provides `keyctl link` noargs coverage for link/unlink and keyring recursion behavior. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: expect_args_error, marker, toolbox_report_result. Expected errno assertions are: none explicitly asserted. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: NO ARGS, ONE ARGS, THREE ARGS.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/link/noargs/runtest.sh` preserves the expected behavior for `keyctl link` noargs coverage for link/unlink and keyring recursion behavior. The explicit expected errors (`none explicitly asserted`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/link/noargs/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/link/recursion/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/link/recursion/runtest.sh

## Purpose

This shell test provides `keyctl link` recursion coverage for link/unlink and keyring recursion behavior. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: create_keyring, expect_error, link_key, marker, set_key_perm, toolbox_report_result, unlink_key. Expected errno assertions are: EDEADLK, ELOOP. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: CREATE KEYRING 1, RECURSE 1, CREATE KEYRING 2, RECURSE 2, CREATE KEYRING 3, RECURSE 3, CREATE KEYRING 4, RECURSE 4, CREATE KEYRING 5, RECURSE 5, CREATE KEYRING 6, RECURSE 6, CREATE KEYRING 7, RECURSE 7, and 16 additional markers.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/link/recursion/runtest.sh` preserves the expected behavior for `keyctl link` recursion coverage for link/unlink and keyring recursion behavior. The explicit expected errors (`EDEADLK, ELOOP`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/link/recursion/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/link/valid/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/link/valid/runtest.sh

## Purpose

This shell test provides `keyctl link` valid coverage for link/unlink and keyring recursion behavior. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: create_key, create_keyring, describe_key, expect_error, expect_key_rdesc, expect_keyring_rlist, failed, link_key, list_keyring, marker, toolbox_report_result, unlink_key. Expected errno assertions are: ENOENT, ENOKEY. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: ADD KEYRING, VALIDATE KEYRING, LIST KEYRING, ADD KEY, LIST KEYRING WITH ONE, LINK KEY 1, CHECK KEY LINKAGE, LINK KEY 2, LINK KEY 3, COUNT LINKS, UNLINK KEY FROM SESSION, UNLINK KEY FROM KEYRING, LINK 2ND KEYRING TO SESSION, COUNT KEYRING LINKS, and 4 additional markers.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/link/valid/runtest.sh` preserves the expected behavior for `keyctl link` valid coverage for link/unlink and keyring recursion behavior. The explicit expected errors (`ENOENT, ENOKEY`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/link/valid/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/listing/bad-args/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/listing/bad-args/runtest.sh

## Purpose

This shell test provides `keyctl listing` bad-args coverage for raw and pretty keyring listing. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: create_key, expect_error, list_keyring, marker, pretty_list_keyring, toolbox_report_result, unlink_key. Expected errno assertions are: ENOKEY. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: CHECK BAD KEY ID, CREATE KEY, UNLINK KEY, CHECK NON-EXISTENT KEY ID.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/listing/bad-args/runtest.sh` preserves the expected behavior for `keyctl listing` bad-args coverage for raw and pretty keyring listing. The explicit expected errors (`ENOKEY`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/listing/bad-args/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/listing/noargs/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/listing/noargs/runtest.sh

## Purpose

This shell test provides `keyctl listing` noargs coverage for raw and pretty keyring listing. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: expect_args_error, marker, toolbox_report_result. Expected errno assertions are: none explicitly asserted. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: NO ARGS, TWO ARGS.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/listing/noargs/runtest.sh` preserves the expected behavior for `keyctl listing` noargs coverage for raw and pretty keyring listing. The explicit expected errors (`none explicitly asserted`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/listing/noargs/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/listing/valid/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/listing/valid/runtest.sh

## Purpose

This shell test provides `keyctl listing` valid coverage for raw and pretty keyring listing. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: create_key, create_keyring, describe_key, expect_error, expect_key_rdesc, expect_keyring_rlist, expect_payload, failed, list_keyring, marker, pretty_list_keyring, revoke_key, set_key_perm, toolbox_report_result, unlink_key. Expected errno assertions are: EACCES, EKEYREVOKED. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: ADD KEYRING, VALIDATE KEYRING, LIST KEYRING, PRETTY LIST KEYRING, ADD KEY, LIST KEYRING WITH ONE, PRETTY LIST KEYRING WITH ONE, ADD KEY 2, LIST KEYRING WITH TWO, PRETTY LIST KEYRING WITH TWO, DISABLE READ PERM, DISABLE SEARCH PERM, REINSTATE READ PERM, REVOKE KEYRING, and 1 additional markers.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/listing/valid/runtest.sh` preserves the expected behavior for `keyctl listing` valid coverage for raw and pretty keyring listing. The explicit expected errors (`EACCES, EKEYREVOKED`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/listing/valid/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/move/bad-args/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/move/bad-args/runtest.sh

## Purpose

This shell test provides `keyctl move` bad-args coverage for atomic key movement between keyrings. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: create_key, expect_error, marker, move_key, toolbox_report_result, unlink_key. Expected errno assertions are: EINVAL, ENOTDIR. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: CHECK MOVE OF BAD KEY ID, CHECK MOVE FROM BAD KEYRING ID, CHECK MOVE TO BAD KEYRING ID, CHECK FORCED MOVE OF BAD KEY ID, CHECK FORCED MOVE FROM BAD KEYRING ID, CHECK FORCED MOVE TO BAD KEYRING ID, CREATE KEY, CREATE KEY2, CHECK MOVE FROM NON-KEYRING KEY, CHECK MOVE TO NON-KEYRING KEY, UNLINK KEY, UNLINK KEY2.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/move/bad-args/runtest.sh` preserves the expected behavior for `keyctl move` bad-args coverage for atomic key movement between keyrings. The explicit expected errors (`EINVAL, ENOTDIR`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/move/bad-args/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/move/noargs/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/move/noargs/runtest.sh

## Purpose

This shell test provides `keyctl move` noargs coverage for atomic key movement between keyrings. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: expect_args_error, marker, toolbox_report_result. Expected errno assertions are: none explicitly asserted. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: NO ARGS, NO ARGS (F), ONE ARGS, ONE ARGS (F), TWO ARGS, TWO ARGS (F), FOUR ARGS, FOUR ARGS (F).

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/move/noargs/runtest.sh` preserves the expected behavior for `keyctl move` noargs coverage for atomic key movement between keyrings. The explicit expected errors (`none explicitly asserted`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/move/noargs/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/move/recursion/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/move/recursion/runtest.sh

## Purpose

This shell test provides `keyctl move` recursion coverage for atomic key movement between keyrings. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: create_keyring, expect_error, link_key, marker, move_key, set_key_perm, toolbox_report_result, unlink_key. Expected errno assertions are: EDEADLK, ELOOP. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: CREATE KEYRING 1, RECURSE 1, RECURSE 1F, CREATE KEYRING 2, RECURSE 2, RECURSE 2F, CREATE KEYRING 3, RECURSE 3, RECURSE 3F, CREATE KEYRING 4, RECURSE 4, RECURSE 4F, CREATE KEYRING 5, RECURSE 5, and 26 additional markers.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/move/recursion/runtest.sh` preserves the expected behavior for `keyctl move` recursion coverage for atomic key movement between keyrings. The explicit expected errors (`EDEADLK, ELOOP`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/move/recursion/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/move/valid/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/move/valid/runtest.sh

## Purpose

This shell test provides `keyctl move` valid coverage for atomic key movement between keyrings. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: create_key, create_keyring, expect_error, expect_keyring_rlist, failed, link_key, list_keyring, marker, move_key, toolbox_report_result, unlink_key. Expected errno assertions are: EEXIST, ENOENT, ENOKEY. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: ADD KEYRING, ADD KEY, LIST KEYRING WITH ONE, MOVE KEY 1, CHECK KEY LINKAGE, CHECK KEY REMOVED, MOVE KEY 2, FORCE MOVE KEY 2, MOVE KEY 3, MOVE KEY 4, ADD KEY 2, MOVE KEY 5, CHECK KEY UNMOVED, CHECK KEY UNDISPLACED, and 31 additional markers.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/move/valid/runtest.sh` preserves the expected behavior for `keyctl move` valid coverage for atomic key movement between keyrings. The explicit expected errors (`EEXIST, ENOENT, ENOKEY`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/move/valid/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/newring/bad-args/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/newring/bad-args/runtest.sh

## Purpose

This shell test provides `keyctl newring` bad-args coverage for keyring creation. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: clear_keyring, create_keyring, expect_error, marker, toolbox_report_result. Expected errno assertions are: EDQUOT, EINVAL. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: CHECK MAXLEN DESC, CHECK MAXLEN DESC FAILS WITH EDQUOT, CHECK OVERLONG DESC, CHECK EMPTY KEYRING NAME, CHECK BAD KEY ID.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/newring/bad-args/runtest.sh` preserves the expected behavior for `keyctl newring` bad-args coverage for keyring creation. The explicit expected errors (`EDQUOT, EINVAL`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/newring/bad-args/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/newring/noargs/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/newring/noargs/runtest.sh

## Purpose

This shell test provides `keyctl newring` noargs coverage for keyring creation. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: expect_args_error, marker, toolbox_report_result. Expected errno assertions are: none explicitly asserted. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: ADD NO ARGS, ADD ONE ARG, ADD THREE ARGS.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/newring/noargs/runtest.sh` preserves the expected behavior for `keyctl newring` noargs coverage for keyring creation. The explicit expected errors (`none explicitly asserted`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/newring/noargs/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/newring/valid/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/newring/valid/runtest.sh

## Purpose

This shell test provides `keyctl newring` valid coverage for keyring creation. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: create_keyring, describe_key, expect_error, expect_key_rdesc, expect_keyring_rlist, failed, list_keyring, marker, pause_till_key_destroyed, toolbox_report_result, unlink_key. Expected errno assertions are: ENOKEY. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: ADD KEYRING, LIST KEYRING, ADD KEYRING AGAIN, LIST SESSION KEYRING, VALIDATE NEW KEYRING, LIST SESSION KEYRING2, VALIDATE NEW KEYRING2, UNLINK KEY.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/newring/valid/runtest.sh` preserves the expected behavior for `keyctl newring` valid coverage for keyring creation. The explicit expected errors (`ENOKEY`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/newring/valid/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/noargs/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/noargs/runtest.sh

## Purpose

This shell test provides `keyctl keyctl` noargs coverage for keyutils command behavior. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../prepare.inc.sh, ../../toolbox.inc.sh. Important helper/API calls observed in the source include: expect_args_error, failed, marker, toolbox_report_result. Expected errno assertions are: none explicitly asserted. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: CHECK NO ARGS.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/noargs/runtest.sh` preserves the expected behavior for `keyctl keyctl` noargs coverage for keyutils command behavior. The explicit expected errors (`none explicitly asserted`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/noargs/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/padd/bad-args/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/padd/bad-args/runtest.sh

## Purpose

This shell test provides `keyctl padd` bad-args coverage for key creation with payloads read from stdin. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: clear_keyring, expect_error, marker, pcreate_key, toolbox_report_result. Expected errno assertions are: EDQUOT, EINVAL, ENODEV, EPERM. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: CHECK EMPTY KEY TYPE, CHECK UNSUPPORTED KEY TYPE, CHECK INVALID KEY TYPE, CHECK MAXLEN KEY TYPE, CHECK OVERLONG KEY TYPE, CHECK ADD KEYRING WITH PAYLOAD, CHECK MAXLEN DESC, CHECK MAXLEN DESC FAILS WITH EDQUOT, CHECK OVERLONG DESC, CHECK BAD KEY ID.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/padd/bad-args/runtest.sh` preserves the expected behavior for `keyctl padd` bad-args coverage for key creation with payloads read from stdin. The explicit expected errors (`EDQUOT, EINVAL, ENODEV, EPERM`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/padd/bad-args/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/padd/noargs/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/padd/noargs/runtest.sh

## Purpose

This shell test provides `keyctl padd` noargs coverage for key creation with payloads read from stdin. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: expect_args_error, marker, toolbox_report_result. Expected errno assertions are: none explicitly asserted. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: ADD NO ARGS, ADD ONE ARG, ADD TWO ARGS, ADD FOUR ARGS.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/padd/noargs/runtest.sh` preserves the expected behavior for `keyctl padd` noargs coverage for key creation with payloads read from stdin. The explicit expected errors (`none explicitly asserted`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/padd/noargs/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/padd/useradd/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/padd/useradd/runtest.sh

## Purpose

This shell test provides `keyctl padd` useradd coverage for key creation with payloads read from stdin. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: clear_keyring, expect_payload, keyutils_at_or_later_than, marker, md5sum_key, pcreate_key, pcreate_key_by_size, print_key, sleep, toolbox_report_result, unlink_key. Expected errno assertions are: none explicitly asserted. Capability or environment gates are: have_big_key_type.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: ADD USER KEY, PRINT PAYLOAD, ADD HEX USER KEY, PRINT PAYLOAD, UPDATE USER KEY, PRINT UPDATED PAYLOAD, UNLINK KEY, INCREASE QUOTA, ADD LARGE USER KEY, ADD SMALL BIG KEY, ADD HUGE BIG KEY, CLEAR KEYRING, RESET QUOTA.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/padd/useradd/runtest.sh` preserves the expected behavior for `keyctl padd` useradd coverage for key creation with payloads read from stdin. The explicit expected errors (`none explicitly asserted`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/padd/useradd/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/permitting/bad-args/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/permitting/bad-args/runtest.sh

## Purpose

This shell test provides `keyctl permitting` bad-args coverage for permission mask changes and access checks. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: chgrp_key, chown_key, create_key, expect_error, marker, set_key_perm, toolbox_report_result, unlink_key. Expected errno assertions are: EINVAL, ENOKEY. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: CHECK BAD KEY ID, CREATE KEY, CHECK PERMS, UNLINK KEY, CHECK CLEAR NON-EXISTENT KEY ID.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/permitting/bad-args/runtest.sh` preserves the expected behavior for `keyctl permitting` bad-args coverage for permission mask changes and access checks. The explicit expected errors (`EINVAL, ENOKEY`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/permitting/bad-args/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/permitting/noargs/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/permitting/noargs/runtest.sh

## Purpose

This shell test provides `keyctl permitting` noargs coverage for permission mask changes and access checks. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: expect_args_error, marker, toolbox_report_result. Expected errno assertions are: none explicitly asserted. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: NO ARGS, ONE ARG, THREE ARGS.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/permitting/noargs/runtest.sh` preserves the expected behavior for `keyctl permitting` noargs coverage for permission mask changes and access checks. The explicit expected errors (`none explicitly asserted`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/permitting/noargs/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/permitting/valid/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/permitting/valid/runtest.sh

## Purpose

This shell test provides `keyctl permitting` valid coverage for permission mask changes and access checks. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: chgrp_key, chown_key, create_key, create_keyring, describe_key, elif, expect_error, expect_key_rdesc, marker, set_key_perm, toolbox_report_result, unlink_key. Expected errno assertions are: EACCES, EOPNOTSUPP. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: ADD KEYRING, ADD KEY, CHOWN, CHOWN, CHOWN, CHOWN BACK, CHGRP, CHGRP, ITERATE PERMISSIONS, VIEW GROUP PERMISSIONS, VIEW OTHER PERMISSIONS, REMOVE SETATTR, REINSTATE SETATTR, UNLINK KEYRING.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/permitting/valid/runtest.sh` preserves the expected behavior for `keyctl permitting` valid coverage for permission mask changes and access checks. The explicit expected errors (`EACCES, EOPNOTSUPP`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/permitting/valid/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/pupdate/bad-args/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/pupdate/bad-args/runtest.sh

## Purpose

This shell test provides `keyctl pupdate` bad-args coverage for key payload update from stdin. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: create_key, expect_error, marker, toolbox_report_result, unlink_key. Expected errno assertions are: EINVAL, ENOKEY, EOPNOTSUPP. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: CHECK UPDATE SESSION KEYRING, CHECK UPDATE INVALID KEY, ADD USER KEY, UNLINK KEY, UPDATE UNLINKED KEY.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/pupdate/bad-args/runtest.sh` preserves the expected behavior for `keyctl pupdate` bad-args coverage for key payload update from stdin. The explicit expected errors (`EINVAL, ENOKEY, EOPNOTSUPP`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/pupdate/bad-args/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/pupdate/noargs/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/pupdate/noargs/runtest.sh

## Purpose

This shell test provides `keyctl pupdate` noargs coverage for key payload update from stdin. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: expect_args_error, marker, toolbox_report_result. Expected errno assertions are: none explicitly asserted. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: PUPDATE NO ARGS, PUPDATE TWO ARGS.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/pupdate/noargs/runtest.sh` preserves the expected behavior for `keyctl pupdate` noargs coverage for key payload update from stdin. The explicit expected errors (`none explicitly asserted`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/pupdate/noargs/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/pupdate/userupdate/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/pupdate/userupdate/runtest.sh

## Purpose

This shell test provides `keyctl pupdate` userupdate coverage for key payload update from stdin. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: create_key, expect_payload, marker, print_key, toolbox_report_result, unlink_key. Expected errno assertions are: none explicitly asserted. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: ADD USER KEY, PRINT PAYLOAD, PUPDATE USER KEY, PRINT UPDATED PAYLOAD, UNLINK KEY.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/pupdate/userupdate/runtest.sh` preserves the expected behavior for `keyctl pupdate` userupdate coverage for key payload update from stdin. The explicit expected errors (`none explicitly asserted`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/pupdate/userupdate/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/reading/bad-args/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/reading/bad-args/runtest.sh

## Purpose

This shell test provides `keyctl reading` bad-args coverage for key payload read/pipe/print behavior. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: create_key, expect_error, marker, pipe_key, print_key, read_key, toolbox_report_result, unlink_key. Expected errno assertions are: ENOKEY. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: CHECK BAD KEY ID, CREATE KEY, UNLINK KEY, CHECK CLEAR NON-EXISTENT KEY ID.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/reading/bad-args/runtest.sh` preserves the expected behavior for `keyctl reading` bad-args coverage for key payload read/pipe/print behavior. The explicit expected errors (`ENOKEY`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/reading/bad-args/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/reading/noargs/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/reading/noargs/runtest.sh

## Purpose

This shell test provides `keyctl reading` noargs coverage for key payload read/pipe/print behavior. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: expect_args_error, marker, toolbox_report_result. Expected errno assertions are: none explicitly asserted. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: NO ARGS, TWO ARGS.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/reading/noargs/runtest.sh` preserves the expected behavior for `keyctl reading` noargs coverage for key payload read/pipe/print behavior. The explicit expected errors (`none explicitly asserted`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/reading/noargs/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/reading/valid/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/reading/valid/runtest.sh

## Purpose

This shell test provides `keyctl reading` valid coverage for key payload read/pipe/print behavior. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: create_key, create_keyring, expect_error, expect_keyring_rlist, expect_payload, list_keyring, marker, pipe_key, print_key, read_key, revoke_key, set_key_perm, toolbox_report_result, unlink_key. Expected errno assertions are: EACCES, EKEYREVOKED. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: ADD KEYRING, ADD KEY, LIST KEYRING, PRINT KEY, PIPE KEY, READ KEY, READ KEYRING, REMOVE READ PERM, REMOVE SEARCH PERM, CHECK POSSESSOR READ, REINSTATE READ PERM, REVOKE KEY, UNLINK KEYRING.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/reading/valid/runtest.sh` preserves the expected behavior for `keyctl reading` valid coverage for key payload read/pipe/print behavior. The explicit expected errors (`EACCES, EKEYREVOKED`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/reading/valid/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/requesting/bad-args/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/requesting/bad-args/runtest.sh

## Purpose

This shell test provides `keyctl requesting` bad-args coverage for request_key and request-key helper callouts. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: expect_error, marker, prequest_key_callout, request_key, request_key_callout, toolbox_report_result. Expected errno assertions are: EINVAL, ENOKEY, EPERM. Capability or environment gates are: skip_install_required.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: SKIP BECAUSE TEST REQUIRES FULL INSTALL (for /sbin/request-key), CHECK EMPTY KEY TYPE, CHECK UNSUPPORTED KEY TYPE, CHECK INVALID KEY TYPE, CHECK MAXLEN INVALID KEY TYPE, CHECK OVERLONG KEY TYPE, CHECK MAXLEN DESC, CHECK OVERLONG DESC, CHECK MAXLEN CALLOUT, CHECK OVERLONG CALLOUT, CHECK MAXLEN PIPED CALLOUT, CHECK OVERLONG PIPED CALLOUT.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/requesting/bad-args/runtest.sh` preserves the expected behavior for `keyctl requesting` bad-args coverage for request_key and request-key helper callouts. The explicit expected errors (`EINVAL, ENOKEY, EPERM`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/requesting/bad-args/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/requesting/noargs/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/requesting/noargs/runtest.sh

## Purpose

This shell test provides `keyctl requesting` noargs coverage for request_key and request-key helper callouts. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: expect_args_error, marker, toolbox_report_result. Expected errno assertions are: none explicitly asserted. Capability or environment gates are: skip_install_required.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: SKIP BECAUSE TEST REQUIRES FULL INSTALL (for /sbin/request-key), NO ARGS, ONE ARG, TWO ARGS, FOUR ARGS, FIVE ARGS.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/requesting/noargs/runtest.sh` preserves the expected behavior for `keyctl requesting` noargs coverage for request_key and request-key helper callouts. The explicit expected errors (`none explicitly asserted`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/requesting/noargs/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/requesting/piped/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/requesting/piped/runtest.sh

## Purpose

This shell test provides `keyctl requesting` piped coverage for request_key and request-key helper callouts. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: create_key, create_keyring, expect_error, expect_keyring_rlist, list_keyring, marker, prequest_key_callout, request_key, set_gc_delay, toolbox_report_result, unlink_key. Expected errno assertions are: ENOKEY. Capability or environment gates are: skip_install_required.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: SKIP BECAUSE TEST REQUIRES FULL INSTALL (for /sbin/request-key), CREATE KEYRINGS, CHECK REQUEST FAILS, ADD USER KEY, REQUEST KEY, DETACH KEY FROM KEYRING, PIPED CALL OUT REQUEST KEY TO SESSION, CHECK ATTACHMENT TO SESSION KEYRING, REDO PIPED CALL OUT REQUEST KEY TO SESSION, DETACH KEY FROM SESSION, PIPED CALL OUT REQUEST KEY TO KEYRING, CHECK ATTACHMENT TO KEYRING, CHECK ATTACHMENT TO SESSION, REDO PIPED CALL OUT REQUEST KEY TO KEYRING, and 2 additional markers.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/requesting/piped/runtest.sh` preserves the expected behavior for `keyctl requesting` piped coverage for request_key and request-key helper callouts. The explicit expected errors (`ENOKEY`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/requesting/piped/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/requesting/valid/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/requesting/valid/runtest.sh

## Purpose

This shell test provides `keyctl requesting` valid coverage for request_key and request-key helper callouts. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: check_notify, create_key, create_keyring, expect_error, expect_keyring_rlist, list_keyring, marker, request_key, request_key_callout, set_gc_delay, toolbox_report_result, unlink_key. Expected errno assertions are: ENOKEY. Capability or environment gates are: skip_install_required.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: SKIP BECAUSE TEST REQUIRES FULL INSTALL (for /sbin/request-key), CREATE KEYRINGS, CHECK REQUEST FAILS, ADD USER KEY, REQUEST KEY, DETACH KEY FROM KEYRING, CALL OUT REQUEST KEY TO SESSION, CHECK ATTACHMENT TO SESSION KEYRING, REDO CALL OUT REQUEST KEY TO SESSION, DETACH KEY FROM SESSION, CALL OUT REQUEST KEY TO KEYRING, CHECK ATTACHMENT TO KEYRING, CHECK ATTACHMENT TO SESSION, REDO CALL OUT REQUEST KEY TO KEYRING, and 2 additional markers.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/requesting/valid/runtest.sh` preserves the expected behavior for `keyctl requesting` valid coverage for request_key and request-key helper callouts. The explicit expected errors (`ENOKEY`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/requesting/valid/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/restrict/bad-args/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/restrict/bad-args/runtest.sh

## Purpose

This shell test provides `keyctl restrict` bad-args coverage for keyring restriction policy and asymmetric trust chains. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: create_keyring, marker, restrict_keyring, toolbox_report_result, toolbox_skip_test. Expected errno assertions are: none explicitly asserted. Capability or environment gates are: have_restrict_keyring.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: ADD CA KEYRING, ADD KEYRING TO RESTRICT, INVALID EXTRA PARAMETER 1, INVALID EXTRA PARAMETER 2, INVALID RESTRICT METHOD, INVALID KEY TYPE, INVALID KEY ID, USE KEY ID 0 FOR KEYRING.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/restrict/bad-args/runtest.sh` preserves the expected behavior for `keyctl restrict` bad-args coverage for keyring restriction policy and asymmetric trust chains. The explicit expected errors (`none explicitly asserted`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/restrict/bad-args/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/restrict/valid/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/restrict/valid/runtest.sh

## Purpose

This shell test provides `keyctl restrict` valid coverage for keyring restriction policy and asymmetric trust chains. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: create_keyring, link_key, marker, pcreate_key, restrict_keyring, toolbox_report_result, toolbox_skip_test. Expected errno assertions are: none explicitly asserted. Capability or environment gates are: have_restrict_keyring.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: ADD CA KEYRING, ADD RESTRICTED USER KEYRING (parent keyring), REJECT RESTRICTION CYCLE, REJECT REPEATED RESTRICTION, ADD RESTRICTED BUILTIN KEYRING, ADD USER SIGNED CERT, REJECT KEY SIGNED BY UNKNOWN CA, REJECT KEY NOT SIGNED BY BUILTIN, ADD SECOND CA KEY, ADD RESTRICTED USER KEYRING (parent key), ADD KEY SIGNED BY KNOWN CA, REJECT SELF-SIGNED KEY, REJECT RESTRICTION CHANGE, ADD USER KEYRINGS (self), and 9 additional markers.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/restrict/valid/runtest.sh` preserves the expected behavior for `keyctl restrict` valid coverage for keyring restriction policy and asymmetric trust chains. The explicit expected errors (`none explicitly asserted`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/restrict/valid/runtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/revoke/bad-args/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/revoke/bad-args/runtest.sh

## Purpose

This shell test provides `keyctl revoke` bad-args coverage for key revocation error handling. It is one leaf in the keyutils testsuite and reports through the shared toolbox harness.

## Important APIs, Types, and Functions

The script sources: ../../../prepare.inc.sh, ../../../toolbox.inc.sh. Important helper/API calls observed in the source include: expect_error, marker, revoke_key, toolbox_report_result. Expected errno assertions are: EINVAL, ENOKEY. Capability or environment gates are: no explicit capability/install gate.

## Control Flow

The test initializes `result=PASS`, writes a begin line to `$OUTPUTFILE`, runs marked phases, calls `failed` through helper assertions on unexpected behavior, writes a finish line, and reports with `toolbox_report_result`. The main marked phases are: CHECK BAD KEY ID, CHECK NON-EXISTENT KEY ID.

## State and Persistence Behavior

State is intentionally kernel keyring state created for the test: temporary keys, keyrings, links, permissions, request-key authorizations, restrictions, or revocation/invalidation state depending on the scenario. Variables capture generated key IDs for later assertions and cleanup. Persistent filesystem output is limited to the harness output file; some feature/regression tests also inspect `/proc/keys`, audit logs, SELinux mode, or installed request-key policy.

## Dependencies and Integration Points

The script depends on `prepare.inc.sh` for feature/capability setup and `toolbox.inc.sh` for wrappers such as key creation, lookup, listing, error checking, and result reporting. It integrates with the `keyctl` CLI, libkeyutils, the kernel key retention service, and, when gated, SELinux, audit tooling, request-key installation, asymmetric key support, DH support, or keyring restriction support.

## Risks and Edge Cases

The assertions are sensitive to kernel version, key quota, active LSM policy, namespace/user identity, and whether keyutils was installed in the expected system paths. Tests that remove keys with `--wait` assume kernel garbage collection timing is compatible with the helper. Recursion and restriction tests deliberately construct invalid graph/trust states, so failures can leave temporary keyrings until the session ends.

## Test Signals

A passing run reaches `toolbox_report_result $TEST PASS` with all expected helper checks satisfied. The strongest signal from this file is that `sources/security-integrity/keyutils/tests/keyctl/revoke/bad-args/runtest.sh` preserves the expected behavior for `keyctl revoke` bad-args coverage for key revocation error handling. The explicit expected errors (`EINVAL, ENOKEY`) are useful regression signatures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/revoke/bad-args/runtest.sh -->

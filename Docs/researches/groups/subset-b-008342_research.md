# Research Report: subset-b-008342

Grouped source research for the subset-b-008342 work item. Each section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/pam_cap/capability.conf -->
# sources/security-integrity/libcap/pam_cap/capability.conf

Purpose: sample `/etc/security/capability.conf` for `pam_cap.so`, documenting how PAM module arguments and capability rules are meant to be used.

Important format and behavior: each non-comment rule begins with an IAB/capability text token such as `all`, `none`, `!cap_chown`, `^cap_setuid`, or comma-separated IAB entries, followed by user selectors. Selectors can be exact users, `*`, or groups with `@group`. The first matching rule wins in `pam_cap.c`, so rule order is security relevant.

State, dependencies, integration: the file is consumed by `pam_cap.c` through `read_capabilities_for_user()`. It relies on libcap text parsing for the first field and NSS group/user lookup for matching.

Risks and test signals: the sample defaults to `none *`, preventing unspecified users from inheriting prior IAB state. Tests in `test_pam_cap.c` exercise this file's beta, gamma, alpha, and delta matching order and IAB effects.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/pam_cap/capability.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/pam_cap/execable.c -->
# sources/security-integrity/libcap/pam_cap/execable.c

Purpose: gives the PAM shared object an executable entry point via `SO_MAIN()` so running `pam_cap.so` directly prints version and help text.

Important APIs/functions: includes `../libcap/execable.h`; `SO_MAIN(int argc, char **argv)` prints `LIBCAP_VERSION`, purpose text, documentation URLs, and optional `--help` module argument documentation. It accepts no functional PAM operations.

Control flow: default invocation prints identity and exits. With exactly `--help`, it also lists supported PAM stack arguments. Any other argument count or value exits with status 1.

State and dependencies: no persistent state; depends on libcap build macros and stdio. It integrates with the module build to provide self-description without loading PAM.

Risks and test signals: risk is documentation drift against `pam_cap.c::parse_args()`. The current help includes `debug`, `config=`, `keepcaps`, `autoauth`, `default=`, and `defer`, matching parser support.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/pam_cap/execable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/pam_cap/lazylink.c -->
# sources/security-integrity/libcap/pam_cap/lazylink.c

Purpose: build/link probe used to test whether the selected link flags support lazy linking for an executable shared object.

Important APIs/functions: declares unresolved `nothing_sets_this()` and defines `nothing_uses_this()` that calls it. The `SO_MAIN()` exits successfully without calling `nothing_uses_this()`.

Control flow: if lazy linking is available, the process can start and exit despite the unresolved symbol path being unused. If link/runtime resolution is eager in the tested configuration, the build or execution exposes that.

State and dependencies: no runtime state. Depends on `execable.h` and the linker/loader behavior under test.

Risks and test signals: intentional unresolved symbol usage can look suspicious to static analysis but is the point of the probe. A failure signals loader/linker assumptions for executable shared modules are not met.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/pam_cap/lazylink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/pam_cap/pam_cap.c -->
# sources/security-integrity/libcap/pam_cap/pam_cap.c

Purpose: PAM module that assigns inheritable, ambient, and bounding capability policy to users using libcap IAB text.

Important APIs/types/functions: `struct pam_cap_s` stores parsed module arguments. `load_groups()` gathers primary and supplemental group names. `read_capabilities_for_user()` scans the capability config and returns the first matching capability text. `set_capabilities()` parses and applies `cap_iab_t`, handling `all`, `none`, fallback defaults, `keepcaps`, and deferred application. PAM entry points are `pam_sm_authenticate()` and `pam_sm_setcred()`.

Control flow: authentication reads rules only to decide PAM success versus ignore unless `autoauth` is set. Credential establishment rereads the config, builds an IAB tuple, and either calls `cap_iab_set_proc()` immediately or stores it with `pam_set_data()` for `iab_apply()` during `pam_end()`.

State and dependencies: uses NSS, PAM, syslog, libcap, `prctl(PR_SET_KEEPCAPS)`, and config file metadata. It zeroes config/group strings before free.

Risks and test signals: first-match rule order, redundant auth/setcred reads, NSS failures, deferred cleanup semantics, and config permissions are key risks. It rejects world-writable config files except `/dev/null`. `test_pam_cap.c` covers parser flags, group matching, no-user `PAM_INCOMPLETE`, fallback, and capability vector changes.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/pam_cap/pam_cap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/pam_cap/sudotest.conf -->
# sources/security-integrity/libcap/pam_cap/sudotest.conf

Purpose: test configuration for privileged `pam_cap` scenarios, not a system default.

Important format and behavior: contains ordered rules for root and test users. `all root` preserves root IAB state. Specific rules exercise bounding drops (`!cap_chown`), inheritable additions (`cap_setuid,cap_chown`), group matching with `@three` and `@one`, invalid non-group prefix `+one`, and ambient/inheritable markers with `^`.

Control flow/integration: consumed by `pam_cap.c` when a test passes `config=./sudotest.conf` or equivalent. The first matching rule wins, so comments explicitly mark rules that should or should not fire.

State and dependencies: no runtime state; depends on the test harness' synthetic user/group map.

Risks and test signals: verifies rule ordering and group selector precedence. A change here can invalidate expected bitmasks in `test_pam_cap.c` and sudo-style integration tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/pam_cap/sudotest.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/pam_cap/test.c -->
# sources/security-integrity/libcap/pam_cap/test.c

Purpose: minimal smoke test for the PAM module authentication entry point.

Important APIs/functions: includes PAM headers and calls `pam_sm_authenticate(NULL, 0, 0, NULL)`, expecting `PAM_SUCCESS`.

Control flow: if the module call does not return success, it prints a failure and exits 1; otherwise exits 0.

State and dependencies: no persistent state. It links against the PAM module entry point and relies on the module's no-argument behavior in the build/test context.

Risks and test signals: because it uses a null PAM handle and no module arguments, it is only a narrow ABI/smoke signal. More complete behavior is covered by `test_pam_cap.c`.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/pam_cap/test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/pam_cap/test_pam_cap.c -->
# sources/security-integrity/libcap/pam_cap/test_pam_cap.c

Purpose: inline unit/integration test for `pam_cap.c` using synthetic PAM, passwd, and group functions.

Important APIs/functions: stubs `pam_get_user()`, `pam_get_item()`, `pam_set_data()`, `getgrouplist()`, `getgrgid()`, and `getpwnam()` to control identities. `load_vectors()` captures ambient, bounding, and inheritable low 64-bit state. `test_arg_parsing()` validates every supported module option.

Control flow: performs non-privileged parser/config smoke tests first, clears inheritable state, skips privileged vector tests unless UID 0, then runs auth and setcred for a selected user and compares observed A/B/I vectors against command-line expectations.

State and dependencies: mutates real process capabilities for privileged tests and uses libcap APIs. Static globals hold current synthetic user and group/passwd records.

Risks and test signals: catches config matching order, unknown user handling, `/dev/null` no-policy behavior, no-user `PAM_INCOMPLETE`, IAB parsing/application, and fallback behavior. Deferred `pam_set_data()` is stubbed to fail after freeing data, so success of deferred application itself is not proven here.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/pam_cap/test_pam_cap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/progs/Makefile -->
# sources/security-integrity/libcap/progs/Makefile

Purpose: builds libcap command-line utilities: `getpcaps`, `getcap`, `setcap`, and `capsh`.

Important targets: `all`, `install`, `test`, `sudotest`, `clean`, `capshdoc.c.cf`, `capsh`, `tcapsh-static`, and `uns_test`. It supports dynamic, full static, and mostly-static libcap linkage through `DYNAMIC`, `LIBCSTATIC`, `LDFLAGS`, `LDFLAGS_SUFFIX`, and `DEPS`.

Control flow: ensures `../libcap/libcap.{a,so}` exists, compiles objects, links utilities, regenerates `capshdoc.c.cf` with `mkcapshdoc.sh` and diffs it against checked-in `capshdoc.c`, then builds static `tcapsh-static` for chroot/test use.

State and dependencies: consumes `Make.Rules`, libcap library artifacts, capsh documentation sources, and sudo for `sudotest`.

Risks and test signals: documentation generation drift fails the build. Static glibc limitations are called out. `sudotest` drives `quicktest.sh`, covering privileged capability behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/progs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/progs/capsh.c -->
# sources/security-integrity/libcap/progs/capsh.c

Purpose: multifunction capability shell/diagnostic launcher used by users and by libcap's privileged test suite.

Important APIs/functions: helpers parse numbers, print process/IAB/securebits state, drop bounding bits, edit ambient bits, locate `capsh` in `PATH`, describe capabilities from `capshdoc.c`, and launch commands via `cap_launch()`. Main option handling covers `--caps`, `--inh`, `--iab`, `--drop`, `--addamb`, `--delamb`, `--mode`, `--secbits`, `--keep`, uid/gid/group changes, chroot, `--no-new-privs`, assertions, explain/suggest, shell exec, and cap-launch paths.

Control flow: options are processed sequentially, so earlier capability or identity changes affect later operations. `--`, `==`, `-+`, and `=+` replace the process with a shell or re-execed `capsh`, optionally through `cap_launch()`.

State and dependencies: mutates process capabilities, IAB, ambient set, securebits, uid/gid/groups, environment, chroot, and child processes. Depends on libcap, prctl, NSS, wait/fork/exec, and generated doc arrays.

Risks and test signals: option order is security relevant. Non-strict mode temporarily raises `CAP_SETPCAP` or `CAP_SYS_CHROOT`; failures restore only by process exit. `quicktest.sh` heavily exercises mode transitions, bounding/ambient semantics, chroot, namespace file caps, and assertion options.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/progs/capsh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/progs/capshdoc.c -->
# sources/security-integrity/libcap/progs/capshdoc.c

Purpose: checked-in generated data table containing text explanations for Linux capability numbers used by `capsh --explain` and `--suggest`.

Important APIs/types: defines one `static const char *explanationN[]` array per capability and exports `const char **explanations[]` plus `const int capsh_doc_limit`.

Control flow/integration: no executable control flow beyond static initialization. `capsh.c::describe()` indexes this table after `cap_from_name()` and prints the lines. `mkcapshdoc.sh` regenerates the file from `../doc/values/*.txt` and capability names, and the Makefile diffs generated output against this checked-in copy.

State and dependencies: no runtime mutation. Depends on alignment with `cap_names.list.h` and documentation value files.

Risks and test signals: stale or misordered entries produce misleading privilege explanations. The build target `capshdoc.c.cf` is the primary drift detector.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/progs/capshdoc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/progs/capshdoc.h -->
# sources/security-integrity/libcap/progs/capshdoc.h

Purpose: small include guard and external declarations for the generated `capshdoc.c` data.

Important APIs/types: declares `extern const char **explanations[];` and `extern const int capsh_doc_limit;`.

Control flow/state: no control flow or persistent state. The guard prevents accidental multiple inclusion under `CAPSHDOC`.

Dependencies and integration: included by both `capsh.c` and `capshdoc.c`; consumers use `capsh_doc_limit` to avoid indexing beyond generated capability documentation.

Risks and test signals: declaration/type mismatch with `capshdoc.c` would be caught by compilation. Semantic drift is checked by `mkcapshdoc.sh` via the Makefile.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/progs/capshdoc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/progs/getcap.c -->
# sources/security-integrity/libcap/progs/getcap.c

Purpose: command-line tool to display file capability xattrs.

Important APIs/functions: option parser supports `-r`, `-v`, `-n`, `-h`, and `-l`. `do_getcap()` is used directly or via `nftw()` to inspect regular files with `cap_get_file()`, render via `cap_to_text()`, and optionally print namespace root owner via `cap_get_nsowner()`.

Control flow: each argument is `lstat()`ed. Recursive mode walks physical files; non-recursive mode maps stat type to an FTW-like flag. Missing caps are silent except under verbose mode.

State and dependencies: global flags hold verbosity, recursion, and namespace display. Depends on libcap and filesystem traversal.

Risks and test signals: symlink and non-regular files are deliberately not treated as targets. Recursive traversal errors are reported but do not stop the full scan. `quicktest.sh` validates namespace file-cap display with `getcap -n`.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/progs/getcap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/progs/getpcaps.c -->
# sources/security-integrity/libcap/progs/getpcaps.c

Purpose: displays capability state for one or more process IDs.

Important APIs/functions: parses long-form options `--help`, `--verbose`, `--ugly`/`--legacy`, `--iab`, and `--license`. For each PID, it uses `cap_get_pid()`, `cap_to_text()`, and optionally `cap_iab_get_pid()`/`cap_iab_to_text()` to print process capability and IAB state.

Control flow: arguments are processed sequentially; options update local output mode and PID tokens are parsed with `strtol()` with overflow and trailing-character checks.

State and dependencies: no persistent state. Depends on libcap's process capability APIs and `/proc`/kernel support.

Risks and test signals: process disappearance and permission failures produce nonzero exit status. Legacy format support is preserved for old scripts. `quicktest.sh` uses it to verify shell scripts do not unexpectedly receive file capabilities.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/progs/getpcaps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/progs/mkcapshdoc.sh -->
# sources/security-integrity/libcap/progs/mkcapshdoc.sh

Purpose: generator for `capshdoc.c`.

Important operations: emits C includes and comments, iterates `../doc/values/${x}.txt` in numeric order, derives capability names from `../libcap/cap_names.list.h`, escapes quotes with `sed`, writes `explanationN` arrays, then emits `explanations[]` and `capsh_doc_limit`.

Control flow: sequential numeric loop stops at first missing `values/N.txt`; a second loop emits the pointer table for all generated arrays.

State and dependencies: depends on Bash, grep, sed, doc value files, and cap name list format. It writes to stdout; the Makefile redirects to a `.cf` comparison file.

Risks and test signals: brittle parsing of `cap_names.list.h` and doc file ordering can mislabel docs. The Makefile `diff -u capshdoc.c capshdoc.c.cf` is the explicit guard.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/progs/mkcapshdoc.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/progs/old/execcap.c -->
# sources/security-integrity/libcap/progs/old/execcap.c

Purpose: legacy wrapper that sets the current process capabilities from text and then execs another command.

Important APIs/functions: `usage()` documents that it is not safe as setuid-root. `main()` rejects setuid-root use, parses `argv[1]` with `cap_from_text()`, applies it with `cap_set_proc()`, then `execvp()`s `argv[2:]`.

Control flow: any validation, parse, or capability set failure prints an error and exits through usage. Successful `execvp()` never returns.

State and dependencies: mutates current process capability sets and inherits all environment variables into the target. Depends on libcap and exec semantics.

Risks and test signals: old example code lacks modern IAB/ambient/bounding handling and intentionally warns against setuid deployment. It is best treated as historical sample code, not a hardened launcher.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/progs/old/execcap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/progs/old/setpcaps.c -->
# sources/security-integrity/libcap/progs/old/setpcaps.c

Purpose: legacy example that sets capabilities on running processes using the old `capsetp()` interface.

Important APIs/functions: `read_caps()` reads capability text from stdin when `-` is used. `main()` supports `-q`, parses capability text with `cap_from_text()`, prints the decoded set in debug-disabled builds, parses PID with `atoi()`, and calls `capsetp(pid, cap_d)`.

Control flow: arguments are consumed as repeated capability/PID pairs. Parse or set failures call `usage()`.

State and dependencies: mutates other processes' capabilities when permitted by the kernel and caller's `CAP_SETPCAP` context. Depends on obsolete libcap process APIs.

Risks and test signals: unsafe by design as an example; PID parsing is weak, and modern kernels restrict arbitrary process capability mutation. The usage text states no safe use of `CAP_SETPCAP` had been demonstrated for this pattern.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/progs/old/setpcaps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/progs/old/sucap.c -->
# sources/security-integrity/libcap/progs/old/sucap.c

Purpose: legacy wrapper that changes UID/GID while trying to preserve privileges for a subsequent exec.

Important APIs/functions: `wait_on_fd()` synchronizes over a pipe. `main()` rejects setuid-root use, reads current caps with `capgetp()`, forks, has the parent drop groups and switch gid/uid, then has the child restore the parent's capabilities with `capsetp(parent_pid, old_caps)` before the parent execs the target.

Control flow: parent and child coordinate through pipe close/read and `wait()`. The child performs cross-process capability mutation after the parent changes identity.

State and dependencies: mutates uid/gid/groups and capabilities across related processes. Depends on old libcap APIs, fork, pipes, passwd/group lookup, and exec.

Risks and test signals: intentionally historical and risky; asynchronous privilege restoration is fragile and not a modern safe pattern. The file is useful for understanding pre-file-capability workarounds.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/progs/old/sucap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/progs/quicktest.sh -->
# sources/security-integrity/libcap/progs/quicktest.sh

Purpose: privileged integration test script for `capsh`, `setcap`, `getcap`, `getpcaps`, namespace file capabilities, ambient capabilities, securebits, chroot, and kernel bug probes.

Important functions: `try_capsh`, `fail_capsh`, and `pass_capsh` standardize expected pass/fail assertions. The script builds local test binaries, manipulates file capabilities, creates symlinks and shell scripts, and runs `uns_test`.

Control flow: starts with basic `capsh` state checks and re-exec path checks, then tests libcap modes, setuid/keepcaps flows, securebits, bounding set behavior, inheritable and ambient capabilities, chroot, namespace rootid file caps, optional Go binary checks, and a user namespace exploit regression.

State and dependencies: requires root-like privilege, sudo, working build products, filesystem xattrs, user `nobody`, and kernel support for tested features.

Risks and test signals: it mutates local files and capabilities, so it must run in the build directory. Fail/pass inversion is deliberate for negative tests. It is the highest-level test signal for `capsh` behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/progs/quicktest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/progs/setcap.c -->
# sources/security-integrity/libcap/progs/setcap.c

Purpose: command-line tool to set, remove, or verify file capabilities.

Important APIs/functions: `pos_uint()` parses namespace root IDs. `read_caps()` reads cap text from stdin. `main()` handles `--license`, `-f`, `-h`, `-n`, `-q`, `-v`, `-r`, `-`, and repeated cap/file pairs. It uses `cap_from_text()`, `cap_set_nsowner()`, `cap_set_file()`, `cap_get_file()`, `cap_compare()`, and `cap_get_nsowner()`.

Control flow: before writing, it raises effective `CAP_SETFCAP` once from the process capability set. Verification compares both capability vectors and rootid. Linux-specific validation rejects effective file capabilities that are not empty or equal to permitted/inheritable union unless `-f` is used.

State and dependencies: mutates filesystem security xattrs and process effective caps. Depends on libcap, kernel file cap support, and regular files.

Risks and test signals: empty whitespace is rejected to avoid accidental clears; symlink removal is expected to fail in `quicktest.sh`. Namespace rootid support is validated by `quicktest.sh`.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/progs/setcap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/psx/doc.go -->
# sources/security-integrity/libcap/psx/doc.go

Purpose: package-level Go documentation for `kernel.org/pub/linux/libs/security/libcap/psx`.

Important APIs described: `Syscall3` and `Syscall6` execute security-relevant syscalls on all threads. Documentation distinguishes non-cgo Go 1.16+ wrappers around `syscall.AllThreadsSyscall*` from cgo wrappers around C libpsx.

Control flow/integration: not executable beyond package declaration, but documents expected behavior: first thread performs syscall, failure returns immediately, success stops/synchronizes runtime so remaining threads perform it.

State and dependencies: explains dependency on Linux thread privilege semantics, Go runtime thread migration, cgo, and libpsx.

Risks and test signals: warns older Go toolchains may hang. The central risk is using regular syscalls for privilege drops in a multithreaded Go process. Tests in `psx_test.go`, `psx_cgo_test.go`, and churn tests cover this contract.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/psx/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/psx/libpsx.h -->
# sources/security-integrity/libcap/psx/libpsx.h

Purpose: private header for the C PSX implementation.

Important APIs/types: defines `_psx_gettid()`, `_psx_sched_yield()`, atomic spinlock macros, `psx_tracker_state_t`, `psx_thread_ref_t`, and `psx_tracker_t`. Declares hidden coordination functions `psx_lock()`, `psx_unlock()`, `psx_cond_wait()`, `psx_mix()`, `psx_actions_size()`, and `psx_confirm_sigaction()`.

Control flow/state model: `psx_tracker_t` is the global state machine for a process, tracking PID, `/proc/<pid>/task` path, current state, signal number, active syscall command, handler action storage, thread hash map, and mismatch sensitivity.

Dependencies and integration: included by `psx.c` and `psx_calls.c`; it deliberately keeps signal action internals opaque because `psx_calls.c` uses raw kernel layouts.

Risks and test signals: custom spinlock/yield behavior and hash map collision expansion are concurrency-sensitive. The tests stressing thread churn, fork, and cgo errno expose regressions.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/psx/libpsx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/psx/psx.c -->
# sources/security-integrity/libcap/psx/psx.c

Purpose: C implementation of process-wide syscall synchronization for Linux threads, used to preserve POSIX-like privilege semantics.

Important APIs/functions: exports `psx_load_syscalls()`, `psx_syscall3()`, `psx_syscall6()`, `__psx_syscall()`, and `psx_set_sensitivity()`. Internal helpers initialize tracker state, allocate the thread map, manage state transitions, run immediate syscalls, scan `/proc/<pid>/task` with raw `getdents64`, and clean up at exit.

Control flow: `__psx_syscall()` validates argument count, enters setup, confirms the signal handler, runs the syscall on the caller, aborts fan-out if it fails, then enters syscall state, signals every other thread with hidden signal 33, waits for two complete no-pending sweeps, blocks until handlers finish, handles mismatched return values by sensitivity, restores errno, and returns the caller result.

State and dependencies: global `psx_tracker` stores PID, state, active command, handler actions, thread map, and incomplete count. It depends on raw syscalls, `/proc`, signals, atomics, and libpsx private headers.

Risks and test signals: signal 33 interposition, thread creation races, map collisions, fork inheritance, errno preservation, and deadlocks are main risks. Go and C tests cover thread sharing, churn, forks, cgo errno, and exploit prevention.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/psx/psx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/psx/psx.go -->
# sources/security-integrity/libcap/psx/psx.go

Purpose: non-cgo Go implementation of the psx package for Linux Go 1.16+.

Important APIs/functions: `Syscall3()` delegates to `syscall.AllThreadsSyscall()`, and `Syscall6()` delegates to `syscall.AllThreadsSyscall6()`. Build tags require `linux && !cgo && go1.16`.

Control flow: each wrapper directly returns Go's all-thread syscall result tuple. The file contains documentation aligning behavior with cgo mode while avoiding C linkage.

State and dependencies: no persistent package state. Depends on Go runtime support for all-thread syscalls and the `syscall` package.

Risks and test signals: limited to Go versions and Linux runtime semantics. Tests in `psx_test.go` and `psx_churn_test.go` exercise PID/error behavior and shared keepcaps state across goroutines/threads.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/psx/psx.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/psx/psx_calls.c -->
# sources/security-integrity/libcap/psx/psx_calls.c

Purpose: low-level signal-handler installation and actor code for libpsx, isolated because it needs raw kernel sigaction layouts.

Important APIs/functions: defines architecture-specific `struct sigaction` compatibility, `psx_actions_t`, `psx_actions_size()`, `psx_posix_syscall_actor()`, and `psx_confirm_sigaction()`. Provides raw `rt_sigprocmask` and `rt_sigaction` wrappers and optional `SA_RESTORER` assembly trampolines.

Control flow: `psx_confirm_sigaction()` blocks the PSX signal, reads existing handler, chains it, installs `psx_posix_syscall_actor()` first, then restores the signal mask. The actor ignores unrelated signals by forwarding to the chained handler. For real PSX signals, it performs the active syscall, records retval/pending in the thread map, waits for command deactivation, decrements incomplete, and returns.

State and dependencies: uses global `psx_tracker`, raw `syscall()`, hidden signal 33, kernel signal ABI knowledge, and per-thread TIDs.

Risks and test signals: architecture ABI mismatch, handler chaining, signal races, and async-signal-safety are key risks. Thread churn and cgo tests stress the handler installation and fan-out.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/psx/psx_calls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/psx/psx_cgo.go -->
# sources/security-integrity/libcap/psx/psx_cgo.go

Purpose: cgo Go binding to the C libpsx all-thread syscall implementation.

Important APIs/functions: C helper `__errno_too()` reads/sets thread-local errno. Go `setErrno()` supports tests, `forceFatal()` sets `PSX_ERROR` sensitivity once, and `Syscall3()`/`Syscall6()` call `C.psx_syscall3/6`.

Control flow: each syscall wrapper forces fatal mismatch mode, locks the current goroutine to its OS thread to preserve errno association, calls the C function, and converts negative results into `syscall.Errno` using the C errno helper.

State and dependencies: package-level `sync.Once` controls sensitivity setup. Depends on cgo, `psx_syscall.h`, Go runtime thread locking, and C libpsx.

Risks and test signals: errno preservation and thread affinity are the core risks. A mismatch in C return behavior kills the program under PSX_ERROR. `psx_cgo_test.go` validates errno is preserved across successful calls and set on failure.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/psx/psx_cgo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/psx/psx_cgo_test.go -->
# sources/security-integrity/libcap/psx/psx_cgo_test.go

Purpose: cgo-specific errno regression test for Go psx wrappers.

Important APIs/functions: `TestErrno()` locks the OS thread, seeds C errno with `EPERM`, calls `Syscall3()` and `Syscall6()` with `SYS_GETUID`, compares return values, then verifies the original errno remains unchanged after successful syscalls.

Control flow: setup and cleanup happen under `runtime.LockOSThread()`, ensuring `setErrno()` and C calls refer to the same thread-local errno.

State and dependencies: mutates C errno for the locked thread. Depends on cgo build, syscall numbers, and psx wrappers.

Risks and test signals: catches accidental errno clobbering in the C bridge and mismatched 3-argument versus 6-argument behavior. It does not test failure errno directly beyond the helper semantics.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/psx/psx_cgo_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/psx/psx_churn_test.go -->
# sources/security-integrity/libcap/psx/psx_churn_test.go

Purpose: Go regression test for PSX behavior during thread churn, especially around Go issue 42494.

Important APIs/functions: `TestThreadChurn()` loops through combinations of killing locked OS threads and issuing PSX `prctl(PR_SET_KEEPCAPS)` syscalls.

Control flow: for each mode, it counts down from 50; optionally starts a goroutine that locks to an OS thread and exits after channel close, and optionally performs an all-thread keepcaps syscall.

State and dependencies: mutates process keepcaps state and relies on Go runtime thread creation/destruction. Uses `killAThread()` from `psx_test.go`.

Risks and test signals: catches hangs, missed threads, or signal/runtime conflicts when threads appear/disappear during PSX operations. This is a concurrency stress signal rather than a semantic capability comparison.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/psx/psx_churn_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/psx/psx_syscall.h -->
# sources/security-integrity/libcap/psx/psx_syscall.h

Purpose: public C header for libpsx syscall synchronization.

Important APIs/types: defines `LIBPSX_MAJOR`, `LIBPSX_MINOR`, variadic macro `psx_syscall()`, functions `__psx_syscall()`, `psx_syscall3()`, `psx_syscall6()`, `psx_load_syscalls()`, enum `psx_sensitivity_t`, and `psx_set_sensitivity()`.

Control flow/integration: macro appends sentinel argument counts so `__psx_syscall()` can infer 0-6 supplied arguments. Function-pointer consumers can use fixed 3- and 6-argument wrappers. `psx_load_syscalls()` supports weak-symbol override in libraries such as libcap.

State and dependencies: no state in the header; declares process-wide behavior implemented by `psx.c`.

Risks and test signals: variadic macro cannot be used as a function pointer, and callers should avoid using PSX for read-only syscalls. Version and sensitivity contracts are checked indirectly by C and Go tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/psx/psx_syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/psx/psx_test.go -->
# sources/security-integrity/libcap/psx/psx_test.go

Purpose: Go tests for psx syscall wrappers in cgo and non-cgo builds.

Important APIs/functions: `TestSyscall3()` and `TestSyscall6()` validate `GETPID` success and malformed `CAPGET` failure errno. `killAThread()` creates an OS-thread churn helper. `TestShared()` repeatedly toggles `PR_SET_KEEPCAPS`, starts locked-thread trackers, and verifies all trackers observe the new state.

Control flow: `TestShared()` serializes tracker goroutines through channels so each reads keepcaps after each process-wide change.

State and dependencies: mutates process keepcaps and creates locked OS threads. Depends on syscall constants and package `Syscall3/6`.

Risks and test signals: catches wrapper return-value handling, errno mapping, all-thread state propagation, and runtime thread migration regressions.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/psx/psx_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/psx/wrap/psx_wrap.c -->
# sources/security-integrity/libcap/psx/wrap/psx_wrap.c

Purpose: weak wrapper support for legacy `-Wl,--wrap=pthread_create` linkage.

Important APIs/functions: declares `__real_pthread_create()` and `__wrap_pthread_create()`. Defines weak `__real_pthread_create()` that checks whether it incorrectly resolves to the wrapper and otherwise calls `pthread_create()`.

Control flow: if wrapper linkage is wrong and `pthread_create` equals `__wrap_pthread_create`, it prints an error and exits 1. Otherwise it delegates to `pthread_create`.

State and dependencies: no persistent state. Depends on pthreads and linker wrap behavior.

Risks and test signals: mainly protects against mislinked legacy libpsx builds. Modern libpsx no longer requires pthread wrapping, but compatibility builds can catch configuration errors here.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/psx/wrap/psx_wrap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/template.c -->
# sources/security-integrity/libcap/template.c

Purpose: skeleton C source template with copyright and placeholder content.

Important APIs/functions: none; it contains only a comment block with `<Author>` and `<Content>` placeholders.

Control flow/state/dependencies: no executable code, no state, and no dependencies.

Integration points: likely used manually when adding new libcap C files, not referenced by build logic in the researched subset.

Risks and test signals: risk is only accidental inclusion in a build without real implementation. No tests target this file.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/template.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/tests/Makefile -->
# sources/security-integrity/libcap/tests/Makefile

Purpose: builds and runs libcap/libpsx C test programs.

Important targets: unprivileged `run_psx_test`, `run_libcap_psx_test`; privileged `run_uns_test`, `run_libcap_launch_test`, `run_libcap_psx_launch_test`, `run_exploit_test`; dynamic shared bug test `run_b219174`; build targets for `noop`, `exploit`, `noexploit`, `weaver.so`, and `b219174`.

Control flow: test target runs PSX tests when `PTHREADS=yes`; `sudotest` adds privileged tests under sudo. Linkage switches between static and dynamic libcap/libpsx, with rpath for dynamic tests.

State and dependencies: depends on `../libcap` artifacts, `../progs/tcapsh-static`, pthreads, sudo, dlopen for b219174, and build variables.

Risks and test signals: library order for `noexploit` is security relevant. The suite distinguishes vulnerable libcap-only threading from protected libpsx-linked behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/tests/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/tests/b219174.c -->
# sources/security-integrity/libcap/tests/b219174.c

Purpose: regression test for kernel bug 219174 involving PSX and threads created from a dynamically loaded shared object.

Important APIs/functions: uses `dlopen()`/`dlsym()` to load `weaver.so` functions, then repeatedly calls `psx_syscall6(SYS_prctl, PR_SET_KEEPCAPS, ...)` while adding threads through the shared object.

Control flow: after `weaver_setup()`, it launches 37 threads one by one. After each PSX keepcaps toggle and new thread creation, it asks `weaver_waitforit()` for an aggregate result and compares against expected totals that encode each thread's observed keepcaps state.

State and dependencies: mutates keepcaps process state, dynamically loads `weaver.so`, creates pthreads, and uses libpsx.

Risks and test signals: catches cases where PSX misses threads created by a library not itself linked against libpsx. Failure indicates thread discovery or signal fan-out is incomplete.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/tests/b219174.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/tests/exploit.c -->
# sources/security-integrity/libcap/tests/exploit.c

Purpose: demonstrates why libcap alone is unsafe for privilege dropping in multithreaded programs, and why libpsx is needed.

Important APIs/functions: creates a victim pthread, drops capabilities only in the main thread with `cap_set_proc(cap_init())`, installs a signal handler, sends the victim `SIGRTMIN`, and records the largest capability text observed by the handler.

Control flow: the victim starts privileged and waits. Main drops its caps, confirms its own text length is 1, then signal-interrupts the victim. If the handler sees a larger capability set, the exploit succeeded and exits 1; otherwise exits 0.

State and dependencies: uses pthread synchronization, signal handlers, libcap capability reads, and process/thread privilege state.

Risks and test signals: linked without libpsx, the exploit should succeed; linked with libpsx as `noexploit`, it should fail. The Makefile inverts expected exit codes accordingly.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/tests/exploit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/tests/libcap_launch_test.c -->
# sources/security-integrity/libcap/tests/libcap_launch_test.c

Purpose: privileged integration test for libcap launcher APIs.

Important APIs/functions: `struct test_case_s` describes launch attributes. `clean_out()` drops all process caps in a callback. Main exercises `cap_new_launcher()`, `cap_func_launcher()`, `cap_launcher_callback()`, `cap_launcher_set_chroot()`, `cap_launcher_setuid()`, `cap_launcher_setgroups()`, `cap_launcher_set_iab()`, `cap_launcher_set_mode()`, `cap_launch()`, and `cap_free()`.

Control flow: iterates table-driven cases, configures launcher attributes, launches, waits, compares wait status against expected result, and finally verifies parent capabilities match the original state.

State and dependencies: spawns child processes, may chroot, changes child uid/gid/IAB/mode, and depends on `../progs/tcapsh-static` plus `noop`.

Risks and test signals: covers launch aborts, callback ordering, IAB propagation, no-priv mode, chrooted static binary execution, and parent-state preservation. A `WITH_PTHREADS` variant links libpsx.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/tests/libcap_launch_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/tests/libcap_psx_test.c -->
# sources/security-integrity/libcap/tests/libcap_psx_test.c

Purpose: C stress test that libcap operations linked with libpsx keep security state coherent across threads and forks.

Important APIs/functions: `thread_fork_exit()` forks from a thread, reads/writes keepcaps via `cap_prctl()` and `cap_prctlw()`, and verifies child state can change independently. Main starts ten threads while toggling keepcaps.

Control flow: each loop creates a worker thread, toggles keepcaps process-wide through libcap, verifies current process state, and allows workers to fork and validate their own transitions.

State and dependencies: uses pthreads, fork/wait, libcap prctl wrappers, libpsx linkage, and keepcaps state.

Risks and test signals: catches races between PSX fan-out, thread creation, and fork inheritance. Failure indicates process-wide security state is not consistently synchronized.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/tests/libcap_psx_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/tests/noop.c -->
# sources/security-integrity/libcap/tests/noop.c

Purpose: static no-op executable for launcher and chroot tests.

Important APIs/functions: `main()` immediately exits 0.

Control flow/state/dependencies: no state and no dependencies beyond libc. Built statically by the tests Makefile so it can run inside a chroot without shared libraries.

Integration points: `libcap_launch_test.c` launches `/noop` after `cap_launcher_set_chroot(".")`.

Risks and test signals: intentionally minimal; failure means execution environment or static linking is broken rather than application logic.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/tests/noop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/tests/psx_test.c -->
# sources/security-integrity/libcap/tests/psx_test.c

Purpose: C test for raw `psx_syscall()` synchronization across pthreads, forks, execs, and keepcaps transitions.

Important APIs/functions: `say_hello_expecting()` checks `PR_GET_KEEPCAPS`. Worker `say_hello()` waits on condition variables and validates shared keepcaps over several steps. Main toggles keepcaps with `psx_syscall(SYS_prctl, PR_SET_KEEPCAPS, ...)`, starts threads, forks/execs a child, and joins threads.

Control flow: ten iterations alternate keepcaps, notify all launched threads to validate state, add threads in early iterations, then join them in later iterations. A forked child execs the same binary with a stop argument.

State and dependencies: mutates keepcaps, uses pthread mutex/cond, fork/exec/wait, and libpsx public header.

Risks and test signals: catches missed threads, stale state after fork/exec, and synchronization deadlocks in the core C PSX path.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/tests/psx_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/tests/uns_test.c -->
# sources/security-integrity/libcap/tests/uns_test.c

Purpose: privileged regression test for user namespace UID/GID map exploit behavior involving `CAP_SETFCAP`.

Important APIs/functions: lowers effective `CAP_SETFCAP`, changes uid through `cap_setuid()`, clones a child in `CLONE_NEWUSER`, writes crafted uid/gid maps under `/proc/<pid>/{uid,gid}_map`, and coordinates through pipes.

Control flow: if environment lacks effective `CAP_SYS_ADMIN`, exits 0 as not testable. Parent rotates uid 1 to 0, attempts map writes, and treats successful exploit launch as failure requiring kernel upgrade. Write or close failure on maps is the expected safe path.

State and dependencies: mutates capabilities, uid, namespaces, `/proc` map files, session state, and may exec `/bin/bash` in child.

Risks and test signals: highly privileged and environment-sensitive. It is run under sudo by `quicktest.sh` and tests kernel hardening rather than libcap logic alone.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/tests/uns_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/tests/weaver.c -->
# sources/security-integrity/libcap/tests/weaver.c

Purpose: shared-object and executable helper that creates threads and reports aggregate keepcaps observations for PSX regression tests.

Important APIs/functions: exports `weaver_thread()`, `weaver_setup()`, `weaver_waitforit()`, and `weaver_terminate()`. `run_thread()` waits for trigger state and adds `PR_GET_KEEPCAPS + 2` to a total. `SO_MAIN()` self-tests ten threads when the shared object is run as executable.

Control flow: condition variables coordinate priming, tick, and exit states. `weaver_waitforit(n)` waits until `n` threads are ready, triggers them, waits for all counters, resets trigger, and returns total.

State and dependencies: static mutex/cond and counters hold shared state. Depends on pthreads, prctl, and `execable.h`.

Risks and test signals: used to prove PSX can discover threads created inside dlopened code not linked directly with libpsx. Expected totals encode keepcaps consistency.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/tests/weaver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/tests/weaver.h -->
# sources/security-integrity/libcap/tests/weaver.h

Purpose: public declarations for the weaver thread helper.

Important APIs/types: declares `pthread_t weaver_thread(void)`, `void weaver_setup(void)`, `int weaver_waitforit(int n)`, and `void weaver_terminate(void)`.

Control flow/state: none in the header; state lives in `weaver.c`.

Dependencies and integration: requires `pthread_t` to be visible to includers. Used by `weaver.c`; `b219174.c` obtains the same symbols dynamically with `dlsym()` instead of including the header.

Risks and test signals: type drift between declarations and implementation would break compilation. Runtime symbol drift is caught by `b219174.c`.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/tests/weaver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/.circleci/config.yml -->
# sources/security-integrity/selinux/.circleci/config.yml

Purpose: legacy CircleCI configuration for SELinux userspace static analysis builds.

Important jobs/steps: one `build` job uses `circleci/python:3.6`, installs compiler and SELinux build dependencies, sets `DESTDIR` and `IS_CIRCLE_CI`, downloads refpolicy headers, patches paths for DESTDIR, runs `./scripts/run-scan-build`, and stores scan-build artifacts.

Control flow: checkout, apt dependency install, environment setup, refpolicy bootstrap, static analysis, artifact upload.

State and dependencies: writes `$HOME/destdir`, `/etc/selinux/config`, `/etc/selinux/sepolgen.conf`, and downloaded refpolicy contents. Depends on network access and old CircleCI image availability.

Risks and test signals: dependency/image age and external refpolicy URL stability are risks. Primary signal is clang scan-build artifact generation, not normal CI test coverage.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/.circleci/config.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/.github/actions/build-userspace/action.yml -->
# sources/security-integrity/selinux/.github/actions/build-userspace/action.yml

Purpose: composite GitHub Action that builds and installs SELinux userspace for workflow matrix jobs.

Important inputs/outputs: inputs select Python, Ruby, compiler, and optional build variant. Output `DESTDIR` exposes `/tmp/destdir`. Steps set up Python and Ruby, install apt dependencies, optionally install clang, configure `CC`, `PYTHON`, `RUBY`, `DESTDIR`, and explicit make variable overrides.

Control flow: build step runs `make install` twice, then `make install-pywrap` and `make install-rubywrap`, with optional linker and debug/flag override variants.

State and dependencies: writes GitHub environment variables, uses apt, pip, bundler cache, and repository Makefiles.

Risks and test signals: duplicated `make install` may be intentional idempotence or accidental redundancy. Matrix variants exercise compiler, linker, flags, debug, and wrapper installation assumptions.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/.github/actions/build-userspace/action.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/.github/workflows/check_format.yml -->
# sources/security-integrity/selinux/.github/workflows/check_format.yml

Purpose: GitHub Actions workflow enforcing C/H formatting.

Important jobs/steps: triggers on push and pull_request to `main`, runs in `fedora:latest`, checks out code, installs `make` and `clang-tools-extra`, and runs `make check-format`.

Control flow: simple single-job format gate. The top-level Makefile selects all C/H files under `SUBDIRS` and invokes `clang-format --dry-run -Werror`.

State and dependencies: depends on Fedora package names and repository Makefile format target. No persistent state beyond CI workspace.

Risks and test signals: branch trigger uses `main`, while other workflows use `master`; that mismatch may affect coverage depending on repository default branch. Signal is purely style conformance.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/.github/workflows/check_format.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/.github/workflows/cifuzz.yml -->
# sources/security-integrity/selinux/.github/workflows/cifuzz.yml

Purpose: GitHub Actions OSS-Fuzz CIFuzz workflow for SELinux fuzz targets.

Important jobs/steps: triggers on push and PR to `master`, only runs for `SELinuxProject/selinux`, and matrixes address, undefined, and memory sanitizers. Uses Google OSS-Fuzz actions to build and run fuzzers for 600 seconds, then uploads crash artifacts on failure after successful build.

Control flow: build fuzzer, run fuzzer, upload artifacts if failing.

State and dependencies: depends on OSS-Fuzz project definition `selinux`, external GitHub actions at `master`, sanitizer support, and generated `out/artifacts`.

Risks and test signals: external action pinning to `master` is mutable. It provides dynamic parser/compiler fuzz coverage, especially for `checkpolicy/fuzz/checkpolicy-fuzzer.c`.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/.github/workflows/cifuzz.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/.github/workflows/run_tests.yml -->
# sources/security-integrity/selinux/.github/workflows/run_tests.yml

Purpose: primary SELinux userspace GitHub Actions test workflow.

Important jobs/steps: triggers on push and pull_request, matrixes gcc/clang with multiple Python and Ruby versions plus build variants. It uses the local build action, downloads refpolicy headers, runs `make all`, sources `scripts/env_use_destdir`, runs `make test`, tests Python/Ruby imports except under sanitizers, runs flake8, and validates `.gitignore` plus `make clean distclean`.

Control flow: build, bootstrap refpolicy, build remaining targets, set test environment, run tests/wrappers/lint, then clean-state checks.

State and dependencies: uses `/tmp/destdir`, apt/pip/ruby setup, refpolicy network download, and many repository subdir Makefiles.

Risks and test signals: broad matrix catches compiler, linker, Python, Ruby, sanitizer, clean, and packaging regressions. External refpolicy availability is a CI risk.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/.github/workflows/run_tests.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/.github/workflows/tf_testsuite.yml -->
# sources/security-integrity/selinux/.github/workflows/tf_testsuite.yml

Purpose: schedules SELinux testsuite runs in Testing Farm.

Important jobs/steps: triggers on push and pull_request, matrixes `x86_64` and `aarch64`, and invokes `sclorg/testing-farm-as-github-action@main` with `TESTING_FARM_API_TOKEN` and selected architecture.

Control flow: single scheduling step per architecture. The actual test plan is delegated to Testing Farm configuration outside this file.

State and dependencies: depends on repository secret, external action at `main`, and Testing Farm service availability.

Risks and test signals: mutable action reference and secret availability can disable signal. It broadens architecture coverage beyond GitHub-hosted x86_64 runners.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/.github/workflows/tf_testsuite.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/CleanSpec.mk -->
# sources/security-integrity/selinux/CleanSpec.mk

Purpose: Android-style clean specification placeholder.

Important behavior: comments state the empty file prevents the build system from descending into subdirectories.

Control flow/state/dependencies: no executable rules, state, or dependencies.

Integration points: recognized by build systems that scan `CleanSpec.mk`; its presence is itself the behavior.

Risks and test signals: if removed, an external build system may perform unwanted recursive clean behavior. No local tests target it directly.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/CleanSpec.mk -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/Makefile -->
# sources/security-integrity/selinux/Makefile

Purpose: top-level SELinux userspace build orchestrator.

Important variables/targets: defines `PREFIX`, optional subdirs, `SUBDIRS`, Python/Ruby wrapper subdirs, `CFLAGS`/`LDFLAGS`, `FTS_LDLIBS` detection, `DESTDIR` include/lib overrides, and aggregate targets `all`, `install`, `relabel`, `clean`, `test`, `install-pywrap`, `install-rubywrap`, `swigify`, `distclean`, `format`, and `check-format`.

Control flow: iterates subdirectories and invokes the same target; wrapper targets only visit Python-capable subdirs. Format targets find C/H files under subdirs and run clang-format.

State and dependencies: exports build flags and lib paths to submakes. Depends on compiler, `fts.h` probe, libsepol location, clang-format, and subdir Makefiles.

Risks and test signals: `-Werror` makes compiler drift visible. DESTDIR path propagation is heavily exercised by CI matrix build variants and clean checks.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/Makefile -->
# sources/security-integrity/selinux/checkpolicy/Makefile

Purpose: builds `checkpolicy` and `checkmodule`.

Important variables/targets: uses flex and bison to generate `lex.yy.c` and `y.tab.c`; defines shared parser/compiler objects plus program-specific objects. Targets include `all`, `checkpolicy`, `checkmodule`, pattern object compilation, `test`, `checkobjects` for fuzzing, `install`, `relabel`, and `clean`.

Control flow: `all` builds tools then runs `make -C test`. Generated parser/lexer objects compile with `-Werror` filtered out. `test` runs `./tests/test_roundtrip.sh`.

State and dependencies: depends on static libsepol, parser grammar, scanner, module compiler objects, man pages, and install destinations.

Risks and test signals: generated C warnings are tolerated by filtering `-Werror`. `checkobjects` supports fuzz builds. Roundtrip tests provide functional policy conversion coverage.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/checkmodule.c -->
# sources/security-integrity/selinux/checkpolicy/checkmodule.c

Purpose: command-line compiler for SELinux base and policy modules.

Important APIs/functions: `read_binary_policy()` opens, stats, mmaps, initializes, reads, and MLS-checks a binary policy. `write_binary_policy()` sets policy type/version/unknown handling and writes via libsepol. `main()` parses options for binary input, CIL output, module/base type, MLS, neverallow disable, warnings-as-errors, line markers, output path, unknown handling, and module policy version.

Control flow: validates incompatible options (`-U` only base, `-b` incompatible with `-m`, `-L` requires `-C`), loads source or binary policy, checks hierarchy constraints, validates module name against output basename, expands base modules when writing binary, loads initial SIDs, then writes binary or CIL if requested.

State and dependencies: uses global `sidtab`, parser globals `mlspol`/`werror`, libsepol policydb services, mmap, basename, and filesystem output.

Risks and test signals: mmapped input is not unmapped on some error paths; option compatibility is security relevant. Build tests and fuzz object builds exercise parser/link/expand paths.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/checkmodule.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/checkpolicy.c -->
# sources/security-integrity/selinux/checkpolicy/checkpolicy.c

Purpose: main SELinux policy compiler and optional interactive policy service debugger.

Important APIs/functions: parses source or binary policies, links optional blocks, expands modules to kernel policy, writes binary policy, CIL, or policy.conf, sorts ocontexts, optimizes kernel policy, and exposes debug menu calls into libsepol service APIs. Helpers display booleans/conditional expressions, change booleans, check MLS levels, print SIDs, and optionally identify equivalent types.

Control flow: command-line options select binary/source, debug, target platform, MLS, output format, policy version, sorting, optimization, unknown handling, neverallow checking, CIL line markers, and warnings-as-errors. Source input builds a base parse policy, validates levels, links optionals, and expands unless CIL output is requested. Binary input is mmapped and version-adjusted. Output is written before debug mode; without debug it cleans up and exits. Debug mode enters a menu loop for access-vector, SID/context, transition, filesystem, network, boolean, constraint, InfiniBand, and equivalent-type queries.

State and dependencies: global `policydb`, `sidtab`, `policydbp`, parser globals, mmap data, and interactive stdin state. Depends heavily on libsepol, parser/scanner objects, networking address parsing, and filesystem I/O.

Risks and test signals: large option surface, policy version downgrades/upgrades, MLS consistency, and interactive input parsing are risk points. Roundtrip tests, CI build variants, and fuzzing cover parse/link/expand/write conversions.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/checkpolicy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/fuzz/checkpolicy-fuzzer.c -->
# sources/security-integrity/selinux/checkpolicy/fuzz/checkpolicy-fuzzer.c

Purpose: libFuzzer target for SELinux checkpolicy parsing, linking, expansion, validation, and output conversion.

Important APIs/functions: `full_write()` writes fuzz data robustly. `read_source_policy()` feeds data through a memfd and the two-pass parser, handling parser longjmp state and cleanup. `LLVMFuzzerTestOneInput()` interprets first bytes as target platform, MLS flag, and policy version, then parses, links, expands, validates, optimizes/sorts, and writes binary/conf/CIL to `/dev/null`.

Control flow: rejects inputs shorter than three bytes or invalid selector bytes. For valid source bodies, it initializes policydbs, parses, expands base policies to kernel policies when needed, loads initial SIDs, validates final policydb, aborts if invalid policy can be emitted, and resets global parser/module state.

State and dependencies: uses parser globals, `id_queue`, `policydbp`, `mlspol`, `policydb_errors`, memfd, libsepol, and module compiler reset.

Risks and test signals: global parser state cleanup is critical for repeated fuzz iterations. CIFuzz and OSS-Fuzz exercise this target under sanitizers.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/fuzz/checkpolicy-fuzzer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/fuzz/min_pol.conf -->
# sources/security-integrity/selinux/checkpolicy/fuzz/min_pol.conf

Purpose: minimal non-MLS SELinux policy seed for checkpolicy fuzzing.

Important content: declares core classes and SIDs, process permissions, default roles for file-like classes, a type with aliases, an allow rule, role/user mappings, SID contexts, and `fs_use_trans` entries.

Control flow/integration: no executable flow. Used as a seed corpus or baseline policy shape for the fuzzer/parser path.

State and dependencies: policy text depends on checkpolicy language grammar and libsepol semantic validation.

Risks and test signals: intentionally small but semantically complete enough to parse and expand. It provides non-MLS coverage for class, SID, typealias, allow, role, user, and filesystem labeling constructs.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/fuzz/min_pol.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/fuzz/min_pol.mls.conf -->
# sources/security-integrity/selinux/checkpolicy/fuzz/min_pol.mls.conf

Purpose: minimal MLS-enabled SELinux policy seed for checkpolicy fuzzing.

Important content: extends the non-MLS minimal policy with `sensitivity`, `dominance`, `category`, `level`, `mlsconstrain`, MLS-aware user range, and MLS-labeled SID and filesystem contexts.

Control flow/integration: policy text seed for parser/fuzzer runs where MLS flag is enabled. It exercises MLS grammar and semantic checks that are absent from `min_pol.conf`.

State and dependencies: depends on checkpolicy MLS grammar, level/category consistency, and libsepol validation.

Risks and test signals: catches regressions in MLS parsing, constraint handling, and context serialization. It is compact enough to mutate efficiently in fuzzing.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/fuzz/min_pol.mls.conf -->

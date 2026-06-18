# Research Report: subset-b-008341

This grouped report covers the requested libcap files. Each section is source-tree aligned and bounded by reconciliation markers for deterministic splitting into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/sucap/su.c -->
## sources/security-integrity/libcap/contrib/sucap/su.c

Purpose: capability-aware `su` implementation that authenticates with PAM, preserves selected privilege through UID/GID transitions, opens and closes login sessions, updates terminal ownership and utmp/wtmp, then launches the target shell through libcap's launcher API.

Important APIs/functions: environment and descriptor setup uses `make_environment()` and `checkfds()`. Terminal handling is split across `store_terminal_modes()`, `restore_terminal_modes()`, `disable_terminal_signals()`, `change_terminal_owner()`, and `restore_terminal_owner()`. Authentication/session flow uses `do_pam_init()`, `authenticate_user()`, `user_accounting()`, `set_credentials()`, `open_session()`, `close_session()`, and PAM calls `pam_start`, `pam_authenticate`, `pam_acct_mgmt`, `pam_setcred`, `pam_open_session`, `pam_close_session`, and `pam_end`. Capability transitions rely on `cap_get_proc`, `cap_fill`, `cap_set_flag`, `cap_set_proc`, `cap_setuid`, `cap_iab_get_proc`, `cap_new_launcher`, `cap_launcher_callback`, and `cap_launch`. Login accounting uses `find_utmp_entry()`, `set_terminal_name()`, `write_wtmp()`, `utmp_do_open_session()`, and `utmp_do_close_session()`.

Control flow: `main()` builds an all-permitted capability set, validates terminal access, parses `su [-] [-h] [-c command] username`, initializes PAM, ignores dangerous terminal signals, temporarily changes UID to `TEMP_UID`, authenticates and performs account checks with capabilities raised, resolves the target passwd entry, initializes groups and uid while keeping permitted caps, optionally changes terminal ownership and utmp/wtmp entries, opens the PAM session, builds shell argv/env, launches the child via `cap_launch()`, waits with signal forwarding/forced kill behavior, closes PAM and utmp sessions, deletes credentials, restores terminal owner/modes, restores the invoking UID, and exits with the child status where possible.

State/persistence: mutates process uid/gid/groups, capability effective/permitted/inheritable state, PAM environment/data, terminal mode and owner, signal dispositions, utmp/wtmp records, current directory for login shells, and spawned child lifetime. Persistent state includes `/var/run/utmp` and `/var/log/wtmp` updates plus syslog alerts on restoration failure.

Dependencies/integration: Linux-PAM, pam_misc, passwd/group databases, libcap, terminal and utmp APIs, `/dev` tty names, `_PATH_UTMP`/`_PATH_WTMP`, syslog, and shell paths. Integrates with libcap's launcher to isolate pre-exec setup from the parent monitor.

Risks: high security blast radius. Shell parsing is whitespace based and deliberately restrictive, but malformed passwd shells and command strings remain sensitive. `getlogin()` and DNS lookup for rhost can fail or block. Terminal and utmp restoration is best effort. Multiple code paths temporarily raise all effective capabilities. `make_process_killable()` assumes `invoked_uid` was set. PAM errors, partial session setup, and child launch failures must not skip cleanup.

Test signals: run through PAM success/failure cases, login and non-login modes, `-c` command mode with job-control signals, terminal owner restoration, utmp/wtmp replacement, target user without shell/home, non-root target rejection for uid 0, and capability drops after child launch. Existing libcap launcher tests indirectly cover `cap_launch`; `su.c` itself needs privileged integration testing.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/sucap/su.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/distcheck.sh -->
## sources/security-integrity/libcap/distcheck.sh

Purpose: release sanity script that checks whether libcap's bundled `include/uapi/linux/capability.h` names the same `CAP_LAST_CAP` as the current upstream Linux kernel header.

Important APIs/functions: shell variables `actual` and `working`; external commands `wget`, `grep`, and `awk`.

Control flow: downloads Torvalds tree's raw capability header, extracts the third field from the `#define CAP_LAST_CAP` line, extracts the same value from the local libcap header, prints success and exits 0 if equal, otherwise prints `want`/`have` and exits 1.

State/persistence: no persistent writes; network read only.

Dependencies/integration: requires network access to `git.kernel.org`, `wget`, and a source tree rooted at libcap so `libcap/include/uapi/linux/capability.h` exists. Integrates with release/distribution checks.

Risks: network instability or upstream format changes can produce false failures; it only compares the last capability macro, not comments, individual names, or semantic drift.

Test signals: mock or cache the upstream header and verify equal/unequal paths; run in CI with network optionality documented.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/distcheck.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/doc/Makefile -->
## sources/security-integrity/libcap/doc/Makefile

Purpose: builds, installs, and optionally renders libcap/libpsx manual pages.

Important targets/variables: `MAN1S`, `MAN3S`, `MAN5S`, `MAN7S`, `MAN8S`, aggregate `MANS`, `all`, `html`, `install`, `clean`, `test`, and `sudotest`.

Control flow: includes `Make.Rules`, treats all listed manpage files as the default build product, renders HTML with `groff -man -Thtml` while skipping `.so man` redirect pages, installs manpages into section-specific `$(MANDIR)/manN` directories using a destination-state loop, and removes generated `html` output on clean.

State/persistence: creates `html/` and installs manpages under `$(FAKEROOT)$(MANDIR)`.

Dependencies/integration: GNU make, project `Make.Rules`, `groff`, install utilities, and the manpage source files. Integrated with top-level libcap build/install flows.

Risks: install loop is compact and depends on absolute-path markers to switch section destinations; missing manpage entries silently break packaging completeness. HTML generation skips redirect pages and may leave crosslinks unresolved.

Test signals: `make -C doc all`, `make -C doc html`, staged `make install FAKEROOT=...`, and package checks confirming every public API in `sys/capability.h` has a corresponding manpage.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/doc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/doc/crosslink.sh -->
## sources/security-integrity/libcap/doc/crosslink.sh

Purpose: helper script for auditing manpage `.so man...` cross-reference redirect pages against their targets.

Important APIs/functions: shell loop over `*.?`, `grep -F '.so m'`, `awk`, and `sed`.

Control flow: for each one-character-extension manpage, extracts the redirect target from `.so man...`, skips non-redirect pages, prints a divider and mapping, then greps the target page for the source basename.

State/persistence: no writes.

Dependencies/integration: intended to be run from `doc/`; assumes manpage redirect syntax and local target files. Supports documentation maintenance rather than build output.

Risks: only handles simple `*.?` section names and fixed `.so m` text; grep failures are informational, not machine-enforced.

Test signals: run after adding or renaming manpage redirect files and inspect missing references.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/doc/crosslink.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/doc/md2html.lua -->
## sources/security-integrity/libcap/doc/md2html.lua

Purpose: Pandoc Lua filter that rewrites markdown links ending in `.md` to `.html` during generated manpage HTML rendering.

Important APIs/functions: `Link(el)` callback and `string.gsub`.

Control flow: every Pandoc link element is visited; its target string has `.md` replaced by `.html`; the modified element is returned.

State/persistence: no persistent state; transformation is in-memory during Pandoc processing.

Dependencies/integration: Pandoc Lua filter API. Used by the comment in `mkmd.sh` for markdown-to-HTML conversion.

Risks: global replacement can rewrite `.md` anywhere in a URL, not only as a suffix; external links containing `.md` may be altered unintentionally.

Test signals: run Pandoc with the filter against generated markdown containing local and external links and check final hrefs.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/doc/md2html.lua -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/doc/mkmd.sh -->
## sources/security-integrity/libcap/doc/mkmd.sh

Purpose: generates markdown versions of libcap manpages plus an index, using Pandoc when available.

Important APIs/functions: `do_page()` converts one manpage or records a redirect; main loop iterates sections 1, 3, 5, 7, and 8; optional `local-md.preamble` and `local-md.postscript` are included.

Control flow: exits successfully without conversion if Pandoc is absent, requires an output directory argument, creates the directory, initializes `index.md`, appends optional preamble, converts each `*.N` page using `pandoc -f man -t markdown`, post-processes bold manpage references into markdown links, writes one `<base>-<section>.md` file per real page, records redirect pages as index links to their targets, and appends more-information text.

State/persistence: creates or overwrites the output directory contents and `index.md`.

Dependencies/integration: Bash, Pandoc, sed, local manpages. Integrates with documentation publishing workflows and `md2html.lua`.

Risks: redirect parsing assumes `.so man` format; sed linkification covers only sections `[1358]` and could miss section 7 or unusual references; generated filenames are based on basename/section and can collide if inputs are unexpected.

Test signals: run `./mkmd.sh md`, inspect `md/index.md`, verify redirect entries, and render with Pandoc plus `md2html.lua`.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/doc/mkmd.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/go/Makefile -->
## sources/security-integrity/libcap/go/Makefile

Purpose: builds and tests libcap's Go packages, Go example applications, and Go/C interoperability checks using a vendor symlink tree that mimics module import paths.

Important targets/variables: `IMPORTDIR`, `PKGDIR`, `DEPS`, `TESTS`, `vendor/modules.txt`, `vendor/.../psx`, `vendor/.../cap`, `good-names.go`, `PSXGOPACKAGE`, `CAPGOPACKAGE`, app targets `web`, `setid`, `gowns`, `captree`, `captrace`, tests `compare-cap`, `try-launching`, `psx-signals`, `mismatch`, `iaber`, `b210613`, `b215283`, `test`, `sudotest`, `install`, and `clean`.

Control flow: builds `../libcap/libcap.a` and `../libcap/libpsx.a`, creates a Go vendor tree with symlinks to `../cap` and `../psx`, generates and diffs `good-names.go` from `cap_names.h`, builds packages/apps with `CGO_ENABLED` selected by `CGO_REQUIRED`, runs `go vet`, executes package tests and helper binaries, and runs privileged tests under `$(SUDO)` for launcher/IAB/regression behavior.

State/persistence: creates vendor directories, stamp files, generated `good-names.go`, binaries, `go.sum`, and optional file capabilities on `web` when `RAISE_GO_FILECAP=yes`.

Dependencies/integration: GNU make, Go toolchain, cgo, libcap/libpsx static libs, top-level `Make.Rules`, `setcap`, `tcapsh-static`, sudo-capable environment for `sudotest`.

Risks: symlinked vendor layout is fragile under tools that rewrite vendor trees; some tests are privilege/kernel/runtime dependent; known older Go all-thread syscall bugs are handled by cgo fallback paths but can still affect results.

Test signals: `make -C go test`, `make -C go sudotest`, cgo and non-cgo matrix when `CGO_REQUIRED=0`, `good-names.go` diff, and successful `captree` install staging.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/go/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/go/b210613.go -->
## sources/security-integrity/libcap/go/b210613.go

Purpose: minimal Go reproducer/regression for kernel bug 210613, verifying `cap.ModeNoPriv.Set()` can drop privilege without failure.

Important APIs/functions: `cap.ModeNoPriv.Set()` and `log.Fatalf`.

Control flow: calls the no-privilege mode setter; exits fatally on error; prints a pass marker on success.

State/persistence: mutates current process capability mode, securebits, bounding set, ambient set, and no-new-privs through the cap package; no persistent files.

Dependencies/integration: Go `cap` package and kernel capability/prctl support. Built and run in `go/Makefile` `sudotest`.

Risks: behavior depends on available privileges and kernel support; after successful mode drop the process cannot regain privilege.

Test signals: privileged `make -C go sudotest` runs this under `tcapsh-static` with required caps.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/go/b210613.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/go/b215283.go -->
## sources/security-integrity/libcap/go/b215283.go

Purpose: privileged Go regression for kernel bug 215283 involving securebits, launcher callbacks, and empty capability sets.

Important APIs/functions: `cap.GetProc().GetFlag`, `cap.GetSecbits`, `cap.FuncLauncher`, `Launcher.Launch`, `cap.NewSet().SetProc`, and `cap.Secbits.Set`.

Control flow: verifies the process has `CAP_SETPCAP` permitted and starts with `secbits=0`, launches a function child that clears process capabilities, prints before/after states, then sets `SECBIT_NOROOT|SECBIT_NO_SETUID_FIXUP`.

State/persistence: mutates process capability state in a launched child and securebits in the parent; no persistent files.

Dependencies/integration: Go cap package, launcher support, privileged kernel state. Built and run by `go/Makefile` `sudotest`.

Risks: must not run in an environment with pre-set securebits; failures are environment-sensitive and use direct process exit instead of test framework reporting.

Test signals: `sudo ./b215283` and cgo fallback target when applicable.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/go/b215283.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/go/cgo-required.sh -->
## sources/security-integrity/libcap/go/cgo-required.sh

Purpose: detects whether the Go runtime lacks `syscall.AllThreadsSyscall`, in which case libcap's Go security-state operations require cgo/libpsx for POSIX thread semantics.

Important APIs/functions: optional first argument selects `GO`; `go doc syscall | grep AllThreadsSyscall`.

Control flow: sets `GO` from argument or defaults to `go`, checks documentation output, echoes `1` if the symbol is absent and `0` if present.

State/persistence: no writes.

Dependencies/integration: Go toolchain and shell utilities; its output feeds build variables such as `CGO_REQUIRED`.

Risks: parsing `go doc` text is brittle and can be affected by localized or changed output; missing Go binary is treated the same as missing symbol.

Test signals: run against known Go versions before and after `AllThreadsSyscall` support and verify expected `1`/`0`.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/go/cgo-required.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/go/compare-cap.go -->
## sources/security-integrity/libcap/go/compare-cap.go

Purpose: Go/C interoperability test proving Go `cap` package text/binary/file/process/IAB operations agree with C libcap.

Important APIs/functions: cgo imports `cap_get_pid`, `cap_to_text`, `cap_from_text`, `cap_copy_ext`, `cap_copy_int_check`, `cap_iab_*`; Go paths use `cap.GetPID`, `cap.FromText`, `Set.Export`, `cap.Import`, `cap.IABFromText`, `IAB.GetVector`, `SetFile`, `GetFile`, `SetFd`, `GetFd`, `SetProc`, `SetUID`, `SetGroups`, mode setters, and comparisons.

Control flow: imports PID 1 capabilities from C text into Go and compares direct Go read, round-trips C/Go binary formats both ways, validates `all=ep`, samples many capability/flag combinations for reversible string/export/import behavior, compares IAB text generated by Go and C, optionally tests file capability setting/removal if permitted, then tests process UID/GID/mode operations and intentionally ends with no privileges.

State/persistence: can modify capabilities on its own executable and current process uid/gid/groups/capability mode; cleans up file caps when possible but privileged failure paths are sensitive.

Dependencies/integration: cgo, local `../libcap` headers/library, Go cap package, Linux file capabilities, `/proc` PID 1 status, and sufficient privilege for full coverage. Built/run by `go/Makefile`.

Risks: mutates its own binary xattrs; process privilege drops are irreversible in-process; optional tests skip on insufficient privilege, so unprivileged success is partial coverage.

Test signals: `LD_LIBRARY_PATH=../libcap ./compare-cap` from `make -C go test`; privileged `sudotest` for process/file capability paths.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/go/compare-cap.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/go/iaber.go -->
## sources/security-integrity/libcap/go/iaber.go

Purpose: helper/regression program that sets an IAB tuple, execs itself, and validates capability inheritance behavior across exec.

Important APIs/functions: `cap.SetUID`, `cap.GetProc`, `cap.IABGetProc`, `cap.IABFromText`, `IAB.SetProc`, and `syscall.Exec`.

Control flow: with no extra args logs success; otherwise changes UID to 1 if needed, logs current cap/IAB state, parses the first argument as IAB text, applies it to the process, logs pre-exec state, and execs itself with remaining arguments.

State/persistence: mutates UID and IAB vectors of the current process; no files.

Dependencies/integration: Go cap package, Linux IAB/ambient/bounding semantics, exec behavior. Used by `go/Makefile` `sudotest`.

Risks: requires privilege for UID/IAB changes; failure leaves only logs; argument contract is terse.

Test signals: `sudo ./iaber` cases in `go/Makefile` that should pass/fail based on bounding drops and ambient/inheritable settings.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/go/iaber.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/go/mismatch.go -->
## sources/security-integrity/libcap/go/mismatch.go

Purpose: negative psx test that should fail/panic because `gettid` returns different values across threads and therefore violates psx all-thread consistency expectations.

Important APIs/functions: `psx.Syscall3(syscall.SYS_GETTID, ...)`.

Control flow: calls the all-thread syscall wrapper for `GETTID` and prints the returned tid/error; Makefile expects this command to fail.

State/persistence: no persistent state.

Dependencies/integration: Go psx package and Go runtime threads. Used by `go/Makefile` as an expected-failure test.

Risks: if psx consistency detection regresses, this may incorrectly succeed; output is diagnostic rather than structured.

Test signals: `./mismatch || exit 0 ; exit 1` in `make -C go test`, plus cgo variant when applicable.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/go/mismatch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/go/mknames.go -->
## sources/security-integrity/libcap/go/mknames.go

Purpose: generator that converts C `cap_names.h` plus per-capability documentation snippets into the Go package's `names.go`.

Important APIs/functions: flags `--header` and `--textdir`; reads header, extracts quoted capability names, reads `<textdir>/<index>.txt`, emits `NamedCount`, Go `Value` constants, `names` map, and reverse `bits` map.

Control flow: validates `--header`, scans lines containing quotes from generated C header, for each name reads matching documentation, rewrites `CAP_` references to `cap.`, requires first doc line to start with `Allows `, emits comments and uppercase trimmed constants using `iota`, then emits maps.

State/persistence: writes generated Go source to stdout; `go/Makefile` redirects through `gofmt` to `good-names.go` and diffs against `../cap/names.go`.

Dependencies/integration: Go standard library, generated `libcap/cap_names.h`, `doc/values/*.txt`, and cap package source conventions.

Risks: parser is intentionally simple and depends on exact generated header/doc formats; typo in fatal text does not affect behavior but indicates manual maintenance.

Test signals: `make -C go good-names.go` and diff against committed `../cap/names.go`.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/go/mknames.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/go/ok.go -->
## sources/security-integrity/libcap/go/ok.go

Purpose: trivial executable used as a successful target for launcher and chroot tests.

Important APIs/functions: `main()` calls `os.Exit(0)`.

Control flow: immediate zero exit.

State/persistence: no state.

Dependencies/integration: built by `go/Makefile` with `CGO_ENABLED=0`; used by `try-launching` as a chroot-friendly binary.

Risks: must remain simple/static enough for chroot tests; adding imports or dynamic dependencies would weaken its role.

Test signals: `make -C go ok` and `try-launching` cases that execute `/ok` inside a chroot.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/go/ok.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/go/psx-fd.go -->
## sources/security-integrity/libcap/go/psx-fd.go

Purpose: reproducer for older Go runtime deadlocks involving `AllThreadsSyscall` while another goroutine is blocked on a file descriptor.

Important APIs/functions: `os.Pipe`, goroutine `Read`, `time.Sleep`, and `psx.Syscall3(SYS_PRCTL, PR_SET_KEEPCAPS, ...)`.

Control flow: creates a pipe, starts a goroutine blocked reading, sleeps briefly to let it block, invokes psx all-thread `prctl`, then closes pipe descriptors.

State/persistence: toggles process `PR_SET_KEEPCAPS` during the test; no files.

Dependencies/integration: Go psx package, Go runtime thread/syscall behavior, Linux prctl. Built and run by `go/Makefile`, with timeout for known buggy Go versions.

Risks: intentionally can deadlock on Go 1.16/1.17 without cgo workaround; test result is runtime-version dependent.

Test signals: `timeout 5 ./psx-fd || echo "this is a known Go bug"` and cgo variant when `CGO_REQUIRED=0`.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/go/psx-fd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/go/psx-signals.go -->
## sources/security-integrity/libcap/go/psx-signals.go

Purpose: validates psx all-thread syscalls do not spuriously interact with Go signal handling.

Important APIs/functions: `signal.Notify`, `psx.Syscall3(SYS_PRCTL, PR_SET_KEEPCAPS, ...)`, and timed select.

Control flow: subscribes to interrupt signals, toggles `KEEP_CAPS` ten times via psx syscall, then waits one second and fails if any signal arrives.

State/persistence: mutates process `PR_SET_KEEPCAPS` flag repeatedly; no persistent files.

Dependencies/integration: Go psx package, Go signal package, Linux prctl. Built/run by `go/Makefile` test, including cgo variant where needed.

Risks: only observes a one-second window; ambient environment signals can cause false failure.

Test signals: successful `./psx-signals` output ending in `PASSED`; cgo/non-cgo matrix.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/go/psx-signals.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/go/try-launching.go -->
## sources/security-integrity/libcap/go/try-launching.go

Purpose: validates Go `cap.Launcher` behavior for normal launches, UID/GID/group changes, IAB setup, chroot, and capability modes.

Important APIs/functions: `cap.NewLauncher`, `Launcher.Callback`, `SetChroot`, `SetUID`, `SetGroups`, `SetMode`, `SetIAB`, `Launch`, `cap.IABFromText`, `cap.GetBound`, and `syscall.Wait4`.

Control flow: determines the libcap tree root and whether `CAP_SYS_ADMIN` is bounded, builds a table of launch scenarios with expected failures based on privilege, configures each launcher, starts all possible children, and waits for exit status validation.

State/persistence: creates child processes with changed credentials/modes/chroot/IAB; parent tracks PIDs/statuses only.

Dependencies/integration: Go cap package, built `go/ok`, `progs/tcapsh-static`, kernel chroot/user/capability support, root privilege for full coverage. Run in `go/Makefile` `sudotest`.

Risks: root/path inference uses the current working directory; expected-failure logic depends on current uid and bounding set; skipped failures can hide unsupported features.

Test signals: `./try-launching` and `sudo ./try-launching`, plus cgo variant when required.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/go/try-launching.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/goapps/captrace/captrace.go -->
## sources/security-integrity/libcap/goapps/captrace/captrace.go

Purpose: user-facing tracing tool that uses `bpftrace` kprobes/kretprobes on `cap_capable` to report kernel capability checks for all processes, a PID, or a launched command.

Important APIs/types/functions: flags `--bpftrace`, `--debug`, `--pid`; `thread` struct stores PPID, datum, capability value, and command token; global mutex-protected `tids` and `cache`; functions `event()`, `tailTrace()`, `tracer()`, and `main()`.

Control flow: starts `bpftrace` with probes emitting `CB` begin and `CE` end lines, scans stdout, caches begin events by tid, matches returns to log capability result and errno detail, filters to a PID tree when requested or when launching a command, and kills/waits the tracer after a launched command.

State/persistence: runtime maps of tracked PIDs and in-flight events; launches external processes; no files.

Dependencies/integration: `bpftrace`, kernel BPF/kprobe permissions, Go cap names for formatting, `/proc` process identity through bpftrace `pid/tid/comm`.

Risks: requires high privilege and kernel tracing support; begin/end matching by tid can race or be overwritten under concurrent nested checks; parser depends on exact printed space-separated format.

Test signals: run against a command that needs a known capability, verify successful and failing checks, run `--pid` filter, and validate cleanup of bpftrace child.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/goapps/captrace/captrace.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/goapps/captree/captree.go -->
## sources/security-integrity/libcap/goapps/captree/captree.go

Purpose: process-tree inspection tool that displays capabilities and IAB state for processes and threads rooted at supplied PIDs or command-name globs.

Important APIs/types/functions: flags `--proc`, `--depth`, `--verbose`, `--color/--colour`; `task` struct; functions `isATTY()`, `highlight()`, `(*task).fill()`, `rDump()`, `findPIDs()`, `setDepth()`, and `main()`. Uses `cap.GetPID`, `cap.IABGetPID`, `cap.ProcRoot`, `Set.Cf`, and `IAB.Cf`.

Control flow: reads all numeric directories under proc root, concurrently fills each process with status name/parent, capabilities, IAB, and thread details, builds parent-child relationships and depths, resolves requested PIDs/globs, then recursively dumps a tree with compact thread grouping when caps/IAB/name match.

State/persistence: in-memory task graph only; reads `/proc` or an alternate proc root.

Dependencies/integration: Go cap package, Linux procfs status/task layout, terminal color detection. Built and installed by `go/Makefile`.

Risks: process churn causes zombie/missing status races; a visible code issue parses `pid` instead of `tid` when filling thread capability state, which can under-report thread differences; recursive `setDepth` assumes parent entries exist except kernel root.

Test signals: `./captree 0`, `./captree $$`, `./captree --proc <fixture>`, thread-difference fixtures, and `go/Makefile` running `./captree 0`.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/goapps/captree/captree.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/goapps/gowns/gowns.go -->
## sources/security-integrity/libcap/goapps/gowns/gowns.go

Purpose: experimental Go wrapper for launching a child with optional user namespace mappings, UID/GID changes, IAB values, and libcap capability mode.

Important APIs/types/functions: `nsDetail`, range type `r`, flags `--base`, `--uid`, `--gid`, `--iab`, `--mode`, `--ns`, `--uids`, `--gids`, `--shell`, `--verbose`; functions `ranges()`, `nsSetup()`, `parseRanges()`, and `main()`. Uses `cap.NewLauncher`, `Launcher.Callback`, `SetUID`, `SetGroups`, `SetIAB`, `SetMode`, `Launch`, and `cap.GetProc`.

Control flow: parses ID mappings, creates a launcher for the requested shell/args, optionally attaches a callback that configures `syscall.SysProcAttr` with `CLONE_NEWUSER` and mappings, sets UID/GID/IAB/mode options, raises effective `CAP_SETUID`/`CAP_SETGID` if permitted to support setup, launches, drops parent privileges to an empty set, and waits for the child.

State/persistence: mutates parent effective capabilities briefly, drops parent privileges, creates child namespace/credential state; no files.

Dependencies/integration: Go cap package launcher support, Linux user namespaces, proc/sysctl namespace policy, CAP_SETUID/CAP_SETGID for extended mappings.

Risks: marked unstable; namespace setup requires kernel support and may fail under distro restrictions; malformed range arguments fatal; parent privilege drop after launch is irreversible.

Test signals: `./gowns -- -c "echo gowns runs"` in normal tests and privileged namespace case in `go/Makefile sudotest`.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/goapps/gowns/gowns.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/goapps/setid/setid.go -->
## sources/security-integrity/libcap/goapps/setid/setid.go

Purpose: demonstration tool for changing UID/GID/supplementary groups across all Go runtime threads using either cap convenience APIs or raw psx syscalls.

Important APIs/functions: flags `--uid`, `--gid`, `--drop`, `--suppl`, `--caps`; functions `setIDsWithCaps()`, `splitToInts()`, `dumpStatus()`, and `showIDs()`. Uses `cap.SetGroups`, `cap.SetUID`, `cap.NewSet().SetProc`, `psx.Syscall3`, and `/proc/<pid>/task/*/status`.

Control flow: records before state, parses target IDs and supplementary groups, changes IDs via cap or psx path, optionally drops all capabilities, then scans every task status to validate all threads show expected Uid/Gid lines.

State/persistence: mutates process UID/GID/groups and capabilities; no persistent files.

Dependencies/integration: Go cap and psx packages, Linux procfs task status, privilege to change IDs. Built/run by `go/Makefile`.

Risks: raw psx setgroups call appears to pass pointer where Linux syscall expects count as first argument on many ABIs, so `--caps=false` may be limited/bug-prone; supplementary groups are not fully validated in output; privilege changes are irreversible.

Test signals: `./setid --caps=false` from `make -C go test`, plus privileged runs with explicit UID/GID/group combinations.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/goapps/setid/setid.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/goapps/web/web.go -->
## sources/security-integrity/libcap/goapps/web/web.go

Purpose: example HTTP server that raises `CAP_NET_BIND_SERVICE` only for binding a privileged port, then drops all privilege before serving requests.

Important APIs/types/functions: flags `--port` and `--skip`; `ensureNotEUID()`, `listen()`, `Handler.ServeHTTP()`, and `main()`. Uses `cap.GetProc`, `Set.Dup`, `GetFlag`, `SetFlag`, `SetProc`, `cap.ModeNoPriv.Set`, `runtime.LockOSThread`, and `net/http`.

Control flow: rejects setuid/root execution, validates port, duplicates current caps, raises effective `NET_BIND_SERVICE` only around `net.Listen` unless skipped, restores original caps via defer, drops to `ModeNoPriv`, and serves responses showing pid/tid/cap state.

State/persistence: opens a listening socket and mutates process capability mode; no file persistence.

Dependencies/integration: Go cap package, Linux file capabilities on the built binary, network stack, HTTP server. `go/Makefile` can optionally set file capabilities on `web`.

Risks: `defer orig.SetProc()` restores caps after `net.Listen` returns, but errors before defer execution are handled by return; `ModeNoPriv` after listen is irreversible; running with `--skip` on low ports demonstrates failure rather than secure behavior.

Test signals: build with file cap `cap_setpcap,cap_net_bind_service=p`, run as non-root on port 80, confirm bind succeeds and request reports empty/no-priv caps.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/goapps/web/web.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/gomods.sh -->
## sources/security-integrity/libcap/gomods.sh

Purpose: bulk helper for updating libcap Go module dependency versions in all `go.mod` files under the current tree.

Important APIs/functions: version argument, `find . -name 'go.mod'`, and `sed -i` replacement.

Control flow: requires a target version argument, otherwise prints usage and exits 1; for each `go.mod`, rewrites lines beginning with `kernel.org/... v...` to the requested version.

State/persistence: edits every discovered `go.mod` in place.

Dependencies/integration: Bash, find, GNU/BSD-compatible `sed -i` behavior. Used for release/version maintenance.

Risks: broad regex can rewrite unintended `kernel.org` module lines; no dry run or git check; `sed -i` portability varies.

Test signals: run on a disposable tree, inspect `git diff`, and validate `go mod tidy/test`.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/gomods.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/kdebug/Makefile -->
## sources/security-integrity/libcap/kdebug/Makefile

Purpose: make wrapper for libcap kernel/debug testing via a generated initramfs and QEMU.

Important targets: `test`, `shell`, `exit`, `all`, `install`, and `clean`.

Control flow: `test` builds static `exit`, removes `interactive`, and runs `test-kernel.sh`; `shell` creates `interactive` before running the same script; `exit` builds `exit.c` statically; `clean` removes generated initramfs/config/output files.

State/persistence: creates `exit`, `interactive`, `fs.conf`, and `initramfs.img`; invokes broader tree build/test.

Dependencies/integration: top-level `Make.Rules`, C compiler, static libc, `test-kernel.sh`, local Linux kernel tree.

Risks: target assumes cwd is `kdebug`; static build may fail if static libc unavailable; `clean` deletes `interactive`, changing shell/test mode.

Test signals: `make -C kdebug test` for noninteractive QEMU run and `make -C kdebug shell` for interactive debug.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/kdebug/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/kdebug/exit.c -->
## sources/security-integrity/libcap/kdebug/exit.c

Purpose: guest-side QEMU exit helper that shuts down or signals status through ISA debug ports.

Important APIs/functions: `clean_exit()` calls `ioperm` and `outw` on ACPI shutdown port `0x604`; `main()` parses optional status, sleeps, uses `outb` on debug exit port `0x501`, and exits 1 if QEMU does not terminate.

Control flow: with wrong argc it attempts clean shutdown; with a status argument it prints status, sleeps three seconds, uses clean shutdown for status 0, otherwise writes `status-1` to the debug-exit port.

State/persistence: performs privileged port I/O in the guest; no files.

Dependencies/integration: Linux `sys/io.h`, x86/QEMU port behavior, QEMU `-device isa-debug-exit`.

Risks: architecture/QEMU-specific; requires I/O permission; status mapping follows QEMU debug-exit convention and can be confusing.

Test signals: run inside the kdebug initramfs and confirm QEMU exits with expected host status for pass/fail.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/kdebug/exit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/kdebug/test-bash.sh -->
## sources/security-integrity/libcap/kdebug/test-bash.sh

Purpose: wrapper that satisfies scripts expecting `/bin/bash` in the initramfs while actually invoking `/bin/sh`.

Important APIs/functions: `exec sh "$@"`.

Control flow: replaces itself with `sh` and forwards all arguments.

State/persistence: none.

Dependencies/integration: busybox or shell available as `sh`; included in `test-kernel.sh` initramfs as `/bin/bash`.

Risks: scripts using bash-specific syntax will fail because this is only a compatibility shim.

Test signals: initramfs quicktest scripts that reference bash still execute when POSIX-compatible.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/kdebug/test-bash.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/kdebug/test-init.sh -->
## sources/security-integrity/libcap/kdebug/test-init.sh

Purpose: init process for the kdebug initramfs that mounts basic filesystems, runs libcap quick tests, optionally opens an interactive shell, and exits QEMU.

Important APIs/functions: mount commands for proc/devtmpfs/sysfs/devpts, `quicktest.sh`, `sh -i`, and `./exit`.

Control flow: sets `PATH=/bin`, mounts required pseudo-filesystems, enters `/root`, runs quicktest and interactive shell when `/root/interactive` exists; otherwise runs quicktest and calls `./exit 1` on failure, then calls `./exit` for success.

State/persistence: mounts virtual filesystems in guest and runs tests; no disk persistence.

Dependencies/integration: generated initramfs layout from `test-kernel.sh`, busybox applets, libcap progs/tests, `exit` helper.

Risks: minimal error handling on mounts; failures before `exit` can leave QEMU running; interactive path depends on marker file.

Test signals: boot QEMU from `make -C kdebug test` and observe quicktest pass/fail exit.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/kdebug/test-init.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/kdebug/test-kernel.sh -->
## sources/security-integrity/libcap/kdebug/test-kernel.sh

Purpose: builds libcap, a Linux kernel, a test initramfs, and runs QEMU for capability/kernel integration testing.

Important APIs/functions: `die()`, `make LIBCSTATIC=yes clean all test`, `make -C progs tcapsh-static`, `make -C tests uns_test`, kernel `make V=1 all`, generated `fs.conf`, `gen_init_cpio`, `gzip`, and `qemu-system-$(uname -m)`.

Control flow: records interactive marker intent, rebuilds libcap static/test artifacts, builds the kernel under `../../linux`, generates an initramfs manifest containing init scripts, passwd, busybox links, libcap tools/tests, optional local `extras.sh`, and optional interactive marker, creates `initramfs.img`, computes bzImage path, and boots QEMU with serial console, SMP, and isa-debug-exit.

State/persistence: writes `fs.conf` and `initramfs.img`; builds libcap, tests, and kernel artifacts.

Dependencies/integration: local Linux kernel source at `../../linux`, kernel config already prepared, busybox at `/usr/sbin/busybox`, QEMU, gen_init_cpio, gzip, static libcap builds.

Risks: script references `HERE` before assignment when checking interactive marker, so preserving interactive mode may be unreliable; hardcoded paths and architecture assumptions; full kernel build is expensive.

Test signals: QEMU exit status, serial quicktest output, successful generation of initramfs, and optional interactive shell.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/kdebug/test-kernel.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/kdebug/test-prompt.sh -->
## sources/security-integrity/libcap/kdebug/test-prompt.sh

Purpose: tiny prompt helper for the kdebug initramfs shell.

Important APIs/functions: prints `$(pwd)# ` without a newline.

Control flow: immediate echo.

State/persistence: none.

Dependencies/integration: installed as `/bin/myprompt` in the generated initramfs.

Risks: assumes POSIX `pwd` and shell command substitution; no escaping.

Test signals: interactive kdebug shell displays current directory prompt.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/kdebug/test-prompt.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/libcap/Makefile -->
## sources/security-integrity/libcap/libcap/Makefile

Purpose: builds libcap and optional libpsx static/shared libraries, generated capability names, pkg-config files, executable shared-object metadata, tests, and install artifacts.

Important targets/variables: `CAPFILES`, `PSXFILES`, `CAPOBJS`, `PSXOBJS`, `cap_names.h`, `cap_names.list.h`, `_makenames`, `libcap.a`, `libpsx.a`, shared `libcap.so*`/`libpsx.so*`, `loader.txt`, `cap_magic.o`, `psx_magic.o`, `cap_test`, `libcapsotest`, `libpsxsotest`, `install-*`, and `clean`.

Control flow: includes `Make.Rules`, forces PIC and libpsx pthread linkage, removes problematic `-Bsymbolic-functions`, generates pkg-config files from templates, extracts capability names from the local UAPI header, optionally creates gperf lookup code, builds static libs, builds shared libs with `__so_start` entry and `.interp` loader data, tests executable shared libs and `cap_test`, and installs headers/libraries/pkg-config metadata.

State/persistence: creates object files, archives, shared libs/symlinks, generated headers, gperf output, loader text, pkg-config files, and install tree files.

Dependencies/integration: C compiler/linker/ar/ranlib/objcopy/sed/egrep, optional gperf, top-level psx sources, libcap headers, and packaging paths.

Risks: generated-name correctness depends on UAPI regex; executable shared-object trick is linker/loader sensitive; install symlink logic must match soname versioning; shared build depends on loader extraction from `empty`.

Test signals: `make -C libcap test`, `./libcap.so --summary`, `./libpsx.so`, `cap_test PASS`, staged install and pkg-config checks.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/libcap/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/libcap/_makenames.c -->
## sources/security-integrity/libcap/libcap/_makenames.c

Purpose: build-time generator that turns `cap_names.list.h` into `cap_names.h`, defining capability count, maximum name size, and optional name array.

Important APIs/functions: generated `list[]`, helper `recalloc()`, and `main()`.

Control flow: scans list entries to find highest capability index and longest name, grows a sparse pointer array, emits a generated-file header, `__CAP_BITS`, `__CAP_NAME_SIZE`, and `LIBCAP_CAP_NAMES` array with `NULL` placeholders for unused indices.

State/persistence: writes generated C preprocessor output to stdout; Makefile redirects to `cap_names.h`.

Dependencies/integration: `cap_names.list.h` generated from UAPI header, C build compiler, libcap internal `cap_text.c` and `libcap.h`.

Risks: `recalloc` uses int byte counts and assumes growth sizes are small; malformed duplicate indices overwrite earlier names silently.

Test signals: `make -C libcap cap_names.h`, compile `cap_text.o`, and `go/Makefile` `good-names.go` diff.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/libcap/_makenames.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/libcap/cap_alloc.c -->
## sources/security-integrity/libcap/libcap/cap_alloc.c

Purpose: allocation, duplication, initialization, and freeing support for `cap_t`, `cap_iab_t`, launcher objects, and libcap-managed strings.

Important APIs/functions: constructor `_libcap_initialize()`, `cap_max_bits()`, `_libcap_strdup()`, `cap_init()`, `cap_dup()`, `cap_iab_init()`, `cap_iab_dup()`, `cap_new_launcher()`, `cap_func_launcher()`, and `cap_free()` in the latter part of the file.

Control flow: constructor initializes syscall routing and discovers runtime kernel capability count via `cap_get_bound` binary search. Allocators allocate a tagged `struct _cap_alloc_s` envelope, set magic/size, initialize kernel capability version, and return the embedded public opaque pointer. Duplicators validate magic, allocate a new object, lock/copy source content, and unlock. Launcher creation stores argv/env/callback fields and security-change flags. `cap_free()` validates back-pointer magic and releases strings, cap sets, IABs, and launchers.

State/persistence: process-global `_cap_max_bits` and init mutex; heap-managed opaque objects with magic tags; no persistent files.

Dependencies/integration: `libcap.h` internals, `cap_set_syscall`, `cap_get_bound`, kernel `capget`, atomic mutex macros. Public APIs declared in `sys/capability.h`.

Risks: callers must free only libcap-managed pointers; global initialization is constructor-order sensitive; `cap_proc_root` strings use same freeing contract; launcher stores argv/env pointers rather than deep-copying all arrays, so caller lifetimes matter.

Test signals: `cap_test` allocation/free bad-pointer checks, launcher allocation tests, and leak/error-path tests for `cap_free` on all magic types.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/libcap/cap_alloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/libcap/cap_extint.c -->
## sources/security-integrity/libcap/libcap/cap_extint.c

Purpose: converts capability sets between libcap's internal `cap_t` and portable external binary representation.

Important APIs/functions: `cap_size()`, `cap_copy_ext()`, `cap_copy_int()`, `cap_copy_int_check()`, internal `_cap_size_locked()`, and `struct cap_ext_struct`.

Control flow: computes minimal byte width needed across effective/permitted/inheritable sets while preserving a historic minimum, exports magic/version length plus per-byte little-endian stacked flag data, imports by validating magic and reconstructing u32 flag blocks, and check-import validates the supplied length before delegating.

State/persistence: caller-provided buffers and newly allocated `cap_t`; no persistent state.

Dependencies/integration: internal `cap_t` layout from `libcap.h`; public binary APIs used by Go/C compatibility tests.

Risks: `cap_copy_int()` intentionally trusts the external length and can overread malformed input; callers should prefer `cap_copy_int_check()`. Export returns `EINVAL` when destination is too short rather than required size.

Test signals: `compare-cap.go` C/Go binary round trips, malformed length tests for `cap_copy_int_check`, and capsets with high-numbered bits.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/libcap/cap_extint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/libcap/cap_file.c -->
## sources/security-integrity/libcap/libcap/cap_file.c

Purpose: reads and writes Linux file capability xattrs for path and file-descriptor APIs.

Important APIs/functions: `cap_get_fd()`, `cap_get_file()`, `cap_set_fd()`, `cap_set_file()`, `cap_get_nsowner()`, `cap_set_nsowner()`, internals `_fcaps_load()` and `_fcaps_save()`.

Control flow: get paths allocate a `cap_t`, read `security.capability` xattrs into `vfs_ns_cap_data`, validate revision/size, convert endian fields, and set effective bits when the file effective flag is present. Set paths validate regular non-symlink files, convert internal caps to VFS v1/v2/v3 format, enforce all-or-none effective flag semantics, and set/remove xattrs. `cap_set_file()` first uses `O_RDONLY|O_NOFOLLOW`; if unreadable, it opens `O_PATH|O_NOFOLLOW`, validates with `fstat`, and writes via `/proc/self/fd/<fd>` to avoid filename replacement races.

State/persistence: persists file xattrs and namespace rootid in v3 capabilities; mutates caller `cap_t` rootid for namespace owner setters.

Dependencies/integration: Linux xattr syscalls, VFS capability UAPI structs, byte-order handling, `/proc/self/fd`, regular file semantics.

Risks: the `cap_get_file()` short-read branch contains a duplicated `cap_free(result)` call, which is a potential double-free if reached; file xattr writes require careful privilege and filesystem support; `O_PATH` fallback depends on procfs availability.

Test signals: path/fd get/set/remove tests, symlink/non-regular rejection, rootid v3 round trips, unreadable regular-file path race tests, and `compare-cap.go` file capability checks.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/libcap/cap_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/libcap/cap_flag.c -->
## sources/security-integrity/libcap/libcap/cap_flag.c

Purpose: implements in-memory manipulation and comparison of `cap_t` flags and `cap_iab_t` vectors.

Important APIs/functions: `cap_get_flag`, `cap_set_flag`, `cap_clear`, `cap_clear_flag`, `cap_compare`, `cap_fill_flag`, `cap_fill`, `cap_iab_get_vector`, `cap_iab_set_vector`, `cap_iab_fill`, and `cap_iab_compare`.

Control flow: validates opaque object magic, capability indices, flag/vector enums, and requested values; locks objects while reading/writing bitsets; compares cap sets by duplicating one side to avoid lock-order deadlock; IAB vector setters enforce invariants where ambient implies inheritable and clearing inheritable clears ambient.

State/persistence: mutates only heap `cap_t`/`cap_iab_t` objects; no kernel state until other APIs apply them.

Dependencies/integration: internal bit macros from `libcap.h`, cap max bit discovery, public comparison macros `CAP_DIFFERS` and `CAP_IAB_DIFFERS`.

Risks: `cap_set_flag` skips invalid array entries instead of failing after initial validation of count/set/value mode; callers may assume stronger validation. IAB vector semantics are subtle because `CAP_IAB_BOUND` stores bits to drop, not bits to keep.

Test signals: `cap_test` flag fill/compare cases, IAB text/process round trips, invalid enum/index tests, and concurrent access stress for lock behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/libcap/cap_flag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/libcap/cap_proc.c -->
## sources/security-integrity/libcap/libcap/cap_proc.c

Purpose: process capability, securebits, ambient/bounding, POSIX-thread syscall routing, IAB application, UID/GID helpers, and privileged launcher implementation.

Important APIs/functions: `cap_set_syscall`, `cap_get_proc`, `cap_set_proc`, `capgetp`, `cap_get_pid`, `capsetp`, `cap_get_bound`, `cap_drop_bound`, `cap_get_ambient`, `cap_set_ambient`, `cap_reset_ambient`, `cap_get_secbits`, `cap_set_secbits`, `cap_prctl`, `cap_prctlw`, `cap_set_mode`, `cap_get_mode`, `cap_setuid`, `cap_setgroups`, `cap_iab_get_proc`, `cap_iab_set_proc`, launcher setters, `_cap_chroot`, `_cap_launch`, and `cap_launch`.

Control flow: wraps raw syscalls in `syscaller_s` so libpsx can replace single-thread calls with all-thread semantics. Process getters/setters use `capget/capset`. Mode setting raises `CAP_SETPCAP`, clears ambient, locks securebits, drops bounding bits for no-priv, and clears effective caps before return. UID/GID helpers temporarily raise `CAP_SETUID`/`CAP_SETGID`, set keepcaps/groups/uids, then clear effective caps. IAB setters adjust inheritable first, optionally raise `CAP_SETPCAP`, reset and raise ambient, and drop bounding bits. Launcher forks with an error pipe, runs callback and requested credential/mode/IAB/chroot changes in the child, then execs or exits for function launch.

State/persistence: mutates kernel process/thread capability state, securebits, bounding and ambient sets, uid/gid/groups, chroot/cwd, child processes, and process name.

Dependencies/integration: Linux syscalls/prctl, libpsx weak/strong syscall override, pthread-aware semantics, `sys/securebits.h`, `fork`, `execve`, `pipe2`, and wait/error propagation.

Risks: security-critical sequencing; privilege drops often irreversible. Launcher stores caller-provided argv/env pointers, so lifetimes must outlive launch. Parent reports child setup failure through errno pipe but successful exec returns only PID.

Test signals: `cap_test`, Go `try-launching`, `b210613`, `b215283`, `iaber`, `setid`, psx signal/deadlock tests, and privileged mode/UID/GID/IAB integration tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/libcap/cap_proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/libcap/cap_syscalls.c -->
## sources/security-integrity/libcap/libcap/cap_syscalls.c

Purpose: weak fallback for `psx_load_syscalls()` when libcap is not linked with libpsx.

Important APIs/functions: weak `psx_load_syscalls()` and internal `_libcap_overrode_syscalls`.

Control flow: when called with syscall function pointer slots, simply sets `_libcap_overrode_syscalls = 0`; if libpsx is linked, its strong symbol overrides this fallback and installs all-thread syscall wrappers instead.

State/persistence: mutates one process-global internal flag.

Dependencies/integration: `cap_proc.c` constructor path calls `cap_set_syscall(NULL,NULL)`, which calls this symbol.

Risks: correctness of POSIX thread semantics depends on link resolution; without libpsx, libcap falls back to libc/raw single-thread semantics.

Test signals: build with and without libpsx/pthreads, verify `_libcap_overrode_syscalls` behavior indirectly through psx tests and threaded UID/cap changes.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/libcap/cap_syscalls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/libcap/cap_test.c -->
## sources/security-integrity/libcap/libcap/cap_test.c

Purpose: built-in C regression executable for core libcap allocation, bit discovery, flag manipulation, launcher allocation, proc-root management, and prctl error behavior.

Important APIs/functions: `test_cap_bits`, `test_cap_flags`, `test_short_bits`, `test_alloc`, `test_prctl`, helper `noop`, and `main`.

Control flow: validates binary-search max-bit logic over sample values, exercises cap flag set/fill/compare/clear behavior, checks text buffer size assumptions, allocates/free-tests `cap_t`, `cap_iab_t`, and launchers including bad-pointer rejection, tests `cap_proc_root()` replacement/free contract, and checks `cap_get_bound(-1)` returns `EINVAL`.

State/persistence: creates and frees libcap heap objects and changes process proc-root global; no kernel state except prctl read.

Dependencies/integration: internal `libcap.h`, public libcap APIs, built by `libcap/Makefile`.

Risks: not exhaustive for file/process mutating APIs; some failure paths return early without freeing every prior allocation in the test itself.

Test signals: `make -C libcap test` expects `cap_test PASS`; failures print named test sections.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/libcap/cap_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/libcap/cap_text.c -->
## sources/security-integrity/libcap/libcap/cap_text.c

Purpose: parses and renders textual capability and IAB formats, maps names to numeric values, reports mode names, manages proc-root override, and reads IAB from `/proc/<pid>/status`.

Important APIs/functions: `cap_from_text`, `cap_to_text`, `cap_from_name`, `cap_to_name`, `cap_mode_name`, `cap_iab_to_text`, `cap_iab_from_text`, `cap_proc_root`, `cap_iab_get_pid`, plus helpers `lookupname`, `forceall`, `_parse_vec_string`.

Control flow: text parser tokenizes capability clauses with `all`, named or numeric values and `+/-/=` operations over e/i/p flags. Renderer builds a compact canonical form by histogramming state combinations and naming deviations. IAB text uses prefixes `!` for bounding drops, `^` for ambient+inheritable, and `%` for inheritable with bounding. `/proc` IAB reader parses `CapInh`, `CapBnd`, and `CapAmb` hex vectors from status, inverting bounding to libcap's drop-bit representation.

State/persistence: allocates returned strings/IAB/cap sets; process-global `_cap_proc_dir` controls proc root and is cleaned by destructor.

Dependencies/integration: generated `cap_names.h`, optional gperf output, `/proc`, public text ABI used by capsh, Go compatibility, and docs.

Risks: parser is compact and format-sensitive; global proc root setter is documented not thread-safe; `cap_to_name` returns numeric strings for unknown values.

Test signals: `cap_test` buffer/name assumptions, Go `compare-cap` text round trips, capsh text parsing tests, and `/proc` fixture tests for `cap_iab_get_pid`.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/libcap/cap_text.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/libcap/empty.c -->
## sources/security-integrity/libcap/libcap/empty.c

Purpose: minimal executable used by the Makefile to extract the dynamic loader `.interp` string for executable shared-library support.

Important APIs/functions: `main()` returns 0.

Control flow: immediate success.

State/persistence: no runtime state; build uses resulting binary with `objcopy --dump-section .interp`.

Dependencies/integration: C compiler, linker, `objcopy`, `libcap/Makefile` `loader.txt` target.

Risks: if built statically or with unusual linker options, `.interp` may be absent and shared-object executability metadata generation fails.

Test signals: `make -C libcap loader.txt` and verify `loader.txt` contains a dynamic loader path.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/libcap/empty.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/libcap/execable.c -->
## sources/security-integrity/libcap/libcap/execable.c

Purpose: executable entry body embedded in `libcap.so` so the shared library can print version/help/summary when run directly.

Important APIs/functions: `usage()`, `summary()`, and `SO_MAIN` from `execable.h`. Uses `cap_max_bits`, `cap_get_mode`, `cap_mode_name`, `cap_to_name`, and `cap_free`.

Control flow: prints library version/license/homepage, handles `--usage`/`--help` by printing usage, handles `--summary` by reporting current mode and comparing libcap-known capabilities with running-kernel supported capabilities.

State/persistence: reads process capability mode and kernel bounds; no persistent writes.

Dependencies/integration: compiled with `LIBRARY_VERSION` and `SHARED_LOADER`, included into shared-lib magic object by `libcap/Makefile`.

Risks: executable shared-library behavior is loader/linker sensitive; summary depends on runtime kernel capability count.

Test signals: `./libcap.so`, `./libcap.so --usage`, `./libcap.so --help`, and `./libcap.so --summary` from `libcapsotest`.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/libcap/execable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/libcap/execable.h -->
## sources/security-integrity/libcap/libcap/execable.h

Purpose: macro/header machinery for making a shared object directly executable through a custom `__so_start` entry and embedded interpreter path.

Important APIs/macros/functions: `__execable_dl_loader` in `.interp`, weak `_IO_stdin_used` for glibc, `__execable_parse_args()`, `__SO_FORCE_ARG_ALIGNMENT`, `EXECABLE_INITIALIZE`, and `SO_MAIN`.

Control flow: `__so_start` reconstructs argv from `/proc/self/cmdline`, runs optional initialization, calls the file's static `__execable_main`, frees reconstructed argv memory, and exits. Argument parsing reads cmdline into a growing buffer and splits NUL-delimited entries.

State/persistence: allocates temporary argv memory; embeds loader path in the shared object; reads `/proc/self/cmdline`.

Dependencies/integration: Linux procfs, ELF `.interp`, glibc compatibility symbol, compiler attributes, Makefile-provided `SHARED_LOADER`.

Risks: Linux/ELF-specific and assumes `/proc` availability; direct shared-object execution can be fragile across loaders/architectures; argv reconstruction exits process on allocation failure.

Test signals: direct execution tests for `libcap.so`, `libpsx.so`, and `pam_cap.so`; run with/without arguments under glibc targets.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/libcap/execable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/libcap/include/sys/capability.h -->
## sources/security-integrity/libcap/libcap/include/sys/capability.h

Purpose: primary public C API header for libcap capability, IAB, process, file, text, mode, prctl, UID/GID, launcher, and low-level syscall interfaces.

Important APIs/types: `cap_t`, `cap_value_t`, `cap_flag_t`, `cap_iab_vector_t`, `cap_iab_t`, `cap_flag_value_t`, `cap_mode_t`, `cap_launch_t`, `LIBCAP_MAJOR/MINOR`, and declarations for `cap_init/free/dup`, flag APIs, file APIs, proc APIs, ambient/bounding, external/text conversion, IAB APIs, `cap_set_syscall`, mode/secbits/prctl, UID/GID wrappers, launcher setters, `capget/capset`, and deprecated `capgetp/capsetp`.

Control flow: header-only declarations and constants; includes Linux UAPI capability definitions after defining `__user`.

State/persistence: no runtime state, but defines ownership contracts for opaque heap objects and process/file mutating calls.

Dependencies/integration: `<linux/capability.h>`, sys/types, stdint, C++ extern guards. Consumed by libcap clients, PAM module, C tests, and cgo.

Risks: ABI stability is critical; opaque pointers require callers to use `cap_free`; `cap_proc_root` is explicitly global and not thread-safe to write; deprecated APIs remain exposed.

Test signals: compile public examples against installed header, pkg-config include path checks, and ABI/API comparison across releases.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/libcap/include/sys/capability.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/libcap/include/sys/securebits.h -->
## sources/security-integrity/libcap/libcap/include/sys/securebits.h

Purpose: public compatibility wrapper that exposes Linux securebits definitions through `<sys/securebits.h>`.

Important APIs/types: C++ extern guards, `__user` definition, and inclusion of `<linux/securebits.h>`.

Control flow: header guard then include-only behavior.

State/persistence: none.

Dependencies/integration: bundled or system `linux/securebits.h`; included by code using `SECBIT_*` constants.

Risks: wrapper correctness depends on include path resolving the intended UAPI header; minimal content means all semantic drift is in the UAPI copy.

Test signals: compile code using `SECBIT_NOROOT`, `SECBIT_NO_SETUID_FIXUP`, and related locks via installed headers.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/libcap/include/sys/securebits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/libcap/include/uapi/linux/capability.h -->
## sources/security-integrity/libcap/libcap/include/uapi/linux/capability.h

Purpose: bundled Linux UAPI capability definitions used to keep libcap independent of system kernel headers and aligned with upstream capability numbering.

Important APIs/types/constants: capability version constants, `__user_cap_header_struct`, `__user_cap_data_struct`, VFS capability xattr revisions/sizes, `struct vfs_cap_data`, `struct vfs_ns_cap_data`, named `CAP_*` values through `CAP_CHECKPOINT_RESTORE`, `CAP_LAST_CAP`, `cap_valid`, `CAP_TO_INDEX`, and `CAP_TO_MASK`.

Control flow: header definitions only; kernel/user conditional defines default legacy version for userspace.

State/persistence: defines binary ABI layouts for capget/capset and file xattrs.

Dependencies/integration: included by public `sys/capability.h`, parsed by `libcap/Makefile` to generate `cap_names.list.h`, compared by `distcheck.sh`.

Risks: must track upstream Linux exactly for capability numbers and xattr structs; stale `CAP_LAST_CAP` causes missing names and tests to warn/fail.

Test signals: `distcheck.sh`, generated `cap_names.h`, `capsh --summary`, and compile/runtime tests against kernels with newer/older capability counts.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/libcap/include/uapi/linux/capability.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/libcap/include/uapi/linux/prctl.h -->
## sources/security-integrity/libcap/libcap/include/uapi/linux/prctl.h

Purpose: bundled subset of Linux `prctl` constants and structs required by libcap for process security state manipulation.

Important APIs/types/constants: `PR_SET_KEEPCAPS`, `PR_CAPBSET_READ`, `PR_CAPBSET_DROP`, `PR_GET_SECUREBITS`, `PR_SET_SECUREBITS`, `PR_SET_NO_NEW_PRIVS`, `PR_CAP_AMBIENT` and ambient subcommands, plus many adjacent `PR_*` definitions and `struct prctl_mm_map`.

Control flow: header constants only.

State/persistence: defines numeric ABI for `prctl()` calls used by `cap_proc.c`.

Dependencies/integration: Linux types header; used when system headers are unavailable or for bundled consistency.

Risks: stale or incorrect numeric constants would corrupt security-state calls; the file is not a complete modern prctl header beyond this snapshot.

Test signals: build libcap against bundled headers, run mode/ambient/bounding tests, and compare with system `linux/prctl.h` for relevant constants.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/libcap/include/uapi/linux/prctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/libcap/include/uapi/linux/securebits.h -->
## sources/security-integrity/libcap/libcap/include/uapi/linux/securebits.h

Purpose: bundled Linux securebits constants that control root privilege semantics, setuid fixup, keepcaps, and ambient capability raising.

Important APIs/constants: `issecure_mask`, `SECUREBITS_DEFAULT`, `SECURE_NOROOT`, `SECBIT_NOROOT`, `SECURE_NO_SETUID_FIXUP`, `SECBIT_NO_SETUID_FIXUP`, `SECURE_KEEP_CAPS`, `SECBIT_KEEP_CAPS`, `SECURE_NO_CAP_AMBIENT_RAISE`, `SECBIT_NO_CAP_AMBIENT_RAISE`, `SECURE_ALL_BITS`, and `SECURE_ALL_LOCKS`.

Control flow: header definitions only.

State/persistence: defines bit layout passed to `PR_SET_SECUREBITS` and read from `PR_GET_SECUREBITS`.

Dependencies/integration: included via `sys/securebits.h` and used by `cap_proc.c` mode logic.

Risks: incorrect bit positions would be catastrophic for privilege behavior; comments describe security semantics and must stay aligned with kernel.

Test signals: `cap_set_mode`/`cap_get_mode` tests, `b215283.go`, and direct securebits set/get checks.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/libcap/include/uapi/linux/securebits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/libcap/libcap.h -->
## sources/security-integrity/libcap/libcap/libcap.h

Purpose: private internal header defining libcap object layouts, magic values, locking primitives, capability bit macros, generated name integration, syscall hooks, launcher internals, and validation helpers.

Important APIs/types/macros: `_cap_struct`, `cap_iab_s`, `cap_launch_s`, `CAP_T_MAGIC`, `CAP_S_MAGIC`, `CAP_IAB_MAGIC`, `CAP_LAUNCH_MAGIC`, `_cap_mu_*` locks, `raise_cap/lower_cap/isset_cap`, `LIBCAP_EFF/INH/PER`, debug macros, `psx_load_syscalls`, `EXECABLE_INITIALIZE`, static assertion support, and `good_cap_*` validation helpers in the later part of the file.

Control flow: compile-time selection validates kernel capability version constants, defines internal data representations and helper macros used by all `.c` files.

State/persistence: describes heap object memory layout and process-global syscall override flag; no standalone runtime code except declarations/macros.

Dependencies/integration: public `sys/capability.h`, generated `cap_names.h`, scheduler/yield for spin locks, optional psx library, executable shared-object support.

Risks: internal ABI offset is coupled to allocation/free logic; lock macros are minimal spin locks, not full pthread mutexes; generated header mismatch stops compilation or causes name/text errors.

Test signals: full libcap compile, `cap_test`, sanitizer builds around `cap_free`/validation, and shared-object execution tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/libcap/libcap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/libcap/libcap.pc.in -->
## sources/security-integrity/libcap/libcap/libcap.pc.in

Purpose: pkg-config template for installed libcap.

Important fields: `prefix`, `exec_prefix`, `libdir`, `includedir`, `Name`, `Description`, `Version`, `Libs`, `Libs.private`, and `Cflags`.

Control flow: `libcap/Makefile` substitutes install paths, version, and private deps using sed to create `libcap.pc`.

State/persistence: template only; generated `.pc` file is installed.

Dependencies/integration: pkg-config consumers, Makefile substitution variables.

Risks: incorrect `Libs.private` or include path breaks static consumers; version substitution must match library soname release.

Test signals: `pkg-config --cflags --libs libcap` and static-link consumer build from staged install.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/libcap/libcap.pc.in -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/libcap/libpsx.pc.in -->
## sources/security-integrity/libcap/libcap/libpsx.pc.in

Purpose: pkg-config template for installed libpsx, including special linker flags needed to force the psx archive into consumers.

Important fields: standard pkg-config variables plus `Libs` using `--no-as-needed`, `--whole-archive -lpsx`, `--no-whole-archive`, `--as-needed`, and `-lpthread`.

Control flow: substituted by `libcap/Makefile` to produce `libpsx.pc`.

State/persistence: template only; generated `.pc` file is installed.

Dependencies/integration: pkg-config, linker behavior for static archive constructors/wrappers, pthreads.

Risks: linker flag ordering is critical; distributions/toolchains may handle whole-archive/as-needed differently.

Test signals: build threaded consumer using `pkg-config --libs libpsx`, verify libpsx overrides libcap syscall hooks at runtime.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/libcap/libpsx.pc.in -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/libcap/psx_exec.c -->
## sources/security-integrity/libcap/libcap/psx_exec.c

Purpose: executable entry body for `libpsx.so` when run directly.

Important APIs/functions: `SO_MAIN` from `execable.h`.

Control flow: prints the invoked command/library version, license note, and homepage.

State/persistence: no mutable state.

Dependencies/integration: compiled with `LIBRARY_VERSION` and `SHARED_LOADER` into `psx_magic.o` by `libcap/Makefile`.

Risks: depends on executable shared-object machinery; no option handling beyond printing.

Test signals: `./libpsx.so` from `libpsxsotest`.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/libcap/psx_exec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/pam_cap/Makefile -->
## sources/security-integrity/libcap/pam_cap/Makefile

Purpose: builds, installs, links, and tests the `pam_cap.so` PAM module and associated executable-shared-object behavior.

Important targets/variables: `all`, `install`, `execable.o`, `LIBCAP`, `pam_cap.so`, `pam_cap_linkopts`, `lazylink.so`, `test_pam_cap`, `testlink`, `incapable.conf`, `test`, `sudotest`, and `clean`.

Control flow: includes `Make.Rules`, forces PIC, builds libcap dependency, compiles executable-shared-object wrapper with loader text, determines whether `pam_cap.so` must link `-lpam` using `FORCELINKPAM` or `lazylink.so` probe, links the module with libcap, builds static and dynamic tests, creates an intentionally writable config for tests, runs module-as-executable checks, and privileged config cases under sudo.

State/persistence: creates module/test objects, `pam_cap_linkopts`, `lazylink.so`, `test_pam_cap`, `testlink`, and `incapable.conf`; installs into `$(LIBDIR)/security`.

Dependencies/integration: PAM headers/libs, libcap, executable shared-object support, loader text from libcap, sudo for privileged tests.

Risks: link behavior varies by distribution PAM packaging; `incapable.conf` is world-writable for test purposes and must not be installed; static test avoids `LDFLAGS` intentionally.

Test signals: `make -C pam_cap test`, direct `LD_LIBRARY_PATH=../libcap ./pam_cap.so --help`, and `make -C pam_cap sudotest` expected capability vectors.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/pam_cap/Makefile -->

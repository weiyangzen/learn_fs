# Research: subset-b-009170

Grouped research for the rsync source files in work item `subset-b-009170`. Each section is bounded by the required reconciliation markers and preserves the original source path in its title.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/options.c -->
# Research: sources/sync-backup/rsync/options.c

## Purpose
`options.c` is rsync's central command-line and daemon-socket option parser. It defines the global option state consumed throughout the program, maps user-facing options into that state via popt, validates option combinations, parses daemon-only options, and serializes a filtered option set for the remote server side. It also handles rsync-specific compatibility mechanics such as protocol feature flags, argument protection, daemon refuse-options, `--info`/`--debug` verbosity words, and hostspec parsing.

## Important APIs, Types, and Functions
- Global option variables: transfer behavior (`whole_file`, `append_mode`, `inplace`, `delete_*`, `files_from`), metadata preservation (`preserve_*`), daemon/client roles (`am_server`, `am_sender`, `am_daemon`, `am_chrooted`), logging/output (`verbose`, `info_levels`, `debug_levels`, `stdout_format`, `logfile_format`), protocol/compression/checksum choices, and remote command construction state (`remote_options`, `basis_dir`, `alt_dest_type`).
- `struct output_struct`, `info_words`, and `debug_words` define named output categories, default/user/help/limit priorities, and the client/server/sender/receiver locations where each word applies.
- `parse_arguments(int *argc_p, const char ***argv_p)` is the main parser. It mutates global rsync option state and may replace the argv array with leftover positional arguments.
- `server_options(char **args, int *argc_p)` emits the option vector sent to the remote rsync process, using short option packing where safe and long options for features needing explicit values.
- `safe_arg()` shell-quotes or protocol-quotes option and filename arguments depending on `protect_args`, `old_style_args`, sender trust, and wildcard handling.
- `set_refuse_options()`, `parse_one_refuse_match()`, and `create_refuse_error()` implement daemon and build-feature option refusal.
- `parse_size_arg()` parses size suffixes for block size, max/min size, bwlimit, and max allocation. `parse_time()` handles `--stop-at` when `mktime()` is available.
- `check_for_hostspec()` and `parse_hostspec()` parse `host:path`, `host::module`, and `rsync://host[:port]/path` syntaxes, including IPv6 literals.

## Control Flow
Startup initializes global defaults, builds popt option tables, then `parse_arguments()` calls `set_refuse_options()` before creating a popt context. Normal parsing loops over `poptGetNextOpt()` return values and handles special options in a large switch. `--daemon` restarts parsing against the smaller daemon option table, processes `--dparam`, validates daemon-only conditions, and returns early with `am_daemon` set. `--server` similarly restarts parsing without aliases so server and daemon control options cannot be hidden by user aliases.

After popt returns EOF, the parser performs a second validation/normalization pass: environment defaults (`RSYNC_MAX_ALLOC`, `RSYNC_OLD_ARGS`, `RSYNC_PROTECT_ARGS`, `RSYNC_PARTIAL_DIR`, `RSYNC_ICONV`), checksum/compression negotiation, output verbosity expansion, feature checks, conflict checks, delete-mode selection, daemon-filter validation for option paths, backup suffix/dir derivation, log format setup, bwlimit conversion, inplace/append partial-file rules, `--files-from` opening, and trust flags for sender arguments/filters. Errors are stored in `err_buf` and returned as failure; `option_error()` later reports them.

`server_options()` runs after local option parsing. It compacts compatible options into a `-...` argument, appends protocol feature flags via `maybe_add_e_option()`, then conditionally appends long options that the remote side needs. It uses sender/receiver role checks to avoid leaking client-only choices, preserves compatibility aliases such as `--log-format`, and inserts remote options after validating argument count limits.

## State and Persistence
The file is mostly process-global state. Parsing mutates globals that other modules read directly; no durable state is written except indirectly via opened `filesfrom_fd`, initialized logs, and copied argv buffers. `remote_options`, `basis_dir`, `max_alloc_arg`, and many string options retain pointers into popt-copied or allocated memory. The `err_buf` static buffer persists the last parse error. Daemon refusal mutates the in-memory `long_options` table by temporarily abusing `descrip` and rewriting `argInfo`/`val` for refused options.

## Dependencies and Integration Points
The parser depends on rsync core headers, popt, filter parsing, logging, protocol constants, chmod parsing, checksum/compression negotiation, daemon config lookups (`lp_refuse_options`, `lp_charset`), path sanitization/filter checks, and system feature macros. It integrates with `pipe.c` through `remote_options` and `parse_arguments()` in local child startup, with client/server startup through `server_options()`, with daemon config through refuse/filter logic, and with many runtime modules via the exported global flags.

## Risks
This file has high blast radius because option state controls filesystem access, delete behavior, daemon security, protocol compatibility, and argument quoting. Risks include stale refusal coverage when new options are added, subtle conflicts between implied options and daemon-refused options, unsafe quoting if `protect_args`/`old_style_args` cases regress, integer/suffix parsing edge cases, and mutable popt table state leaking between daemon/non-daemon parses. Security-sensitive paths include daemon filter validation, `--files-from` host handling, symlink munging safety, and `am_chrooted` semantics for daemon chroot boundaries.

## Test Signals
Useful signals include rsync option tests for archive/delete/inplace/partial conflicts, daemon `refuse options` acceptance/refusal including wildcards and negations, remote-shell argument quoting tests with spaces/wildcards/leading dashes/tildes, `--files-from` local and remote forms, protocol downgrade tests, `--info`/`--debug` round trips, max/min size parsing, and build-matrix tests with feature macros disabled (`ICONV_OPTION`, ACLs, xattrs, hard links, crtimes, `mktime`, `setvbuf`).
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/options.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/packaging/cull-options -->
# Research: sources/sync-backup/rsync/packaging/cull-options

## Purpose
`packaging/cull-options` is a Python generator that scans `../options.c` and emits Perl or Python data tables describing the rsync server options that restricted `rrsync` should recognize. It keeps wrapper option policy synchronized with the options that `server_options()` may send.

## Important APIs, Types, and Functions
- Module dictionaries `short_no_arg`, `short_with_num`, and `long_opts` accumulate option names and argument-checking modes.
- `main()` reads `../options.c`, applies regexes against `argstr[x++]`, `asprintf`, literal `args[ac++]`, `safe_arg()`, and `alt_dest_opt()` patterns, then prints generated code between start/end comments.
- `str_assign()` emits either Python assignment syntax or Perl `our $...` syntax based on command-line mode.
- The CLI is `--python` by default with mutually exclusive `--perl`.

## Control Flow
The script seeds tables with known special options, walks `options.c` line by line, infers short options without args, short options with numeric args, long options with no args, long options with inline args, and long options whose next argv element needs path checking. A one-line `last_long_opt` state tracks whether a preceding literal long option is followed by `safe_arg("", value)`. After scanning it forces `files-from` to mode `3`, prints disabled-option settings, then prints a sorted `long_opts` table.

## State and Persistence
State is in-memory only; output goes to stdout for inclusion in generated `rrsync` code. The script depends on being run from `packaging/` or another directory where `../options.c` is the rsync option source.

## Dependencies and Integration Points
It depends on Python `re` and `argparse`, and on the exact formatting/style of `options.c`. Its output is consumed by `rrsync`, so it indirectly protects restricted rsync deployments from unexpected server-side options.

## Risks
The scanner is regex- and style-dependent. New `server_options()` patterns can be missed if they do not match existing regexes, which can make `rrsync` reject valid options or, more seriously, fail to classify an argument-bearing option for path checking. It also hard-codes extra BackupPC options and special disables, so policy drift needs review when option semantics change.

## Test Signals
Run the script after option changes and diff the generated block in `rrsync`. Add tests that introduce representative `server_options()` additions with no arg, inline arg, split path arg, short numeric arg, and alt-dest return paths. Restricted `rrsync` integration tests should cover subdir path checking for `--files-from`, alt-dest, and backup/temp/partial path arguments.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/packaging/cull-options -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/packaging/pkglib.py -->
# Research: sources/sync-backup/rsync/packaging/pkglib.py

## Purpose
`packaging/pkglib.py` is a shared Python helper library for rsync packaging and release scripts. It wraps subprocess execution, git state checks, generated-file discovery, and version/protocol parsing from rsync source files.

## Important APIs, Types, and Functions
- `warn()` and `die()` are stderr/error-exit helpers.
- `_tweak_opts()` centralizes subprocess defaults: `shell=True` for string commands, UTF-8 encoding unless `raw=True`, capture modes, and discard modes.
- `cmd_run()`, `cmd_chk()`, `cmd_txt()`, `cmd_txt_chk()`, and `cmd_pipe()` provide common subprocess patterns.
- `check_git_status()` and `check_git_state()` validate branch/cleanliness, with optional extra checkout handling.
- `latest_git_hash()` and `get_patch_branches()` inspect git history/branch naming.
- `get_gen_files()` reads `GENFILES` from `auto-build-save/<branch>/Makefile`.
- `get_rsync_version()`, `get_NEWS_version_info()`, and `get_protocol_versions()` parse `version.h`, `NEWS.md`, and `rsync.h`.

## Control Flow
Most helpers are leaf routines. Subprocess wrappers call `_tweak_opts()` then `subprocess.run()` or `Popen()`. Git checks run command-line git, parse status text, and may prompt before proceeding if branch expectations differ. Version helpers open source files and regex-match defines or NEWS table rows, exiting via `die()` if required signals are absent.

## State and Persistence
The only module-level state is `default_encoding`. `set_default_encoding()` attempts to change it, but because it does not declare `global default_encoding`, it currently creates a local variable and does not update module state. Other functions are stateless except for subprocess side effects and user prompts.

## Dependencies and Integration Points
The library is imported by `packaging/release.py` and likely other packaging scripts. It assumes an rsync source checkout with git available and specific source-file formats. `get_gen_files()` integrates with `prep-auto-dir`'s branch-specific `auto-build-save` layout.

## Risks
The subprocess wrapper defaults string commands to shell execution, so callers must not pass unsanitized input as a string. Git status parsing is text-format dependent. Interactive prompts in `check_git_state()` can block automation. `set_default_encoding()` is a likely bug if callers expect it to disable or change encoding globally. `get_gen_files()` assumes a generated Makefile exists in the auto-build directory.

## Test Signals
Unit tests can monkeypatch subprocess calls to verify capture/discard/raw options, branch parsing, and error propagation. Fixture tests should cover `version.h`, `rsync.h`, `NEWS.md`, and Makefile `GENFILES` parsing. A regression test should assert `set_default_encoding(None)` changes later subprocess behavior if that function is intended to work.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/packaging/pkglib.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/packaging/prep-auto-dir -->
# Research: sources/sync-backup/rsync/packaging/prep-auto-dir

## Purpose
`packaging/prep-auto-dir` manages rsync's branch-specific auto build directory. It moves the real `build` directory in and out of `auto-build-save/<branch>`, preserving a stable real `build` path for ccache efficiency while keeping branch-specific build artifacts separated.

## Important APIs, Types, and Functions
This POSIX shell script has no functions. Key variables are `auto_top=auto-build-save`, `desired_branch` from `git rev-parse --abbrev-ref HEAD | tr / %`, `auto_dir`, and `cur_branch` from `build/.branch`.

## Control Flow
If `auto-build-save` and `.git` both exist, the script determines the current branch, rejects detached HEAD, compares it to the branch currently represented by `build/.branch`, and if they differ moves the current `build` directory back under `auto-build-save/<old>`, creates the desired branch directory as needed, makes `.branch` and reverse symlinks, and moves the desired directory to `build`. It also ensures top-level `Makefile` is a symlink to `packaging/auto-Makefile`, then echoes the branch id.

## State and Persistence
It persistently moves directories and symlinks: `build`, `build/.branch`, `auto-build-save/<branch>`, and top-level `Makefile`. It does nothing when the expected auto-build top directory is absent, allowing normal builds.

## Dependencies and Integration Points
It depends on `git`, `readlink`, `mv`, `ln`, and shell utilities. `packaging/smart-make` calls it and switches into `build` when it prints a branch name. `pkglib.get_gen_files()` expects the same `auto-build-save/<branch>` convention.

## Risks
Directory moves are destructive if the layout is manually altered or `.branch` is stale. The script does not quote `$auto_top` in all tests, although the values are controlled. It refuses detached HEAD rather than handling it. Interrupted moves could leave `build` and `auto-build-save` inconsistent.

## Test Signals
Use temporary git repositories to exercise first setup, branch switch, existing build preservation, detached HEAD refusal, and Makefile symlink creation. Verify ccache-sensitive real `build` path stays consistent after switches.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/packaging/prep-auto-dir -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/packaging/release.py -->
# Research: sources/sync-backup/rsync/packaging/release.py

## Purpose
`packaging/release.py` is rsync's step-driven maintainer release workflow. Each `--step-N-*` invocation performs one release action, using `../release` for persistent mirrors, scratch data, and a JSON state file shared across steps.

## Important APIs, Types, and Functions
- Constants define `RELEASE_DIR`, `FTP_DIR`, `HTML_DIR`, `WORK_DIR`, `STATE_FILE`, `HTML_SRC`, remote samba paths, and `GEN_FILES`.
- `STEPS`, `STEP_FLAGS`, and `STEP_FUNCS` implement the step registry.
- State helpers: `load_state()`, `save_state()`, `require_samba_host()`, `require_top_of_checkout()`, `replace_or_die()`, `section()`, `confirm()`.
- Step functions: `step_1_fetch()`, `step_2_prepare()`, `step_3_tweak()`, `step_4_build()`, `step_5_commit()`, `step_6_tag()`, `step_7_tarball()`, `step_8_update_ftp()`, `step_9_toplinks()`, `step_10_push_ftp()`, `step_11_push_html()`, and `step_12_push_git()`.
- `rsync_with_confirm()` wraps dry-run-then-confirm for pushes.

## Control Flow
`main()` parses exactly one step flag or `--list`, installs a SIGINT handler, sets `LESS`, and dispatches to the selected function. Step 1 mirrors ftp/html content from a samba host and snapshots `rsync-web`. Step 2 interactively derives release version, previous version, rpm release, protocol-change metadata, source directories, date strings, and writes `release-state.json`. Step 3 edits version, protocol, NEWS, and spec files, runs `year-tweak`, and shows a diff. Step 4 runs source preparation, configure, build, and `make gen`. Steps 5 and 6 commit and sign a tag. Step 7 creates source tarball and diffs using git archive plus generated files. Step 8 refreshes ftp README/NEWS/INSTALL/html, ChangeLog, and signatures. Step 9 updates top-level hard links for final releases. Steps 10 and 11 push ftp/html after dry runs. Step 12 prints git push and announcement instructions.

## State and Persistence
Persistent state lives in `../release/release-state.json`; release artifacts and mirrors live under `../release/rsync-ftp`, `../release/rsync-html`, and `../release/work`. Several steps modify the source checkout (`version.h`, `rsync.h`, `NEWS.md`, specs, generated files), create git commits/tags, write tarballs/diffs/signatures, and update remote samba directories. The script is intentionally manual and interactive at key gates.

## Dependencies and Integration Points
It imports `pkglib` helpers, calls `rsync`, `git`, `tar`, `gzip`, `fakeroot`, `gpg`, `make`, `configure`, `prepare-source`, `md-convert`, `support/git-set-file-times`, and `packaging/year-tweak`. It expects `RSYNC_SAMBA_HOST` to identify a samba.org host. It integrates with release docs (`NEWS.md`), generated manual/html files, rpm spec files, and the `rsync-web/` subtree.

## Risks
This script performs high-impact filesystem, git, signing, and remote sync operations. Risks include stale format regexes for NEWS/spec/version files, accidental operation on the wrong branch or dirty checkout, interactive prompts blocking unattended use, reliance on external host layout and `.filt` filters, shell-command strings with interpolated paths, and partial release state if a step fails midway. `step_5_commit()` commits all tracked changes with `git commit -a`, so unrelated tracked edits in the checkout would be swept into the release commit.

## Test Signals
Use a disposable checkout with fake `../release`, mocked samba host, and fixture `NEWS.md`/spec files to test step 2 state generation and step 3 rewrites. Dry-run tests for steps 7-9 should verify tarball names, diff paths, generated-file inclusion, and hard-link behavior. Manual release rehearsals should confirm gpg, fakeroot, rsync filters, and html/ftp mirror permissions.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/packaging/release.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/packaging/smart-make -->
# Research: sources/sync-backup/rsync/packaging/smart-make

## Purpose
`packaging/smart-make` is a convenience build wrapper that prepares the source, reruns configure only when `configure.sh` changes, executes `config.status`, builds `make all`, and optionally runs `make check`.

## Important APIs, Types, and Functions
This shell script has no functions. It uses `packaging/prep-auto-dir` to decide whether to build in `build/` with `srcdir=..` or in the source directory with `srcdir=.`.

## Control Flow
The script sets `LANG=C` and `set -e`, calls `prep-auto-dir`, changes into `build` if an auto-build branch is active, snapshots `configure.sh` to `configure.sh.old` or creates an empty placeholder, runs `prepare-source` or `prepare-source fetch` depending on `.fetch`, diffs the new and old `configure.sh`, and reruns either `./config.status --recheck` or `$srcdir/configure` only when needed. It then runs `./config.status`, `make all`, and `make check` when the first argument is `check`.

## State and Persistence
It modifies build outputs, `configure.sh.old`, generated configure/config files, and build artifacts. It relies on `prep-auto-dir` for persistent build-directory state.

## Dependencies and Integration Points
It integrates with `prep-auto-dir`, `prepare-source`, Autoconf-generated `configure.sh`, `config.status`, and Make. It is also referenced by the release workflow as a build-preparation concept, although `release.py` performs its own release-specific configure sequence.

## Risks
The script assumes `configure.sh` changes are the right trigger for reconfigure, which may miss environment or option changes unless `config.status` handles them. It may overwrite `configure.sh.old`. It exits on first failure but does not clean partial build outputs. Running in the wrong directory without expected scripts will fail.

## Test Signals
Exercise no-change and changed-`configure.sh` cases, `.fetch` and non-`.fetch` paths, auto-build and normal layouts, and `check` argument behavior. Confirm that `config.status --recheck` is invoked only when an existing `config.status` and changed configure are present.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/packaging/smart-make -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/packaging/solaris/build_pkg.sh -->
# Research: sources/sync-backup/rsync/packaging/solaris/build_pkg.sh

## Purpose
`packaging/solaris/build_pkg.sh` builds a legacy Solaris package for rsync by staging a fake install tree, generating `pkginfo` and `prototype`, running Solaris packaging tools, and removing the staging tree.

## Important APIs, Types, and Functions
This shell script has no functions. Important variables are `PKGNAME=SMBrsync`, `BASEDIR=/usr/local`, `VERSION="2.5.5"`, `ARCH=$(uname -p)`, `NAME=rsync`, `FAKE_ROOT=$PWD/$PKGNAME`, and `OUTPUTFILE=$PKGNAME-$VERSION-sol8-$ARCH-local.pkg`.

## Control Flow
The script creates `$FAKE_ROOT`, copies the rsync binary, man pages, README, COPYING, and `tech_report.pdf` from relative paths three levels up, writes package metadata with here-documents, runs `pkgmk -d . -r . -f ./prototype -o`, translates the package with `pkgtrans -os`, moves the output package to the original directory, and removes the fake root.

## State and Persistence
It creates and deletes a staging directory named after `PKGNAME`, and leaves the `.pkg` file in the starting directory. It assumes relative path layout under `packaging/solaris/5.8/` as described in comments.

## Dependencies and Integration Points
It depends on Solaris tools `pkgmk` and `pkgtrans`, `uname`, shell utilities, and prebuilt rsync/manual/documentation artifacts. It is independent of modern release automation.

## Risks
The script is stale: version is hard-coded to `2.5.5`, vendor URL is old, paths assume a specific copied location, and unquoted variables could break with spaces. `mkdir $FAKE_ROOT` fails if a stale staging directory exists. It removes `$FAKE_ROOT` recursively, so variable correctness matters.

## Test Signals
On a Solaris-compatible environment, verify staging tree contents, `pkginfo` metadata, `prototype` ownership/modes, package filename, and installability. In CI, shellcheck/static review and a fake-tools dry run can catch quoting and path regressions.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/packaging/solaris/build_pkg.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/packaging/systemd/rsync.service -->
# Research: sources/sync-backup/rsync/packaging/systemd/rsync.service

## Purpose
`packaging/systemd/rsync.service` defines a standalone systemd service for running rsync daemon mode as a long-running process.

## Important APIs, Types, and Functions
The unit has `[Unit]`, `[Service]`, and `[Install]` sections. Key directives are `ConditionPathExists=/etc/rsyncd.conf`, `After=network.target`, `Documentation=man:rsync(1) man:rsyncd.conf(5)`, `ExecStart=/usr/bin/rsync --daemon --no-detach`, `Restart=on-failure`, `ProtectSystem=full`, `PrivateDevices=on`, and `NoNewPrivileges=on`.

## Control Flow
systemd starts this service only when `/etc/rsyncd.conf` exists. The rsync process remains in the foreground due to `--no-detach`; systemd restarts it after failures with a one-second delay. The install target is `multi-user.target`.

## State and Persistence
The unit itself does not store state. Runtime state belongs to systemd and the rsync daemon. It hardens filesystem/device access by making major system paths read-only and hiding devices.

## Dependencies and Integration Points
It integrates with Linux systemd packaging and `/etc/rsyncd.conf`. It conflicts operationally with the socket-activation unit because the socket unit declares a conflict with this service.

## Risks
`ProtectSystem=full` and `PrivateDevices=on` are secure defaults but can break modules that need writes under protected paths or device access; admins must override via drop-ins. The hard-coded `/usr/bin/rsync` path must match package layout. `After=network.target` does not guarantee fully configured network in all environments.

## Test Signals
Package tests should run `systemd-analyze verify`, start the service with a minimal `/etc/rsyncd.conf`, verify foreground daemon behavior, restart-on-failure, and check hardening compatibility for expected module paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/packaging/systemd/rsync.service -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/packaging/systemd/rsync.socket -->
# Research: sources/sync-backup/rsync/packaging/systemd/rsync.socket

## Purpose
`packaging/systemd/rsync.socket` defines systemd socket activation for rsync daemon connections on TCP port 873.

## Important APIs, Types, and Functions
The unit uses `[Socket]` directives `ListenStream=873` and `Accept=true`. The `[Unit]` section declares `Conflicts=rsync.service`, and `[Install]` uses `WantedBy=sockets.target`.

## Control Flow
When enabled, systemd listens on port 873. With `Accept=true`, each accepted connection starts an instance of the matching template service, `rsync@.service`, with the accepted socket passed as standard input.

## State and Persistence
The unit persists only as systemd configuration. Runtime listener state is owned by systemd.

## Dependencies and Integration Points
It integrates with `rsync@.service` by systemd naming convention and conflicts with the standalone `rsync.service` to prevent two listeners on the same port.

## Risks
Port 873 requires appropriate privileges/capabilities. `Accept=true` creates one service instance per connection, so resource limits and daemon config should be reviewed for high-connection environments. Socket activation bypasses the standalone service's `ConditionPathExists` check unless the template has equivalent validation.

## Test Signals
Run `systemd-analyze verify` on the socket and template together, enable/start the socket, connect to port 873, and verify an `rsync@...service` instance is spawned and exits correctly.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/packaging/systemd/rsync.socket -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/packaging/systemd/rsync@.service -->
# Research: sources/sync-backup/rsync/packaging/systemd/rsync@.service

## Purpose
`packaging/systemd/rsync@.service` is the per-connection systemd template used by `rsync.socket` for socket-activated rsync daemon sessions.

## Important APIs, Types, and Functions
Key directives are `ExecStart=-/usr/bin/rsync --daemon`, `StandardInput=socket`, `StandardOutput=inherit`, `StandardError=journal`, `ProtectSystem=full`, `PrivateDevices=on`, and `NoNewPrivileges=on`.

## Control Flow
For each accepted socket connection, systemd starts an instance of this template and attaches the socket to stdin. The leading `-` in `ExecStart` tells systemd to treat non-zero rsync exits as non-fatal for unit failure accounting.

## State and Persistence
No persistent state is written by the unit. Each service instance is transient per connection, with logs going to journald and output inherited as configured.

## Dependencies and Integration Points
It pairs with `rsync.socket` and runs `/usr/bin/rsync --daemon` in socket mode. It shares hardening assumptions with the standalone service.

## Risks
The template lacks `ConditionPathExists=/etc/rsyncd.conf`, so behavior without a config depends on rsync defaults/errors. The `-` prefix can hide failure status from systemd-level monitoring. Hardening may block unusual daemon modules without drop-in overrides.

## Test Signals
Verify socket activation with `systemd-analyze verify`, a real TCP connection, journald logging, expected exit status treatment, and module access under the hardening directives.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/packaging/systemd/rsync@.service -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/packaging/var-checker -->
# Research: sources/sync-backup/rsync/packaging/var-checker

## Purpose
`packaging/var-checker` is a Python maintenance checker for rsync C sources. It reports extraneous `extern` declarations, variables defined but apparently unused, and inconsistent types or array sizes across files.

## Important APIs, Types, and Functions
- Regexes `VARS_RE` and `EXTERNS_RE` find candidate file-scope variables and extern declarations.
- Global dictionaries `types` and `sizes` track cross-file declarations by variable name.
- `main()` locates the source directory, loads helper C files for special test sources, scans all `*.c`, and reports one-reference variables/externs.
- `slurp_file()` reads a file and can strip extern declarations.
- `parse_vars()` normalizes declarations, splits multiple declarators, checks type/size consistency, and returns variable names.

## Control Flow
The script changes to the parent directory if invoked from `packaging/`, reads `syscall.c` and `util1.c` as supplemental text for specific test files, then processes each C file. It parses variable and extern candidate lines, appends supplemental helper text where needed, rewrites macro names that would otherwise confuse usage search, constructs a combined variable-name regex, counts occurrences, and prints variables or externs that occur only in their declaration.

## State and Persistence
It has no file-writing side effects. Cross-file type and size observations persist in module dictionaries for the duration of the run.

## Dependencies and Integration Points
It depends on Python stdlib and rsync C source naming conventions. It is a developer hygiene tool, not part of the runtime build. It integrates with the source tree by assuming `syscall.c` marks the top-level directory.

## Risks
Regex-based C parsing can produce false positives/negatives for complex declarations, macros, function pointers, comments, conditional compilation, or generated uses. The occurrence count treats textual matches as uses and has special-case rewrites for only a few macros. It reports to stdout without structured status.

## Test Signals
Run it before releases or variable refactors and review output manually. Fixture C snippets should cover multiple declarators, pointers, arrays, initialized variables, externs, macro references, and inconsistent declarations.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/packaging/var-checker -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/packaging/year-tweak -->
# Research: sources/sync-backup/rsync/packaging/year-tweak

## Purpose
`packaging/year-tweak` updates `latest-year.h` so the embedded latest copyright year matches the newest git-derived modification year among source files.

## Important APIs, Types, and Functions
The script's `main()` runs `support/git-set-file-times --list`, parses each output line for a year and filename, tracks the maximum year, reads `latest-year.h`, and rewrites it if the `#define LATEST_YEAR "YYYY"` line differs.

## Control Flow
It starts with `latest_year = '2000'`, streams command output from `subprocess.Popen`, regex-parses each line, exits on parse failure, waits for the subprocess, compares the generated one-line header content with the existing file, and writes only when changed.

## State and Persistence
The persistent output is `latest-year.h` in the current directory. It performs no backup. It depends on git-derived file times rather than wall-clock time.

## Dependencies and Integration Points
It depends on `support/git-set-file-times --list` and the format of its output. `release.py` invokes it during the tweak step after editing version/release files.

## Risks
The script does not check the subprocess return code, so a failing `git-set-file-times` that emits no parseable output could leave `latest_year` at `2000` or fail only on malformed lines. It assumes it is run from the rsync checkout root and that `latest-year.h` already exists.

## Test Signals
Use mocked `git-set-file-times --list` output to verify maximum-year selection, parse failures, unchanged-file behavior, and rewrite behavior. Release tests should check that `latest-year.h` changes when a newer source year is present.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/packaging/year-tweak -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/params.c -->
# Research: sources/sync-backup/rsync/params.c

## Purpose
`params.c` is rsync's Windows/INI-like configuration parser, derived from Samba. It tokenizes rsync daemon config files into sections and parameter name/value pairs, handles comments and line continuations, and supports include/merge directives.

## Important APIs, Types, and Functions
- Static parser buffer state: `bufr`, `bSize`, `the_sfunc`, and `the_pfunc`.
- Lexer helpers: `EatWhitespace()`, `EatComment()`, and `Continuation()`.
- Token parsers: `Section()` parses `[section]` names and invokes the section callback; `Parameter()` parses `name = value` lines or directive lines and invokes the parameter callback.
- Include support: `include_config()` handles file or directory includes; `parse_directives()` recognizes `&include` and `&merge`.
- `Parse()` is the main file scanner over blank/comment/section/directive/parameter lines.
- `OpenConfFile()` opens a config file with rsync logging.
- Public entry point `pm_process(char *FileName, BOOL (*sfunc)(char *), BOOL (*pfunc)(char *, char *))`.

## Control Flow
`pm_process()` opens a file, allocates the shared buffer for the outermost call, and calls `Parse()`. `Parse()` reads the first non-newline whitespace-delimited character of each line and dispatches to comment skipping, section parsing, directive parsing, or parameter parsing. `Section()` compresses internal whitespace, supports backslash continuation before the closing bracket, rejects empty names, and calls `sfunc`. `Parameter()` first scans the parameter name until `=` or a directive space/tab after `&`, then scans the value while preserving internal whitespace, stripping CR, trimming trailing whitespace, and supporting backslash continuation. Directives call `include_config()`, which recursively calls `pm_process()` on regular files or sorted `*.conf`/`*.inc` directory entries.

## State and Persistence
The parser uses a single reusable global buffer, growing it in 1024-byte increments. Recursive includes reuse the existing buffer instead of allocating another. Include directives can temporarily notify the section callback with synthetic `]push`, `]reset`, and `]pop` section names when managing globals. The parser itself does not persist config; callbacks own storage.

## Dependencies and Integration Points
It depends on rsync logging/allocation/path helpers, `wildmatch`, `item_list`, directory APIs, and callback implementations elsewhere in rsync daemon configuration handling. `&include` uses `*.conf` and manages global section state; `&merge` uses `*.inc` without global push/pop.

## Risks
The global buffer and callback globals make the parser non-reentrant outside its intended recursive include pattern. Include directory traversal is sorted but can recurse deeply or loop if configs include each other. Regex-free manual parsing must preserve legacy whitespace/continuation behavior. Synthetic section names beginning with `]` are an implicit contract with callback code. Very large config tokens can grow memory without a strict cap.

## Test Signals
Config parser tests should cover comments, blank lines, section whitespace compression, empty/bad sections, parameter whitespace trimming, values containing `=`, `[` and `;`, CR stripping, line continuations, bad lines, missing files, `&include` regular files and directories, sorted directory order, `&merge`, and include recursion failure behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/params.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/pipe.c -->
# Research: sources/sync-backup/rsync/pipe.c

## Purpose
`pipe.c` creates inter-process communication channels for remote-shell children and local rsync child processes. It hides pipe/socketpair setup, fork/exec, descriptor duplication, and local child role adjustments.

## Important APIs, Types, and Functions
- `piped_child(char **command, int *f_in, int *f_out)` forks and execs an external remote-shell command connected to rsync by stdin/stdout pipes.
- `local_child(int argc, char **argv, int *f_in, int *f_out, int (*child_main)(int, char*[]))` forks another in-process rsync role for local transfers and calls `child_main()` in the child.
- Extern state includes `am_sender`, `am_server`, `blocking_io`, `filesfrom_fd`, `munge_symlinks`, `logfile_name`, `remote_options`, and `chmod_modes`.

## Control Flow
Both functions create two fd pairs: parent-to-child and child-to-parent. After `do_fork()`, the child duplicates the read side of the input pair to stdin and the write side of the output pair to stdout, closes unused ends, and then either execs `command[0]` (`piped_child`) or adjusts rsync role state and calls `child_main()` (`local_child`). The parent closes child-only ends and returns the child pid plus read/write descriptors via `f_in` and `f_out`.

## State and Persistence
State changes are process-local after fork. `piped_child()` sets child stdin blocking and optionally stdout blocking based on `blocking_io`. `local_child()` changes the child to server/receiver role, resets `filesfrom_fd`, disables sender-side symlink munging, clears `chmod_modes`, closes client-side logfile state, and parses any `remote_options` before connecting stdio. No durable state is written.

## Dependencies and Integration Points
The file depends on rsync wrappers `fd_pair()`, `do_fork()`, `set_blocking()`, `rsyserr()`, `exit_cleanup()`, logging helpers, `parse_arguments()`, `option_error()`, and optional `setup_iconv()`. It integrates with remote-shell startup, local transfers, and option propagation from `options.c`.

## Risks
IPC setup failures abort the process. Descriptor leaks or wrong close order would deadlock rsync. `local_child()` must keep role-specific global resets aligned with option semantics; missing a reset could make the local receiver inherit sender-only behavior. `remote_options` parsing in the child can fail after fork and must report cleanly. External `execvp()` depends on `PATH`.

## Test Signals
Exercise remote-shell command execution, failed `pipe`/`fork`/`exec` paths, blocking and nonblocking modes, local transfer child role flags, remote option parsing failures, logfile closure, iconv setup, and descriptor liveness/deadlock under large transfers.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/pipe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/popt/dummy.in -->
# Research: sources/sync-backup/rsync/popt/dummy.in

## Purpose
`popt/dummy.in` is an empty placeholder file in the bundled popt directory. It carries no executable logic, declarations, or configuration content.

## Important APIs, Types, and Functions
None. The file length is zero bytes.

## Control Flow
None.

## State and Persistence
No state is represented or persisted.

## Dependencies and Integration Points
As a placeholder, it may exist to satisfy packaging, build-system, or distribution tooling that expects an input file in this path. No direct code dependency is visible from the file itself.

## Risks
The main risk is accidental removal if external tooling expects the path. Since the file is empty, content-level regressions are not applicable.

## Test Signals
Build/package tests should reveal whether the placeholder is required. A file-existence check is sufficient if tooling depends on it.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/popt/dummy.in -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/popt/lookup3.c -->
# Research: sources/sync-backup/rsync/popt/lookup3.c

## Purpose
`popt/lookup3.c` provides Bob Jenkins lookup3 32-bit hash functions for hash table lookup, with optional single-hash, pair-hash, word-array, byte-array, big-endian, and self-test builds. In this rsync tree it supports popt bitset/Bloom-filter-style helpers through `poptJlu32lpair()`.

## Important APIs, Types, and Functions
- Endian detection uses static union `endian` and macros `HASH_LITTLE_ENDIAN`/`HASH_BIG_ENDIAN`.
- Mixing macros `_JLU3_INIT`, `_JLU3_MIX(a,b,c)`, and `_JLU3_FINAL(a,b,c)` implement the Jenkins reversible block mix and final avalanche.
- Conditionally compiled functions: `jlu32w()`, `jlu32l()`, `jlu32lpair()`, and `jlu32b()`.
- `_JLU3_SELFTEST` enables test drivers `driver1()` through `driver4()` and a `main()`.

## Control Flow
Each hash initializes `a`, `b`, and `c` from `0xdeadbeef + size + seed`, then processes 12-byte/3-word blocks through `_JLU3_MIX()`. Tail handling is specialized by endian and alignment: aligned little-endian can read 32-bit chunks, half-aligned little-endian reads 16-bit chunks, and unaligned or other cases assemble bytes. `jlu32lpair()` also incorporates a secondary seed in `c` and returns two results through `pc` and `pb`. Big-endian `jlu32b()` mirrors the strategy for big-endian ordering.

## State and Persistence
The functions are pure except for output parameters in `jlu32lpair()`. No global mutable state is used. The self-test build prints diagnostics and returns from a local `main()`.

## Dependencies and Integration Points
It depends on `<stdint.h>` and compile-time feature macros selecting which symbols are emitted. `popt.c` uses the pair hash via popt's wrapper names for bitset operations. It is non-cryptographic and intended for lookup distribution, not security.

## Risks
Fast aligned tail paths intentionally read beyond the nominal byte length and mask unused bytes; this is documented as safe on common word-boundary memory systems but noisy under Valgrind unless `VALGRIND` is defined. Endian/alignment assumptions are delicate on strict-alignment platforms. The hash must not be used as an adversarial security primitive. A visible typo in the `VALGRIND` branch of `jlu32l()` (`a+=k[0] break`) would matter if that compile path is enabled.

## Test Signals
Build with default, `VALGRIND`, and `_JLU3_SELFTEST` configurations. Run the self-test drivers for avalanche, alignment, overread, and zero-length behavior. Cross-platform tests should compare expected hashes on little-endian, big-endian, aligned, and unaligned buffers.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/popt/lookup3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/popt/popt.c -->
# Research: sources/sync-backup/rsync/popt/popt.c

## Purpose
`popt/popt.c` is the core implementation of the bundled popt option parser used by rsync. It creates parser contexts, walks argv/options/aliases, saves typed option arguments, supports callbacks, leftovers, alias expansion, exec actions, argument stripping, and bitset helper operations.

## Important APIs, Types, and Functions
- Context lifecycle: `poptGetContext()`, `poptResetContext()`, and `poptFreeContext()`.
- Callback dispatch: `invokeCallbacksPRE()`, `invokeCallbacksPOST()`, and `invokeCallbacksOPTION()`.
- Option and alias machinery: `findOption()`, `longOptionStrcmp()`, `handleAlias()`, `handleExec()`, `poptAddAlias()`, `poptAddItem()`, `poptStuffArgs()`.
- Argument parsing and saving: `poptGetNextOpt()`, `poptGetOptArg()`, `poptGetArg()`, `poptPeekArg()`, `poptGetArgs()`, `poptSaveArg()`, `poptParseInteger()`, `poptSaveLongLong()`, `poptSaveLong()`, `poptSaveInt()`, `poptSaveShort()`, `poptSaveString()`, `poptSaveBits()`.
- Bitset helpers: `poptBitsAdd()`, `poptBitsChk()`, `poptBitsClr()`, `poptBitsDel()`, `poptBitsIntersect()`, `poptBitsUnion()`, `poptBitsArgs()`.
- Error/report helpers: `poptBadOption()`, `poptStrerror()`, `poptGetInvocationName()`, `poptStrippedArgv()`, `poptSetExecPath()`.

## Control Flow
`poptGetContext()` allocates and initializes a context, sets the initial option stack entry, applies POSIX environment flags, stores the application name, and invokes pre-parse callbacks. `poptGetNextOpt()` is the central loop: it pops exhausted alias/stuffed stack entries, handles end-of-input post callbacks/maincall/exec, classifies leftovers and `--`, parses long options including `--opt=arg`, tries aliases and exec triggers, falls back to short-option clusters, finds option descriptors, consumes required/optional arguments, expands `!#:+` substitutions, saves typed values, invokes callbacks, records final argv, and returns option values.

Alias expansion pushes a new option-stack entry with duplicated argv. Exec handling records a target command and later `execCommand()` builds argv from exec args, final option argv, and leftovers, drops elevated privileges where possible, and calls `execvp()`. Context reset/free paths release leftovers, aliases, execs, stacked argv, final argv, help strings, exec path, and bitmaps.

## State and Persistence
All parser state lives in `poptContext`: option stack, argv indexes, `nextCharArg`, `nextArg`, leftovers, aliases, exec definitions, final argv, strip bitmap, flags, callbacks, and exec failure. Module globals `_poptArgMask`, `_poptGroupMask`, and bitset sizing parameters tune parser masks and bitset behavior. No durable state is written; `execCommand()` replaces the process image on success.

## Dependencies and Integration Points
It depends on popt internal headers/macros, allocation helpers, bitmap macros, string helpers, `poptJlu32lpair()` from lookup3 for bitsets, libc parsing (`strtoll`, `strtod`), process APIs (`execvp`, uid/gid drops), and environment variables `POSIXLY_CORRECT`/`POSIX_ME_HARDER`. Rsync integrates through `options.c` by creating contexts, reading defaults, adding unaliases, fetching options, and reporting errors.

## Risks
This is security-sensitive parser code. Alias stack depth, argument ownership, optional-argument rules, final argv growth, and exec privilege dropping are key correctness points. Some comments mark memory leaks as application-owned for saved strings/argv/bitsets. String-command exec path handling and alias substitution must avoid unexpected argument injection. Numeric parsing currently lacks suffix support and treats extrema as overflow sentinels. Alignment checks in typed saves can reject unusual pointers. Bloom-style bitset deletion can create false negatives by clearing shared bits.

## Test Signals
Parser tests should cover long/short options, short clusters, `--opt=arg`, split args, optional args, unwanted args, `--`, POSIX leftover mode, aliases with depth limits and argument substitution, callbacks, typed saves and overflow, toggle/no- prefix behavior, strip argv, exec registration with privilege dropping, stuffed args, bad-option reporting, and bitset add/check/delete/intersection/union behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/popt/popt.c -->

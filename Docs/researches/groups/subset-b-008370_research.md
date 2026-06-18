<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/newrole/newrole.c -->
# sources/security-integrity/selinux/policycoreutils/newrole/newrole.c

## Purpose
`newrole` is a privileged SELinux RBAC/MLS transition tool analogous to `su`: it authenticates the current login user, validates a requested role/type/level transition, optionally relabels the controlling TTY, and execs the user's shell under the requested SELinux exec context.

## Important APIs, Types, And Functions
Key local helpers are `build_new_range()`, `authenticate_via_pam()` or `authenticate_via_shadow_passwd()`, `extract_pw_data()`, `restore_environment()`, `drop_capabilities()`, `send_audit_message()`, `relabel_tty()`, `restore_tty_label()`, `parse_command_line_arguments()`, and `set_signal_handles()`. It uses libselinux context APIs (`getprevcon`, `context_new`, `context_role_set`, `context_type_set`, `context_range_set`, `security_check_context`, `setexeccon`, `security_compute_relabel`, `fgetfilecon`, `fsetfilecon`), PAM or shadow/crypt authentication, optional libaudit, optional libcap-ng, and a small `hashtab` to map target commands to alternate PAM service names from `/etc/selinux/newrole_pam.conf`.

## Control Flow
`main()` drops unnecessary capabilities, clears the signal mask, initializes NLS, detaches the environment while parsing, requires SELinux, captures the previous context and tty, builds a valid target context from `-r`, `-t`, and `-l`, then authenticates the login uid or real uid. After authentication it relabels the tty, forks, and has the parent wait and restore the tty label. The child reopens stdin/stdout/stderr on the tty, calls `setexeccon(new_context)`, optionally opens a PAM namespace session, writes an audit success record, drops remaining privilege, restores either a scrubbed or preserved environment, and `execv()`s the user's configured shell.

## State And Persistence
Persistent state is limited but security-sensitive: it may relabel the tty device until the parent restores it, opens PAM sessions/namespaces, writes audit records, and runs a shell in the requested context. Environment state is deliberately scrubbed unless `-p` is used. Password buffers are zeroed in the shadow path.

## Dependencies And Integration Points
It integrates with `/etc/passwd`, `/etc/shells`, PAM, `/etc/shadow`, SELinux policy, audit, terminal devices, and package build flags controlling PAM/audit/namespace capability behavior.

## Risks And Edge Cases
The main risks are privilege retention, failure to restore tty labels, partial PAM session cleanup, unsafe preserved environments, MLS level changes from insecure terminals, and command-service parsing in `newrole_pam.conf`. The code mitigates several of these with capability drops, securetty checks, parent cleanup, `O_NONBLOCK` open handling, and context validation.

## Test Signals
Useful tests cover duplicate/invalid role/type/level options, MLS disabled behavior, secure and insecure terminals, PAM and shadow builds, tty label restore on shell exit and exec failure, audit success/failure emission, preserved versus scrubbed environment, and capability-restricted non-root invocation.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/newrole/newrole.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/po/Makefile -->
# sources/security-integrity/selinux/policycoreutils/po/Makefile

## Purpose
Builds and installs gettext catalogs for the `policycoreutils` package.

## Important APIs, Types, And Functions
The file defines `NLSPACKAGE=policycoreutils`, `POTFILE`, gettext commands (`xgettext`, `msgmerge`, `msgfmt`), `PO_LINGUAS`, `USER_LINGUAS`, `USE_LINGUAS`, `POFILES`, `MOFILES`, and `POTFILES` read from the local `POTFILES` manifest. Targets include `all`, `refresh-po`, `clean`, `install`, `report`, `relabel`, and `test`.

## Control Flow
`all` regenerates the POT template and compiles selected `.po` files into `.mo` files. `$(POTFILE)` runs `xgettext` over the files listed in `POTFILES`, replacing the old template only when it differs. `refresh-po` merges each language with the new POT. `install` places compiled catalogs under `$(DESTDIR)$(PREFIX)/share/locale/<lang>/LC_MESSAGES/policycoreutils.mo`.

## State And Persistence
The build produces `.mo`, temporary `.pot`, and generated `.po`/`.pot` files. Installation persists translation catalogs into the filesystem image.

## Dependencies And Integration Points
Depends on gettext tooling and the package-wide `LINGUAS` selection. It is called from the parent policycoreutils make recursion.

## Risks And Edge Cases
An incomplete `POTFILES` manifest misses translatable strings. Invalid `LINGUAS` silently falls back to all languages. Install paths depend on `PREFIX` and `DESTDIR`.

## Test Signals
`make report` runs `msgfmt --statistics` for catalog health; successful `all` and `install` indicate gettext tools and locale paths are usable.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/po/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/run_init/Makefile -->
# sources/security-integrity/selinux/policycoreutils/run_init/Makefile

## Purpose
Builds and installs the `run_init` and `open_init_pty` utilities used to execute init scripts under the correct SELinux context and PTY label.

## Important APIs, Types, And Functions
Variables configure install roots (`SBINDIR`, `MANDIR`, `ETCDIR`, `LOCALEDIR`), feature detection (`PAMH`, `AUDITH`), compiler flags for NLS/PAM/audit, and libselinux linkage through `LIBSELINUX_LDLIBS`. `TARGETS` is derived from local `.c` files. `open_init_pty` links with `-ldl -lutil`.

## Control Flow
`all` builds every C file as a binary. The PAM build path adds `-DUSE_PAM` and links PAM libraries; otherwise it enables shadow/crypt support. The audit header enables `-DUSE_AUDIT`. `install` creates sbin/man directories, installs both binaries and man pages, localized man pages, and `run_init.pamd` when PAM is available. `relabel` restores labels on installed binaries.

## State And Persistence
The Makefile creates binary artifacts and may install a PAM service file under `/etc/pam.d/run_init`.

## Dependencies And Integration Points
It is part of policycoreutils recursion and depends on libselinux, optional PAM, optional libaudit, `libutil` for PTY support, and localized man page directories.

## Risks And Edge Cases
Feature detection depends on host header locations, which can make cross builds inconsistent. PAM installs require `$(DESTDIR)$(ETCDIR)/pam.d` to exist or be creatable.

## Test Signals
Successful builds with and without PAM/audit, a working `open_init_pty` link, and restorecon success on installed paths are the primary signals.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/run_init/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/run_init/open_init_pty.c -->
# sources/security-integrity/selinux/policycoreutils/run_init/open_init_pty.c

## Purpose
Wraps a command in a freshly allocated pseudo-terminal so the spawned init command receives a PTY with the desired SELinux labeling path instead of reusing the caller's PTY.

## Important APIs, Types, And Functions
Important helpers are `tty_semi_raw()`, `tty_atexit()`, the `struct ring_buffer` routines (`rb_init`, `rb_space`, `rb_chunk_size`, `rb_read`, `rb_write`), `setfd_nonblock()`, `setfd_block()`, `setfd_atexit()`, and `sigchld_handler()`. It uses `forkpty`, `termios`, `ioctl(TIOCGWINSZ)`, `select`, nonblocking `read`/`write`, `waitpid`, and `execvp`.

## Control Flow
`main()` validates a program argument, installs a SIGCHLD handler so blocking I/O can be interrupted, captures terminal attributes/window size for interactive sessions, then calls `forkpty()`. The child disables echo/newline output translation and execs the requested program. The parent switches the pty, stdin, and stdout to nonblocking mode, optionally puts the terminal into semi-raw mode, then repeatedly uses `select()` to shuttle data between stdin/stdout and the pty through two ring buffers until the child exits and buffered data drains or retry limits are reached.

## State And Persistence
It temporarily changes terminal modes and file descriptor blocking flags, restoring them through `atexit` handlers. No persistent filesystem state is written.

## Dependencies And Integration Points
It is called by `run_init` after `setexeccon()` so the PTY allocation happens in the init execution context. It depends on libc, libutil/pty support, and terminal-capable stdio.

## Risks And Edge Cases
I/O retry handling treats repeated nonpositive reads/writes as terminal failure. Noninteractive use omits inherited termios/window sizing. Exit status is propagated only when `waitpid` records normal or signal termination.

## Test Signals
Tests should verify interactive echo behavior, stdin/stdout relay, child exit status propagation, noninteractive execution, SIGCHLD interruption, terminal restoration after early failures, and large bidirectional streams exceeding the 2 KiB buffers.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/run_init/open_init_pty.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/run_init/run_init.c -->
# sources/security-integrity/selinux/policycoreutils/run_init/run_init.c

## Purpose
Authenticates the caller and runs an init script or command under the SELinux context stored in the configured `initrc_context` file.

## Important APIs, Types, And Functions
Key functions are `authenticate_via_pam()` or `authenticate_via_shadow_passwd()`, `authenticate_user()`, `get_init_context()`, and `main()`. It uses libselinux (`is_selinux_enabled`, `selinux_contexts_path`, `setexeccon`), PAM or shadow/crypt, optional audit login uid lookup, passwd lookup, and `execvp`.

## Control Flow
`main()` initializes localization, requires SELinux, validates that a command is present, authenticates the login uid or real uid, reads the first nonblank context line from `$(selinux_contexts_path())/initrc_context`, changes directory to `/`, sets the exec context, and then either execs the requested command directly or execs `/usr/sbin/open_init_pty` with the original argument vector if that helper is executable.

## State And Persistence
It does not persist configuration itself, but consumes SELinux context configuration and can cause the child process to run with a new exec context. PAM may update authentication/accounting state; the child process may mutate system state as an init command.

## Dependencies And Integration Points
This utility bridges user authentication, SELinux policy contexts, and init/service scripts. It integrates with the optional `open_init_pty` helper to ensure PTY labels align with the initrc domain.

## Risks And Edge Cases
If `initrc_context` is missing or empty, execution fails. The shadow authentication path zeroes only the plaintext password and exits on several auth errors. Direct exec without `open_init_pty` may occur if the helper is not installed or executable.

## Test Signals
Exercise PAM and shadow builds, missing command, missing/empty context file, failed authentication, `setexeccon` failure, helper-present versus helper-absent execution, and child exit behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/run_init/run_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/scripts/Makefile -->
# sources/security-integrity/selinux/policycoreutils/scripts/Makefile

## Purpose
Installs the shell-script utilities in the policycoreutils scripts directory, currently centered on `fixfiles`.

## Important APIs, Types, And Functions
Defines `PREFIX`, `SBINDIR`, `MANDIR`, `LINGUAS`, and targets `all`, `install`, `clean`, and `relabel`. `all` depends on the executable script `fixfiles`.

## Control Flow
`install` creates the sbin and man8 destinations, installs `fixfiles` as mode 755, installs `fixfiles.8`, and copies localized man pages from language subdirectories when `LINGUAS` entries exist.

## State And Persistence
Only installed script and man page files are persisted. `clean` and `relabel` are no-op placeholders.

## Dependencies And Integration Points
This Makefile is invoked by the policycoreutils parent build. The installed script expects system tools such as `restorecon`, `setfiles`, `find`, `rpm`, `mount`, `unshare`, and SELinux utilities.

## Risks And Edge Cases
The target does not validate script syntax or dependency availability. `LINGUAS` handling assumes each language directory contains matching man8 pages.

## Test Signals
Useful signals are successful install into a staging `DESTDIR`, correct executable mode on `fixfiles`, correct man page placement, and shell syntax checks run separately against the script.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/scripts/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/scripts/fixfiles -->
# sources/security-integrity/selinux/policycoreutils/scripts/fixfiles

## Purpose
Provides high-level SELinux filesystem relabel workflows: check, verify, restore, relabel now, or request relabel on next boot.

## Important APIs, Types, And Functions
Major shell functions are `useseclabel`, `get_all_labeled_mounts`, `get_rw_labeled_mounts`, `get_ro_labeled_mounts`, `get_undefined_type`, `get_unlabeled_type`, `exclude_dirs_from_relabelling`, `LogReadOnly`, `LogExcluded`, `newer`, `diff_filecontext`, `rpmlist`, `fix_labels_on_mountpoint`, `restore`, `fullrelabel`, `relabel`, `process`, `usage`, and `set_restore_mode`. It drives `/sbin/setfiles`, `/sbin/restorecon`, `secon`, `find`, `rpm`, `genhomedircon`, `mount --bind`, `unshare -m`, `chcon`, and `selinuxenabled`.

## Control Flow
Startup computes labeled rw/ro mounts and the active `file_contexts` path from `/etc/selinux/config`. Options select force, verbose/progress, boot-time cutoff, previous file-context diff mode, RPM file list mode, bind-mount mode, full `/tmp` cleanup, and thread count. `process()` dispatches commands. `restore()` handles boot-time incremental relabel, file-context diff relabel, RPM-owned paths, explicit paths, or all writable labeled mounts. `relabel()` optionally asks about `/tmp` cleanup; `onboot` writes `/.autorelabel`.

## State And Persistence
The script can relabel large filesystem trees, delete `/tmp` contents, delete selected unlabeled temporary sockets/FIFOs, create temporary bind mount trees under `/run`, write `/.autorelabel`, and redirect logs with the obsolete `-l` option.

## Dependencies And Integration Points
It is the operational front end for `setfiles`/`restorecon`, RPM databases, SELinuxfs initial contexts, `/proc/self/mounts`, `/proc/self/mountinfo`, `/etc/selinux/fixfiles_exclude_dirs`, and boot relabel handling.

## Risks And Edge Cases
The blast radius is high: wrong mount detection, broken excludes, regex simplification in `diff_filecontext`, or `-F` can relabel many files. Bind-mount cleanup must not leave mounts behind. `set -o nounset` makes unset-variable paths fail fast.

## Test Signals
Run shell syntax checks, staged `DESTDIR`/container relabel dry runs, exclude-file parsing tests, RPM mode with missing packages, bind-mount cleanup on failure, `-N`/`-B` incremental modes, and `onboot` content validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/scripts/fixfiles -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/secon/Makefile -->
# sources/security-integrity/selinux/policycoreutils/secon/Makefile

## Purpose
Builds and installs `secon`, a command-line SELinux context inspection utility.

## Important APIs, Types, And Functions
Defines strict warning flags in `WARNS`, reads `VERSION` from `../VERSION`, adds libselinux include/library paths, and uses `LIBSELINUX_LDLIBS`. Targets are `all`, `secon`, `install-nogui`, `install`, `relabel`, `clean`, and `bare`.

## Control Flow
`all` builds `secon` from `secon.o`. `install` copies the binary to `$(BINDIR)`, installs `secon.1`, and installs localized man1 files. `relabel` calls `/sbin/restorecon` on the installed binary. `bare` aliases cleanup.

## State And Persistence
The build creates `secon` and object files; install persists the binary and man pages.

## Dependencies And Integration Points
Depends on libselinux and the parent policycoreutils build exports. `secon` is also used by scripts such as `fixfiles` to extract context types.

## Risks And Edge Cases
The aggressive warning profile can expose portability issues across compilers. Install does not create `$(BINDIR)` before copying, so packaging must ensure it exists.

## Test Signals
Compile with the configured warning set, install into a staging root, run `secon --version`, and relabel the installed binary when SELinux is active.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/secon/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/secon/secon.c -->
# sources/security-integrity/selinux/policycoreutils/secon/secon.c

## Purpose
Displays selected fields from SELinux security contexts obtained from arguments, stdin, current process state, parent/pid process state, files, or symlinks.

## Important APIs, Types, And Functions
The option state lives in a single bitfield struct `opts`. Important functions are `cmd_line()`, `get_scon()`, `my_getXcon_raw()`, `disp__color_to_ansi()`, `disp__con_color_ansi()`, `disp__con_val()`, and `disp_con()`. It uses libselinux APIs such as `getcon_raw`, `getexeccon_raw`, `getfscreatecon_raw`, `getkeycreatecon_raw`, `getpidcon_raw`, `getfilecon_raw`, `lgetfilecon_raw`, context translation, `context_new`, and `selinux_raw_context_to_color`.

## Control Flow
`cmd_line()` toggles requested fields (`user`, `role`, `type`, sensitivity, clearance, range), output modes (`raw`, prompt, color), and input source. If no source is provided it defaults to current process or stdin when piped. `get_scon()` reads or queries a raw context. `disp_con()` translates to display context unless raw mode is requested, optionally loads color information, parses fields with `context_new`, and prints either labeled multiline output or prompt-style colon-separated output.

## State And Persistence
The tool is read-only. It reads `/proc/<pid>/attr/{exec,fscreate,keycreate}` directly for process attributes not wrapped by libselinux APIs.

## Dependencies And Integration Points
It integrates with libselinux context parsing/translation and `/proc` process attributes, and is used by scripts for field extraction.

## Risks And Edge Cases
`atoi()` pid parsing accepts malformed input as zero. Color parsing assumes a fixed token sequence. Empty exec/fs/key contexts are represented as empty strings. Context translation failures abort.

## Test Signals
Cover field combinations, raw versus translated output, stdin input, file versus symlink labels, current and parent process modes, prompt/color output, missing SELinux, and invalid context strings.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/secon/secon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/semodule/Makefile -->
# sources/security-integrity/selinux/policycoreutils/semodule/Makefile

## Purpose
Builds and installs `semodule`, plus a `genhomedircon` symlink that reuses `semodule` behavior.

## Important APIs, Types, And Functions
Variables configure sbin/man destinations, libselinux/libsemanage include and library paths, `LIBSEMANAGE_LDLIBS`, `LIBSELINUX_LDLIBS`, and `SEMODULE_OBJS`. Targets are `semodule`, `genhomedircon`, `install`, `relabel`, and `clean`.

## Control Flow
`all` builds `semodule` and creates a local symlink named `genhomedircon`. `install` copies `semodule`, creates the installed symlink, installs both man8 pages, and installs localized man pages. `clean` removes the binary, objects, and symlink.

## State And Persistence
Build state is `semodule.o`, `semodule`, and symlinks. Install persists the management utility and compatibility entry point.

## Dependencies And Integration Points
Depends on libsemanage, libsepol, libselinux, and CIL logging through the linked libraries. The `genhomedircon` invocation is handled by `semodule.c` based on `argv[0]`.

## Risks And Edge Cases
The symlink target assumes both commands can share one binary. If packaging strips or renames one entry point, `argv[0]` behavior changes.

## Test Signals
Build/link success against libsemanage/libsepol, installed symlink correctness, `semodule -l`, and `genhomedircon` mode invocation are good signals.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/semodule/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/semodule/semodule.c -->
# sources/security-integrity/selinux/policycoreutils/semodule/semodule.c

## Purpose
Implements the SELinux module-store command-line client for installing, removing, listing, extracting, enabling/disabling, rebuilding, refreshing, and reloading policy modules.

## Important APIs, Types, And Functions
Core types are `enum client_modes` and `struct command`. Important helpers are `cleanup()`, `set_store()`, `set_store_root()`, `create_signal_handlers()`, `parse_command_line()`, `set_mode()`, and `hash_module_data()`. It uses libsemanage handles, transactions, module keys/info, module install/remove/extract/list/set-enabled APIs, checksum computation, store selection/root APIs, reload/rebuild flags, and CIL log level control.

## Control Flow
`main()` handles `genhomedircon` argv0 compatibility by replacing argv with `-B -n`, parses global options and ordered commands, creates or uses a semanage handle, selects store/store root, enables store creation, connects, optionally reloads, begins a transaction for build/refresh, sets default priority, executes each queued command, accumulates whether a commit is needed, applies reload/rebuild/dontaudit/tunables/cache flags, commits, disconnects, and cleans up.

## State And Persistence
Install/remove/enable/disable/build operations mutate the semanage policy store and may reload the active policy unless `-n/-N` suppresses reload. Extract writes a module file in the current directory using exclusive create. List operations are read-only.

## Dependencies And Integration Points
It is the user-facing bridge to libsemanage's direct policy store, CIL compiler behavior, module cache, store priority model, and `genhomedircon` rebuild logic.

## Risks And Edge Cases
Mode ordering matters because priority and CIL/HLL extraction mode are commands in the same queue. Signal handlers drop termination signals, relying on cleanup after API calls. Extract refuses to overwrite files, which avoids clobber but can surprise scripts. Store path/root mistakes affect persistent policy.

## Test Signals
Test ordered multi-command sequences, priority validation, install/remove/enable/disable commits, no-reload, full and standard listing with checksums, extract CIL/HLL output and no overwrite, refresh/rebuild flags, alternate store/config paths, and `genhomedircon` argv0 behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/semodule/semodule.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/sestatus/Makefile -->
# sources/security-integrity/selinux/policycoreutils/sestatus/Makefile

## Purpose
Builds and installs `sestatus`, its configuration file, man pages, and a compatibility symlink in sbin.

## Important APIs, Types, And Functions
Defines `BINDIR`, `SBINDIR`, `MANDIR`, `ETCDIR`, libselinux include/library flags, and `_FILE_OFFSET_BITS=64`. Targets include `sestatus`, `install`, `clean`, and `relabel`.

## Control Flow
`all` builds `sestatus`. `install` creates man and binary directories, creates a relative sbin symlink to the bindir binary for tools that hard-code `/usr/sbin/sestatus`, installs the binary, installs man8/man5 files, localized man pages, and installs `sestatus.conf` under `$(ETCDIR)`.

## State And Persistence
Persists the executable, symlink, man pages, and `/etc/sestatus.conf`.

## Dependencies And Integration Points
Depends on libselinux and system packaging conventions where `BINDIR` and `SBINDIR` may differ or be identical.

## Risks And Edge Cases
The relative symlink creation must behave correctly under `DESTDIR`; unusual install tools or non-GNU `ln` may differ. Existing symlinks are deliberately overwritten before binary install.

## Test Signals
Staged install should show a working binary in bindir, correct sbin symlink, installed config, and successful execution against active or disabled SELinux.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/sestatus/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/sestatus/sestatus.c -->
# sources/security-integrity/selinux/policycoreutils/sestatus/sestatus.c

## Purpose
Reports SELinux system status, optional boolean state, and optional verbose process/file context checks.

## Important APIs, Types, And Functions
Important helpers are `cmp_cmdline()`, `pidof()`, `load_checks()`, and `printf_tab()`. It uses libselinux status/config APIs (`is_selinux_enabled`, `selinux_mnt`, `selinux_path`, `selinux_policy_root`, `security_getenforce`, `selinux_getenforcemode`, `is_selinux_mls_enabled`, `security_deny_unknown`, `security_get_checkreqprot`, `security_policyvers`, boolean APIs, `getcon`, `getpidcon`, `lgetfilecon`, `getfilecon`) plus `/proc` directory scanning.

## Control Flow
`main()` parses `-v` and `-b`, prints core SELinux mount/root/policy/mode/MLS/deny_unknown/checkreqprot/policy version state, optionally lists active and pending booleans, and exits unless verbose mode is enabled. In verbose mode it loads process and file checks from `/etc/sestatus.conf`, prints current and init process contexts, looks up configured process executables by scanning `/proc`, then prints controlling terminal and configured file/symlink contexts.

## State And Persistence
The tool is read-only. It dynamically allocates check lists from the config file and frees them while reporting.

## Dependencies And Integration Points
It integrates with `/etc/sestatus.conf`, SELinuxfs, `/proc/<pid>/exe`, and libselinux runtime/config status.

## Risks And Edge Cases
`cmp_cmdline()` uses fixed-size buffers and `readlink` without the return length, though it forces termination. `ttyname(0)` can be NULL, causing context lookup failures. The config loader caps each section at 50 entries and ignores overflow.

## Test Signals
Exercise disabled SELinux, missing selinuxfs, `-b` boolean output, `-v` with missing and populated config, symlink file checks, long command paths, and no controlling terminal.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/sestatus/sestatus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/sestatus/sestatus.conf -->
# sources/security-integrity/selinux/policycoreutils/sestatus/sestatus.conf

## Purpose
Provides the default verbose-check input for `sestatus -v`.

## Important APIs, Types, And Functions
The file has two recognized sections: `[files]` and `[process]`. The C loader treats noncomment, nonblank lines under `[files]` as paths for `lgetfilecon`/`getfilecon` checks and lines under `[process]` as executable paths to locate in `/proc`.

## Control Flow
`sestatus` reads the file top to bottom, switches parser state on section headers, and records up to 50 entries for each section. The shipped file checks core login/shell/system binaries and common getty/sshd processes.

## State And Persistence
This is persistent host configuration under `/etc/sestatus.conf` when installed.

## Dependencies And Integration Points
Entries must match real filesystem paths and process executable symlink targets. Package layouts using `/usr` merge or alternate init/getty locations may need customization.

## Risks And Edge Cases
Stale paths cause missing context output. Process checks are exact executable-path matches, not service names. The file has no schema version, so parser compatibility depends on stable section names.

## Test Signals
Run `sestatus -v` with the installed file on systems with and without the listed paths/processes, and verify comments/blank lines are ignored.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/sestatus/sestatus.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/setfiles/Makefile -->
# sources/security-integrity/selinux/policycoreutils/setfiles/Makefile

## Purpose
Builds and installs `setfiles`, its `restorecon` symlink, and `restorecon_xattr`.

## Important APIs, Types, And Functions
Defines `/sbin` as default `SBINDIR`, audit header detection, libselinux/libsepol/pthread linkage, and optional libaudit flags. Targets are `setfiles`, `restorecon`, `restorecon_xattr`, `install`, `clean`, and `relabel`.

## Control Flow
`all` builds `setfiles restorecon restorecon_xattr`. `setfiles` links `setfiles.o restore.o`; `restorecon` is a symlink to `setfiles`; `restorecon_xattr` links `restorecon_xattr.o restore.o`. Install copies binaries, creates the symlink, installs man pages and localized man pages. `relabel` runs the installed `restorecon` on installed binaries.

## State And Persistence
Produces binaries, symlinks, and installed man pages; `relabel` can mutate labels on installed utility files.

## Dependencies And Integration Points
Depends on libselinux restorecon APIs, libsepol, pthreads for parallel restorecon, and optional audit.

## Risks And Edge Cases
The behavior of `setfiles` versus `restorecon` is selected by argv0, so symlink correctness is functional. Default `/sbin` install path may differ from distribution policy.

## Test Signals
Check that both argv0 modes exist, `restorecon` symlink points to `setfiles`, optional audit builds work, and staged relabel targets only installed utility files.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/setfiles/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/setfiles/restore.c -->
# sources/security-integrity/selinux/policycoreutils/setfiles/restore.c

## Purpose
Provides shared restorecon initialization, exclusion, glob expansion, and cleanup helpers used by `setfiles`, `restorecon`, `restorecon_xattr`, and noted restorecond integration.

## Important APIs, Types, And Functions
Exports `restore_init()`, `restore_finish()`, `process_glob()`, `add_exclude()`, and global `exclude_list`. It uses `selabel_open`, `selinux_restorecon_set_sehandle`, `selinux_restorecon_set_alt_rootpath`, `selinux_restorecon_set_exclude_list`, `selinux_restorecon_parallel`, and restorecon counters.

## Control Flow
`restore_init()` opens a file-context label handle with validation/path/digest options, assembles `restorecon_flags` from `struct restore_opts`, registers the handle globally with libselinux restorecon, applies an alternate root path, and installs excludes. `process_glob()` expands a user path with tilde/period/nocheck/brace flags, skips trailing `/.` and `/..`, then calls `selinux_restorecon_parallel()` for each result and accumulates skipped-error and relabeled-file counters. `add_exclude()` appends absolute directories to a NULL-terminated list.

## State And Persistence
The helpers own the selabel handle and process-global libselinux restorecon handle/exclusion state. `process_glob()` can relabel filesystem objects depending on flags passed by callers.

## Dependencies And Integration Points
It is the shared adapter between command-line options and libselinux restorecon internals.

## Risks And Edge Cases
`add_exclude()` exits on relative paths. Global `exclude_list` and restorecon handle make concurrent embedding risky unless callers isolate processes. Globbing with `GLOB_NOCHECK` means unmatched patterns are still processed.

## Test Signals
Test exclude list construction/freeing, alternate root errors, digest/validate option propagation, glob patterns including unmatched and brace forms, thread counts, and relabeled/skipped counter accumulation.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/setfiles/restore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/setfiles/restore.h -->
# sources/security-integrity/selinux/policycoreutils/setfiles/restore.h

## Purpose
Defines the shared restorecon option structure and function prototypes for the setfiles-family utilities.

## Important APIs, Types, And Functions
`struct restore_opts` stores individual SELINUX_RESTORECON flags, computed `restorecon_flags`, `rootpath`, `progname`, `selabel_handle *hnd`, selabel option pointers for validate/path/digest, and a debug flag. It declares `restore_init`, `restore_finish`, `add_exclude`, `process_glob`, and `extern char **exclude_list`.

## Control Flow
Callers initialize a `restore_opts`, set fields from command-line options, call `restore_init()`, call `process_glob()` or other libselinux operations, then call `restore_finish()`.

## State And Persistence
The header itself persists no state, but its structure controls relabel, digest, validation, traversal, audit, and error-count behavior in callers.

## Dependencies And Integration Points
Includes libsepol, libselinux label/restorecon, syslog, fts, stat, and standard system headers. This makes it the ABI-like contract among `setfiles.c`, `restore.c`, and `restorecon_xattr.c`.

## Risks And Edge Cases
Because flags are stored as unsigned ints and ORed later, callers must only assign compatible libselinux flag constants. New libselinux flags require coordinated additions here and in `restore_init()`.

## Test Signals
Compile all consumers after any struct change, and verify each command-line option maps to the expected struct field and final restorecon flag set.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/setfiles/restore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/setfiles/restorecon_xattr.c -->
# sources/security-integrity/selinux/policycoreutils/setfiles/restorecon_xattr.c

## Purpose
Inspects and optionally deletes `security.sehash` restorecon digest extended attributes for directories under a path.

## Important APIs, Types, And Functions
`main()` parses options and uses shared `add_exclude()`/`restore_finish()`. It uses `selabel_open` with `SELABEL_OPT_DIGEST`, `selabel_digest`, `selinux_restorecon_set_sehandle`, `selinux_restorecon_set_exclude_list`, `realpath`, and `selinux_restorecon_xattr`. It consumes `struct dir_xattr` results with statuses `MATCH`, `NOMATCH`, `DELETED_MATCH`, `DELETED_NOMATCH`, and `ERROR`.

## Control Flow
The program requires SELinux enabled, parses display/delete/recurse/ignore-mount/exclude/specfile options, opens a label handle with digest enabled, optionally prints the calculated specfile SHA1 digest and source specfiles, registers excludes, resolves the target path, calls `selinux_restorecon_xattr()`, prints each returned directory digest state, frees the returned linked list, closes the handle, and frees excludes.

## State And Persistence
With `-d` or `-D`, it removes restorecon digest xattrs. Otherwise it is read-only apart from allocation and label-handle state.

## Dependencies And Integration Points
Works with libselinux restorecon digest support and the same exclude mechanism as `setfiles`. It can target alternate file_contexts via `-f`.

## Risks And Edge Cases
Digest display requires the label backend to provide a digest. `realpath()` rejects nonexistent targets. Delete options can invalidate cached relabel optimization for many directories.

## Test Signals
Test digest display, no-comment mode, recursive and mount-ignore flags, exclude handling, nonmatching digest deletion, all-digest deletion, alternate specfile, SELinux-disabled failure, and memory cleanup under empty result lists.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/setfiles/restorecon_xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/setfiles/setfiles.c -->
# sources/security-integrity/selinux/policycoreutils/setfiles/setfiles.c

## Purpose
Implements both `setfiles` and `restorecon`, mapping their different command-line semantics onto libselinux restorecon operations.

## Important APIs, Types, And Functions
Important helpers are `usage()`, `set_rootpath()`, `canoncon()`, `audit_mass_relabel()`, and `log_callback()`. It configures global `r_opts`, `iamrestorecon`, `ctx_validate`, `policyfile`, `altpath`, `warn_no_match`, `null_terminated`, and `request_digest`. It uses libsepol policy validation, selinux callbacks, selabel stats/close, restore helpers, and optional libaudit `AUDIT_FS_RELABEL`.

## Control Flow
`main()` determines mode from `basename(argv[0])`. `setfiles` defaults to recursive, no realpath, association tracking, xdev, and eager context validation; `restorecon` defaults to nonrecursive, realpath, no association tracking, follows mounts, and exits silently if SELinux is disabled. Option parsing sets restorecon flags, exclusions, input-file mode, alternate root/specfile, policy validation source, digest behavior, and threads. It validates arguments, configures selabel options/callbacks, calls `restore_init()`, processes either `-f` input records or argv paths via `process_glob()`, optionally audits mass relabel, emits stats/counts, closes/free resources, and exits based on errors/skipped errors/relabeled count.

## State And Persistence
The command can relabel files, update directory digest xattrs, log to syslog, and emit audit records. In no-change mode it reports without mutating labels.

## Dependencies And Integration Points
It is the core backend for `restorecon`, `setfiles`, `fixfiles`, and build relabel targets.

## Risks And Edge Cases
Mode selection by argv0 is critical. `-f` input supports newline or NUL delimiting and can drive broad relabels. Alternate root rejects `/`. Policyfile validation exits on invalid contexts. Count-relabeled mode intentionally returns 1 when nothing changed.

## Test Signals
Cover argv0 mode differences, every option-to-flag mapping, input file delimiting, mass relabel audit, invalid contexts, alternate roots, excludes, digest behavior, thread counts, count-relabeled exit semantics, and SELinux-disabled restorecon behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/setfiles/setfiles.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/setsebool/Makefile -->
# sources/security-integrity/selinux/policycoreutils/setsebool/Makefile

## Purpose
Builds and installs the `setsebool` utility and bash completion.

## Important APIs, Types, And Functions
Defines libselinux/libsemanage include and library paths, `SETSEBOOL_OBJS`, `BASHCOMPLETIONDIR`, and `BASHCOMPLETIONS`. Targets include `all`, `setsebool`, `install`, `relabel`, and `clean`.

## Control Flow
`all` builds `setsebool`. `install` copies the binary to sbin, installs `setsebool.8` and localized man pages, creates the bash-completion directory, and installs `setsebool-bash-completion.sh` as the `setsebool` completion.

## State And Persistence
Build outputs are object and binary files; install persists the executable, man pages, and completion script.

## Dependencies And Integration Points
Depends on libselinux for active booleans and libsemanage for persistent boolean changes.

## Risks And Edge Cases
Completion install only names `setsebool`, while the script also registers `getsebool`; packaging must decide whether that is intended. Relabel is a no-op.

## Test Signals
Compile/link success, staged install of the binary and completion file, and runtime tests for temporary and permanent boolean changes.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/setsebool/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/setsebool/setsebool-bash-completion.sh -->
# sources/security-integrity/selinux/policycoreutils/setsebool/setsebool-bash-completion.sh

## Purpose
Provides bash completions for `setsebool` and `getsebool`.

## Important APIs, Types, And Functions
Functions are `__get_all_booleans()`, `_setsebool()`, and `_getsebool()`. It calls `getsebool -a` to enumerate names and uses bash `COMP_WORDS`, `COMP_CWORD`, `COMPREPLY`, `compgen`, and `compopt -o nospace`.

## Control Flow
`_setsebool()` offers values after `=`, booleans or `on/off` for recognized boolean names, numeric `0/1`, and options `-N -P -V`. `_getsebool()` offers `-a` and boolean names. The script registers both completion functions at the bottom.

## State And Persistence
No persistent state is written; completions reflect current `getsebool -a` output each invocation.

## Dependencies And Integration Points
Requires bash programmable completion and the `getsebool` binary. It integrates with installed shell completion directories through the Makefile.

## Risks And Edge Cases
`_getsebool()` declares but never assigns `verb`, so its first branches rely on it remaining empty. Frequent `getsebool` calls may be slow on large policies. Completion behavior depends on current word parsing around `=`.

## Test Signals
Source the file in bash and complete options, boolean names, `bool=on/off`, separate `bool 1`, and `getsebool -a` forms.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/setsebool/setsebool-bash-completion.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/setsebool/setsebool.c -->
# sources/security-integrity/selinux/policycoreutils/setsebool/setsebool.c

## Purpose
Changes SELinux policy booleans either temporarily in the active policy or persistently through the semanage store.

## Important APIs, Types, And Functions
Important functions are `usage()`, `main()`, `selinux_set_boolean_list()`, `semanage_set_boolean_list()`, and `setbool()`. It uses `SELboolean`, `security_set_boolean_list`, semanage handle/transaction APIs, local boolean records and keys, active boolean update APIs, syslog, and passwd lookup.

## Control Flow
`main()` parses `-P` permanent, `-N` no reload, and `-V` verbose. It supports legacy `boolean value` syntax by synthesizing `boolean=value`, or multi-assignment syntax. `setbool()` parses each assignment, validates true/false/on/off/1/0 values, builds a `SELboolean` array, calls either active libselinux update or persistent semanage update, then logs each change to syslog.

## State And Persistence
Temporary mode mutates active kernel boolean state. Permanent mode opens the managed policy store, modifies local booleans, optionally sets active values if SELinux is enabled, and commits with optional reload suppression. Syslog records the caller.

## Dependencies And Integration Points
It bridges `setsebool` CLI syntax, active policy booleans, semanage persistent policy, and audit/operations logging through syslog.

## Risks And Edge Cases
`setbool()` temporarily overwrites `=` in argv strings and restores it during parsing, but not in the later syslog loop. Permanent mode requires managed policy and sufficient privilege. `-N` only affects semanage commits.

## Test Signals
Test both syntaxes, batches with mixed valid/invalid values, temporary failure for nonexistent booleans, permanent commits, no-reload, verbose semanage messages, non-root errors, and syslog names for uid without passwd entry.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/setsebool/setsebool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/unsetfiles/Makefile -->
# sources/security-integrity/selinux/policycoreutils/unsetfiles/Makefile

## Purpose
Builds and installs `unsetfiles`, a utility for removing SELinux xattrs on SELinux-disabled systems.

## Important APIs, Types, And Functions
Defines `PREFIX`, `SBINDIR`, `MANDIR`, libselinux include/library flags, and `-D_GNU_SOURCE`. Targets are `all`, `unsetfiles`, `install`, `clean`, and `relabel`.

## Control Flow
`all` builds `unsetfiles` from `unsetfiles.o`. `install` creates sbin and man1 directories, installs the binary and `unsetfiles.1`. `relabel` runs restorecon on the installed binary.

## State And Persistence
Build state is object/binary files; install persists the utility and man page.

## Dependencies And Integration Points
Depends on libselinux and system xattr support used by the C source.

## Risks And Edge Cases
The `relabel` target invokes `/sbin/restorecon`, which may be inappropriate when building for systems where SELinux is disabled, although it targets only the installed utility.

## Test Signals
Compile/link success, staged install, and runtime dry-run tests against xattr-capable filesystems.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/unsetfiles/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/unsetfiles/unsetfiles.c -->
# sources/security-integrity/selinux/policycoreutils/unsetfiles/unsetfiles.c

## Purpose
Removes `security.selinux` extended attributes from files or directory trees, but only when SELinux is not enabled.

## Important APIs, Types, And Functions
Key functions are `usage()`, recursive `unset()`, and `main()`. It uses `lgetxattr`, `lremovexattr`, `openat`, `fdopendir`, `readdir`, `dirfd`, `fstat`, `stat`, `asprintf`, and `is_selinux_enabled()`.

## Control Flow
`main()` parses dry-run, recursive, verbose, and same-filesystem options, rejects execution on SELinux-enabled systems, optionally records the root device for `-x`, and calls `unset()` for each path. `unset()` checks for an SELinux xattr and either reports or removes it. In recursive mode it opens directories without following symlinks, enforces the device boundary when requested, iterates children, builds full paths for reporting/xattr calls, and recurses.

## State And Persistence
Without `-n`, it persistently removes SELinux labels from filesystem objects. It does not follow symlinked directories for traversal.

## Dependencies And Integration Points
Useful for converting or cleaning filesystems outside active SELinux. It depends on Linux xattrs and libselinux status.

## Risks And Edge Cases
It intentionally refuses to run when SELinux is enabled. Errors are reported but do not accumulate into a nonzero exit code for individual failed paths. Full paths are used for xattr operations while `openat` protects traversal.

## Test Signals
Test SELinux-enabled refusal, dry-run output, recursive traversal, symlink handling, device-boundary skipping, verbose ENODATA/ENOTSUP reporting, and failure exit behavior expectations.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/unsetfiles/unsetfiles.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/Makefile -->
# sources/security-integrity/selinux/python/Makefile

## Purpose
Top-level recursive Makefile for SELinux Python tooling.

## Important APIs, Types, And Functions
Defines `SUBDIRS = sepolicy audit2allow semanage sepolgen chcat po` and forwards `all install relabel clean format test` to each subdirectory.

## Control Flow
For any supported target, it loops through `SUBDIRS`, changes into each directory, invokes `$(MAKE) $@`, and stops on the first failure.

## State And Persistence
State is produced by subdirectory builds and installs; this file itself creates no artifacts.

## Dependencies And Integration Points
It integrates the Python components into the broader SELinux build. Subdirectories contain scripts, libraries, translations, tests, and man pages.

## Risks And Edge Cases
Ordering matters: tools such as `audit2allow` depend on sepolgen modules being installed or importable at runtime, though make recursion does not express fine-grained dependencies. A missing target in any subdir fails the whole target.

## Test Signals
Run each forwarded target in a staged environment and confirm failures propagate. `make test` is the broadest signal because it invokes all subproject tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/audit2allow/Makefile -->
# sources/security-integrity/selinux/python/audit2allow/Makefile

## Purpose
Builds, tests, and installs `audit2allow`, the `audit2why` symlink, `sepolgen-ifgen`, and the C attribute helper.

## Important APIs, Types, And Functions
Defines `PYTHON`, `SECILC`, install directories, CFLAGS/LDFLAGS for libselinux, optional `LIBSEPOLA`, `LDLIBS_LIBSEPOLA`, and targets `audit2why`, `sepolgen-ifgen-attr-helper`, `test_dummy_policy`, `test`, `install`, `clean`, and `relabel`.

## Control Flow
`all` creates the `audit2why` symlink and builds the helper. The helper links against static or fallback libsepol and libselinux. `test` builds a dummy binary policy from CIL using `secilc`, then runs `test_audit2allow.py`. `install` copies scripts and helper to bindir, recreates the `audit2why` symlink, and installs man pages and localized man pages.

## State And Persistence
Build outputs include the helper binary, object files, `audit2why` symlink, and `test_dummy_policy`. Install persists command-line tools and man pages.

## Dependencies And Integration Points
Depends on Python sepolgen modules, libselinux, libsepol, `secilc`, and test fixtures in the directory.

## Risks And Edge Cases
Static libsepol selection can vary by build environment. `audit2why` behavior is name-sensitive because the Python source checks basename. Tests require local execution from the source directory.

## Test Signals
`make test`, helper link success, symlink correctness, script install permissions, and successful `audit2allow`/`audit2why` execution against `test_dummy_policy`.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/audit2allow/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/audit2allow/audit2allow -->
# sources/security-integrity/selinux/python/audit2allow/audit2allow

## Purpose
Converts SELinux audit denials into allow/dontaudit policy, reference-policy interface calls, CIL, loadable module packages, or human-readable `audit2why` explanations.

## Important APIs, Types, And Functions
The central class is `AuditToPolicy` with methods `__parse_options()`, `__read_input()`, `__process_input()`, `__load_interface_info()`, `__output_modulepackage()`, `__output_audit2why()`, `__output()`, and `main()`. It uses `sepolgen.audit`, `policygen`, `interfaces`, `output`, `objectmodel`, `defaults`, `module`, `selinux.audit2why`, and optional `sepolicy` boolean descriptions.

## Control Flow
Options choose audit source (`stdin`, file, dmesg, audit log, boot audit), policy path, module/package output, CIL, reference-policy generation, xperms, explanation verbosity, type filters, and audit2why mode. Input is parsed to AVC accesses and role transitions. Normal output configures a `PolicyGenerator`, optionally loads interface and permission maps, adds access/role data, and writes to stdout, append file, or `.te` plus compiled `.pp`. Audit2why mode initializes the audit2why engine and prints cause-specific explanations for allow/dontaudit/boolean/TE/constraint/RBAC/bounds outcomes.

## State And Persistence
It may read audit logs/dmesg, append output files, create `.te` and `.pp` module-package artifacts, and initialize/finish the audit2why analysis engine.

## Dependencies And Integration Points
It integrates audit records, active or supplied binary policy, sepolgen reference data, module compiler tooling, and `semodule -i` deployment guidance.

## Risks And Edge Cases
Conflict checks print errors but do not always exit immediately. Generated policy may be overly broad if audit input is noisy. Module package mode refuses output/module/CIL combinations. Missing interface or perm-map files abort reference-policy output.

## Test Signals
Use supplied dummy policy/log tests, xperm generation, module name validation, each input source, CIL and reference/no-reference modes, module package output, and audit2why boolean/constraint cases.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/audit2allow/audit2allow -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/audit2allow/audit2why -->
# sources/security-integrity/selinux/python/audit2allow/audit2why

## Purpose
Acts as the `audit2why` command entry point using the same Python source as `audit2allow`, switching default behavior based on `os.path.basename(sys.argv[0])`.

## Important APIs, Types, And Functions
The same `AuditToPolicy` class and methods are used as in `audit2allow`. The important distinction is option parsing: `--why` defaults to true when the basename is `audit2why`, so `__output()` routes to `__output_audit2why()`.

## Control Flow
The program parses audit input and policy options, initializes `selinux.audit2why`, parses messages into the audit parser, then walks AVC messages and prints diagnostic causes and suggested remediation for booleans, missing TE rules, constraints, missing role allows, and typebounds.

## State And Persistence
It is normally read-only, consuming logs or stdin and printing explanations. It initializes policy-analysis state through the audit2why binding and calls `audit2why.finish()`.

## Dependencies And Integration Points
Depends on the same sepolgen and libselinux Python bindings as `audit2allow`, with optional `sepolicy` descriptions for booleans.

## Risks And Edge Cases
Because it shares the file with `audit2allow`, installed symlink/name correctness is functional. Policy mismatches between logged denials and current/supplied policy can produce misleading "would be allowed" or dontaudit explanations.

## Test Signals
Verify the installed symlink invokes why mode by default, `-p test_dummy_policy -i test.log` succeeds, and known boolean/TE/constraint denial samples produce expected explanation categories.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/audit2allow/audit2why -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/audit2allow/sepolgen-ifgen -->
# sources/security-integrity/selinux/python/audit2allow/sepolgen-ifgen

## Purpose
Parses reference-policy interface headers and optional policy attribute access into an interface-info file used by sepolgen/audit2allow.

## Important APIs, Types, And Functions
Functions are `parse_options()`, `get_attrs()`, and `main()`. It uses `sepolgen.refparser.parse_headers`, `sepolgen.defaults`, `sepolgen.interfaces.InterfaceSet`/`AttributeSet`, `tempfile.NamedTemporaryFile`, and an external `sepolgen-ifgen-attr-helper`.

## Control Flow
`main()` parses output path, header directory, policy path, verbosity/debug, helper path, and `--no_attrs`. It opens the output early, optionally calls the helper to write attribute info to a temporary file and parses it into an `AttributeSet`, parses header files, adds parsed headers plus attributes into an `InterfaceSet`, writes the interface-info file, and returns success only if the reference parser reports success.

## State And Persistence
It writes the selected interface-info output file and uses a temporary file for helper output. It reads policy and header inputs.

## Dependencies And Integration Points
This script connects Python sepolgen parsing with the C helper that reads binary policy access vectors for attributes.

## Risks And Edge Cases
Opening the output before parsing can truncate an existing file even if later parsing fails. Helper execution failures abort. `--no_attrs` trades completeness for independence from binary policy/helper availability.

## Test Signals
Run with fixture headers and `test_dummy_policy`, alternate helper path, `--no_attrs`, verbose/debug parsing, unwritable output, and malformed headers.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/audit2allow/sepolgen-ifgen -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/audit2allow/sepolgen-ifgen-attr-helper.c -->
# sources/security-integrity/selinux/python/audit2allow/sepolgen-ifgen-attr-helper.c

## Purpose
Reads a binary SELinux policy and emits attribute access vectors in the format consumed by `sepolgen-ifgen`.

## Important APIs, Types, And Functions
Important local types/functions are `struct val_to_name`, `perm_name()`, `render_access_mask()`, `render_key()`, `struct callback_data`, `output_avrule()`, `attribute_callback()`, `load_policy()`, `usage()`, and `main()`. It uses libsepol `policydb_t`, `policy_file`, `policydb_read`, hashtab and avtab traversal, plus libselinux policy path discovery.

## Control Flow
`main()` validates `out_file [policy_file]`, loads the requested, current, or version-suffixed default binary policy, opens the output, then maps all policy types. For each `TYPE_ATTRIB`, `attribute_callback()` writes an attribute header and scans both unconditional and conditional TE avtabs. `output_avrule()` filters allowed AV rules with the attribute as source, renders source/target/class names and permission names, and writes comma-separated rows.

## State And Persistence
It writes the helper output file. It reads binary policy files and allocates/destroys a full policydb.

## Dependencies And Integration Points
It is a companion binary for the Python `sepolgen-ifgen` script and depends on libsepol's internal policydb structures.

## Risks And Edge Cases
The permission variable is not reset inside each permission-bit iteration, so stale names are a possible correctness risk if a lookup fails after a previous success. Internal libsepol structure assumptions can break with ABI changes. `load_policy(argv[2])` is unsafe when `argc == 2` because it passes an out-of-bounds argument instead of NULL.

## Test Signals
Tests should invoke with explicit and implicit policy paths, compare known attribute output for dummy policy, run under ASan/UBSan for argv and stale-pointer issues, and verify malformed policy failure cleanup.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/audit2allow/sepolgen-ifgen-attr-helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/audit2allow/test_audit2allow.py -->
# sources/security-integrity/selinux/python/audit2allow/test_audit2allow.py

## Purpose
Provides unit/integration tests for the audit2allow toolchain using local scripts and a dummy binary policy.

## Important APIs, Types, And Functions
Defines `Audit2allowTests(unittest.TestCase)` with assertion helpers `assertDenied`, `assertNotFound`, `assertFailure`, `assertSuccess`, and test methods `test_sepolgen_ifgen`, `test_audit2allow`, `test_audit2why`, and `test_xperms`. It uses `mkdtemp`, `Popen`, `PIPE`, `sys.executable`, and local files `test_dummy_policy` and `test.log`.

## Control Flow
Each test spawns a command in the current source directory. `test_sepolgen_ifgen` writes interface info to a temporary directory with the local helper and deletes it. `test_audit2allow` and `test_audit2why` run the local scripts with the dummy policy and log. `test_xperms` verifies generated output contains `allowxperm`.

## State And Persistence
Creates and removes a temporary directory/output file. Other tests are read-only aside from subprocess output.

## Dependencies And Integration Points
Runs under the audit2allow Makefile after building `test_dummy_policy` and the helper. It assumes source-directory relative paths.

## Risks And Edge Cases
The tests capture only stdout, so stderr diagnostics are not inspected despite variables named `err`. Temporary cleanup lacks `finally`, so failures can leave directories.

## Test Signals
Passing tests indicate the helper, audit2allow, audit2why, xperm path, dummy policy, and fixture log are minimally functional.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/audit2allow/test_audit2allow.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/chcat/Makefile -->
# sources/security-integrity/selinux/python/chcat/Makefile

## Purpose
Installs the `chcat` Python MLS category management script and man pages.

## Important APIs, Types, And Functions
Defines `PREFIX`, `BINDIR`, `MANDIR`, `LINGUAS`, and targets `all`, `install`, `clean`, `relabel`, and `test`. `all` depends on the `chcat` script.

## Control Flow
`install` creates the binary directory, installs `chcat` mode 755, creates man8 directory, installs `chcat.8`, and installs localized man8 pages for selected languages.

## State And Persistence
The install persists the executable script and documentation. There are no build products beyond the source script.

## Dependencies And Integration Points
The script itself depends on Python SELinux bindings, `seobject`, `chcon`, and `semanage`; this Makefile only places it in the target image.

## Risks And Edge Cases
No syntax/test target is implemented, so packaging can install a script that has not been exercised. `relabel` is a no-op.

## Test Signals
Run `python3 -m py_compile` or script help manually, staged install checks, and functional MLS category tests on an MLS-enabled SELinux system.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/chcat/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/chcat/chcat -->
# sources/security-integrity/selinux/python/chcat/chcat

## Purpose
Modifies or lists MLS/MCS categories on files or SELinux login mappings.

## Important APIs, Types, And Functions
Key functions are `verify_users()`, `chcat_user_add()`, `chcat_add()`, `chcat_user_remove()`, `chcat_remove()`, `chcat_user_replace()`, `chcat_replace()`, `check_replace()`, `isSensitivity()`, `expandCats()`, `translate()`, `usage()`, `listcats()`, `listusercats()`, and `error()`. It uses Python `selinux`, `seobject.loginRecords`, `pwd`, `subprocess.check_call`, `chcon`, and `semanage login`.

## Control Flow
Startup requires MLS and SELinux enabled. Options choose delete, list, or login mode. Listing either prints translations from `selinux_translations_path()` or user categories from `getseuserbyname()`. Delete resets targets to `s0`. Otherwise the first positional argument is parsed as comma-separated categories. Pure category lists replace the range; `+cat` and `-cat` forms add/remove one category at a time. File operations use `chcon -l`; login operations inspect current semanage login records and run `semanage login -a` or `-m`.

## State And Persistence
File mode changes filesystem labels via `chcon`. Login mode persists semanage login range changes. Listing is read-only.

## Dependencies And Integration Points
It bridges human-readable category translations, raw SELinux ranges, file labels, and semanage login mappings.

## Risks And Edge Cases
`isSensitivity()` assumes nonempty strings. `expandCats()` only expands ranges when <=25 results. Add/remove paths handle only the first category in `newcat` for file operations. Subprocess failures are counted but details are suppressed.

## Test Signals
Test on MLS-enabled systems: list translations, list user categories, replace/add/remove/delete file labels, replace/add/remove login mappings, invalid users, mixed `+/-` with replacement, translated category ranges, and subprocess failure reporting.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/chcat/chcat -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/po/Makefile -->
# sources/security-integrity/selinux/python/po/Makefile

## Purpose
Builds and installs gettext catalogs for SELinux Python tools.

## Important APIs, Types, And Functions
Defines `NLSPACKAGE=python`, gettext command variables, selected language lists, `POFILES`, `MOFILES`, and `POTFILES`. Targets are `all`, `$(POTFILE)`, `refresh-po`, `clean`, `install`, `report`, `relabel`, and `test`.

## Control Flow
`all` compiles `.po` files into `.mo` files. The POT target runs Python-aware `xgettext` over `POTFILES`, joins additional strings from the sepolicy Glade file, and replaces the POT only when changed. `refresh-po` merges translations. `install` writes catalogs as `selinux-python.mo` under locale directories.

## State And Persistence
Produces `.mo` files and may refresh `.po` catalogs. Install persists locale catalogs under `$(PREFIX)/share/locale`.

## Dependencies And Integration Points
Depends on gettext tools, a local `POTFILES` manifest, and `../sepolicy/sepolicy/sepolicy.glade` for GUI strings.

## Risks And Edge Cases
The package name `python` maps to installed catalog `selinux-python.mo`, so runtime domains must match. Missing Glade file or POTFILES entries can drop translations.

## Test Signals
`make report`, successful `msgfmt`, successful POT refresh, and runtime gettext lookup in Python tools.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/po/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/semanage/Makefile -->
# sources/security-integrity/selinux/python/semanage/Makefile

## Purpose
Installs the Python `semanage` command, `seobject.py` module, bash completion, man pages, and runs semanage tests.

## Important APIs, Types, And Functions
Defines `PYTHON`, `SBINDIR`, `MANDIR`, `PYTHONLIBDIR` via `sysconfig`, `PACKAGEDIR`, `BASHCOMPLETIONDIR`, `TARGETS=semanage`, and `BASHCOMPLETIONS=semanage-bash-completion.sh`. Targets are `all`, `install`, `test`, `clean`, and `relabel`.

## Control Flow
`all` depends on the `semanage` script. `install` creates man/sbin/package/completion directories, installs `semanage`, all `*.8` man pages and localized man pages, installs `seobject.py` into the Python purelib path, and installs completion as `semanage`. `test` runs `test-semanage.py -a`.

## State And Persistence
Install persists command scripts, Python modules, documentation, and completion. Tests may mutate their configured test environment depending on `test-semanage.py`.

## Dependencies And Integration Points
Depends on Python sysconfig path calculation and the semanage Python module consumers, especially `chcat` using `seobject`.

## Risks And Edge Cases
`PYTHONLIBDIR` is computed with `platbase`/`base` set to `PREFIX`, so cross-install layouts depend on Python's sysconfig scheme. Installing every `*.8` can pick up unintended files.

## Test Signals
Staged install path validation, import of installed `seobject`, `semanage --help`, completion install, and `make test`.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/semanage/Makefile -->

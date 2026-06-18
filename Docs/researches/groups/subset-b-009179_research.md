# subset-b-009179 research

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/monitor_test.go -->
# sources/sync-backup/syncthing/cmd/syncthing/monitor_test.go

## Purpose
This Go test file validates the monitor logging helpers implemented in `cmd/syncthing/monitor.go`, specifically rotated log file naming/retention and automatically closed append-only log files. It is not production code, but it is the main local regression signal for log rotation behavior used by `serveCmd.monitorMain` when Syncthing is running under its supervising monitor process.

## Important APIs, Types, And Functions
The file defines three tests and two small assertion helpers. `TestRotatedFile` exercises `newRotatedFile`, `rotatedFile.Write`, `rotatedFile.rotate`, and `numberedFile` through a custom `open` callback that creates files in `t.TempDir()`. `TestNumberedFile` directly checks how `numberedFile` inserts suffixes before extensions and after extensionless names. `TestAutoClosedFile` exercises `newAutoclosedFile`, `autoclosedFile.Write`, `autoclosedFile.Close`, and the underlying timer-driven close loop by inspecting `ac.fd` under `ac.mut`. `checkSize` and `checkNotExist` wrap `os.Lstat` assertions.

## Control Flow
`TestRotatedFile` creates a base `log.txt`, writes fixed test data, and checks the exact file set after each write. The chosen `maxSize` allows one full record plus a small extra byte, so the second and later full-record writes force rotation. The assertions verify the base file remains current, `.0` and `.1` are aged rotated copies, and `.2` is absent because `maxFiles` is two. `TestNumberedFile` iterates table cases for normal extensions, multi-dot names, and names without extensions. `TestAutoClosedFile` creates `_autoclose/tmp`, writes once, polls until the internal file descriptor becomes nil, writes again to confirm append-on-reopen, closes, reads the file length, then creates a second autoclosed writer to confirm new instances also append instead of truncate.

## State And Persistence Behavior
The tests create real temporary files and directories, so they validate on-disk state rather than mocks. `TestRotatedFile` uses `t.TempDir()` and registers cleanup for every opened file handle. `TestAutoClosedFile` uses a fixed `_autoclose` directory in the package working directory, with `defer os.RemoveAll` cleanup before and after the test. Persistence expectations are byte-count based: rotated logs preserve previous data in numbered files, and autoclosed files preserve existing contents through close/reopen cycles.

## Dependencies And Integration Points
The file depends on the unexported monitor helpers in the same `main` package. It uses `io`, `os`, `path/filepath`, `testing`, and `time`. The behavior under test integrates with `monitorMain`, where Syncthing log output may be sent through `newRotatedFile` and `newAutoclosedFile`, optionally wrapped by a Windows newline replacing writer. The tests indirectly protect user-facing `--logfile`, `--log-max-size`, and `--log-max-files` behavior.

## Risks And Edge Cases
The autoclosed test polls internal state with a one-second timeout, so it is somewhat timing-sensitive on heavily loaded systems. It also uses a package-relative `_autoclose` directory instead of `t.TempDir()`, which can collide with interrupted or parallel package runs if the directory is externally modified. The rotation test checks sizes but not file contents, permissions, or close errors. The custom `open` callback registers cleanup even when `os.Create` fails and `f` is nil, which is safe but means the test mostly focuses on happy-path file creation.

## Test Signals
The file itself is the test signal. Running `go test ./cmd/syncthing` or a narrower package test should execute these cases on supported platforms. Passing tests indicate log rotation naming/retention and autoclosed append behavior remain compatible with monitor logging expectations.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/monitor_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/openurl_unix.go -->
# sources/sync-backup/syncthing/cmd/syncthing/openurl_unix.go

## Purpose
This non-Windows Go file implements the platform-specific `openURL(url string) error` helper used by the Syncthing command to open the GUI URL in a browser. It covers macOS and other Unix-like platforms selected by the `!windows` build tag.

## Important APIs, Types, And Functions
The sole API is `openURL`. On Darwin it runs `open <url>` using `os/exec`. On other non-Windows platforms it runs `xdg-open <url>` and sets `cmd.SysProcAttr = &syscall.SysProcAttr{Setpgid: true}` before starting, isolating the browser opener into a separate process group. It depends on `github.com/syncthing/syncthing/lib/build` for the runtime platform flag.

## Control Flow
The function branches on `build.IsDarwin`. The macOS branch constructs and synchronously runs `exec.Command("open", url)`. The generic Unix branch constructs `exec.Command("xdg-open", url)`, attaches the process-group attribute, and synchronously returns `cmd.Run()`'s error. There is no fallback command list and no URL validation in this file.

## State And Persistence Behavior
The function does not persist Syncthing state. Its side effect is external process execution, which may launch or signal a desktop browser. It waits for the opener command to exit, but the opened browser generally outlives the command.

## Dependencies And Integration Points
Call sites in `cmd/syncthing/main.go` invoke `openURL` when handling browser-opening behavior, including initial GUI launch and browser commands. The generic Unix path depends on `xdg-open` being available in the user's environment; macOS depends on `/usr/bin/open` or the shell path resolving `open`. The process group setting matters because the monitor process and child Syncthing process perform signal handling and restarts.

## Risks And Edge Cases
Minimal environments, servers, containers, or non-XDG desktops may not have `xdg-open`, causing an error that the caller must log or surface. The function passes the URL as a separate argument, avoiding shell interpretation, but any malformed URL may still be interpreted by the platform opener. Because the command is synchronous, a hanging opener can delay the caller. Build selection means BSD, Linux, and other non-Windows non-Darwin platforms all use the same XDG assumption.

## Test Signals
There are no direct tests in this file. Useful checks include package build tests on non-Windows targets and manual or integration tests for `syncthing browser` or startup browser opening on macOS and Linux desktop environments.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/openurl_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/openurl_windows.go -->
# sources/sync-backup/syncthing/cmd/syncthing/openurl_windows.go

## Purpose
This Windows-only Go file implements `openURL(url string) error` using the native Windows shell association mechanism. It is the Windows counterpart to the Unix implementation and lets Syncthing open its GUI URL through the user's configured default browser.

## Important APIs, Types, And Functions
The file exposes only `openURL`. It converts the URL and the `"open"` verb to UTF-16 pointers via `windows.UTF16PtrFromString`, then calls `windows.ShellExecute` with `SW_SHOWNORMAL`. It imports `golang.org/x/sys/windows` rather than invoking `cmd.exe` or `rundll32`.

## Control Flow
`openURL` first converts `url` to a UTF-16 pointer and returns conversion errors immediately. It then converts the verb string and returns that error if it occurs. Finally it calls `ShellExecute` with no owner window, no parameters, no working directory, and normal show mode, returning the resulting error value directly.

## State And Persistence Behavior
The function does not modify Syncthing configuration or files. Its observable side effect is delegated to Windows ShellExecute, which may start a browser process, reuse an existing browser instance, or display a shell-level error depending on file association and desktop state.

## Dependencies And Integration Points
This function is selected by the `windows` build tag and shares the same package-level signature as the Unix implementation. Call sites in `cmd/syncthing/main.go` use it for GUI browser startup and explicit browser-opening commands. It relies on Windows URL association configuration and the `golang.org/x/sys/windows` syscall wrapper.

## Risks And Edge Cases
`UTF16PtrFromString` rejects strings containing NUL bytes, so malformed input is stopped before the syscall. `ShellExecute` behavior depends heavily on user profile, desktop session, and registry associations; service or headless contexts may fail or do nothing visible. Because the return is the syscall wrapper's error, callers need to handle platform-specific shell errors. The file has no URL scheme allow-list; it assumes callers pass the GUI URL or another trusted URL.

## Test Signals
There are no direct unit tests. The practical signals are Windows package builds and manual tests for `syncthing browser` or automatic GUI opening in an interactive Windows session.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/openurl_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/perfstats_unix.go -->
# sources/sync-backup/syncthing/cmd/syncthing/perfstats_unix.go

## Purpose
This Go file implements periodic performance statistics collection for supported Unix-like platforms. It is compiled for `!solaris && !windows` and writes process CPU, memory, network throughput, and database-size samples to a tab-separated CSV-like file.

## Important APIs, Types, And Functions
`startPerfStats` launches `savePerfStats` in a goroutine using a filename derived from the current PID. `savePerfStats(file string)` creates the output file, writes a header, and samples every 250 milliseconds. `cpusec` converts `syscall.Rusage` user plus system time to seconds. The generic `rate[T number]` computes per-second deltas for floats and integers, where `number` is constrained by `golang.org/x/exp/constraints`.

## Control Flow
The collection goroutine creates `perfstats-<pid>.csv` and panics if creation fails. It initializes previous resource and memory snapshots, writes a header row, then ranges forever over `time.NewTicker(250 * time.Millisecond).C`. On each tick it reads current resource usage, runtime memory stats, protocol traffic counters, computes elapsed time from the previous sample, normalizes Darwin `Maxrss`, and writes one line containing elapsed time since start, CPU rate, heap-ish memory in KiB, RSS KiB, network input/output rates in KB/s, and database directory size in KiB. Previous counters are updated at the end of each iteration.

## State And Persistence Behavior
The file creates a persistent `perfstats-<pid>.csv` in the current working directory and never closes it because the sampling loop is unbounded for process lifetime. It repeatedly reads the Syncthing database directory size through `locations.Get(locations.Database)` and `osutil.DirSize`, which can be relatively expensive depending on database size and filesystem behavior. It reads process-global network counters from `protocol.TotalInOut`.

## Dependencies And Integration Points
`cmd/syncthing/main.go` calls `startPerfStats` when the corresponding runtime/debug option is enabled. The implementation integrates with Go runtime memory statistics, Unix `getrusage`, Syncthing build flags, configured locations, filesystem utilities, and protocol traffic accounting. The unsupported Solaris/Windows file provides a no-op implementation with the same function signature.

## Risks And Edge Cases
`prevTime` starts as the zero time, so the first computed `timeDiff` is enormous and first-row rates are not meaningful; subsequent rows are meaningful after `prevTime` is set. `os.Create` failure panics, which is acceptable for an explicit diagnostic mode but can terminate startup. The ticker is not stopped, and the file descriptor is not closed during normal process lifetime. `DirSize` every 250 ms can add overhead. RSS units differ by platform, so the Darwin adjustment is necessary but still depends on platform conventions.

## Test Signals
There are no direct tests. Build coverage across Unix targets protects build tags and syscall use. Manual diagnostic validation should check that enabling perf stats creates the expected file, writes the header, and updates rows with plausible CPU/network/database values.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/perfstats_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/perfstats_unsupported.go -->
# sources/sync-backup/syncthing/cmd/syncthing/perfstats_unsupported.go

## Purpose
This small Go file supplies a no-op `startPerfStats` implementation for platforms where the Unix perf stats collector is not compiled: Solaris and Windows. It keeps the rest of the command code platform-neutral.

## Important APIs, Types, And Functions
The only function is `startPerfStats()`, with an empty body. Its signature matches the supported Unix implementation.

## Control Flow
There is no runtime control flow. If the binary is built with `solaris` or `windows` tags, calls to `startPerfStats` return immediately and no file is created.

## State And Persistence Behavior
The function performs no I/O, allocates no state, starts no goroutines, and persists nothing. This avoids relying on unsupported or differently shaped resource-accounting APIs on Solaris and Windows.

## Dependencies And Integration Points
The file is selected by `//go:build solaris || windows`. It integrates with `cmd/syncthing/main.go`, which can call `startPerfStats` without platform conditionals. The supported implementation lives in `perfstats_unix.go`.

## Risks And Edge Cases
Users enabling perf stats on Windows or Solaris get silent no-op behavior unless higher-level command help documents the platform limitation. Any future code expecting output files after calling `startPerfStats` must account for this build-specific no-op.

## Test Signals
The primary signal is successful compilation on Windows and Solaris targets. There are no direct tests because behavior is intentionally empty.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/perfstats_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/traceback.go -->
# sources/sync-backup/syncthing/cmd/syncthing/traceback.go

## Purpose
This Go file adjusts Go runtime panic traceback behavior during package initialization so Syncthing panic logs include all application goroutines. It improves crash diagnostics for the monitor and crash-reporting pipeline.

## Important APIs, Types, And Functions
The only code is an `init` function calling `debug.SetTraceback("all")` from `runtime/debug`. The file is gated by `//go:build go1.7`, which is always true for modern supported Go versions but records the historical API requirement.

## Control Flow
The `init` function runs automatically before `main`. It does not branch or return errors. Once set, the runtime traceback setting affects subsequent panics and fatal runtime traces in the process.

## State And Persistence Behavior
The file changes process-global runtime debug state. It does not write files directly, but it changes the content of panic output that may later be captured by `monitor.go` into timestamped panic logs and potentially uploaded by the crash-reporting flow.

## Dependencies And Integration Points
The primary integration is with `cmd/syncthing/monitor.go`, where stderr lines beginning with panic/fatal/runtime prefixes start panic-log capture. More complete goroutine traces make those captured logs more useful. It also affects any direct process panic output outside the monitor path.

## Risks And Edge Cases
Including all goroutines can make panic logs larger and may include more contextual data from unrelated goroutines. That is usually desirable for diagnostics, but it can increase log size and privacy exposure in crash reports. Because it is an unconditional init-time process setting, tests and tools in this package inherit the same traceback behavior.

## Test Signals
There are no direct tests. Crash receiver fixtures and manual panic testing can confirm that panic logs include multiple goroutines rather than only the crashing goroutine.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/syncthing/traceback.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/compat.yaml -->
# sources/sync-backup/syncthing/compat.yaml

## Purpose
This YAML file records release compatibility requirements by Go runtime version. During release builds it is transformed into `compat.json`, which is included with releases and later used by upgrade infrastructure to decide whether a release is compatible with a client's operating system version.

## Important APIs, Types, And Functions
The file is data, not executable code. Each top-level list item has `runtime: go1.xx` and `requirements` mapping OS names to minimum OS versions. The data shape matches `upgrade.ReleaseCompatibility` in `lib/upgrade/upgrade_common.go`, with `Runtime string` and `Requirements map[string]string`. `build.go` reads `compat.yaml`, unmarshals it with YAML, selects the entry whose runtime prefixes `runtime.Version()`, and writes `compat.json`.

## Control Flow
There is no runtime flow inside the YAML. The build flow reads all entries, scans in order for a matching Go runtime, marshals that one entry as JSON, and fails if no runtime matches. Upgrade filtering later treats missing compatibility data as compatible, missing OS entries as compatible, and compares client OS versions against the required version when an OS entry exists.

## State And Persistence Behavior
The source file is maintained in the repository and does not change at runtime. Its build-time output is `compat.json`, a release artifact. Current entries cover Go 1.21 through Go 1.26 and list minimum Darwin, Linux, and Windows versions, with comments documenting upstream Go release-policy sources.

## Dependencies And Integration Points
The file integrates with `build.go` release tooling and `cmd/infra/stupgrades`, which attaches and consumes `compat.json` release metadata. It depends on Go runtime support policy and OS version strings remaining comparable by Syncthing's version comparison logic. It also influences GUI/upgrade behavior because incompatible releases should not be offered to clients below the minimum OS version.

## Risks And Edge Cases
Stale or incorrect minimum versions can either block valid upgrades or offer upgrades that cannot run. The runtime match uses prefix logic against `runtime.Version()`, so future Go versions require an entry or the build fails. Comments cite evolving Go documentation; those comments are useful but not machine-checked. Version string comparison must remain compatible with Darwin kernel versions, Linux kernel versions, and Windows NT version strings.

## Test Signals
The build-time `writeCompatJSON` path is the main validation signal: release builds fail if the current runtime is absent or YAML parsing breaks. Upgrade service tests or manual checks should validate that generated `compat.json` filters releases correctly for representative OS/user-agent versions.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/compat.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/etc/freebsd-rc/syncthing -->
# sources/sync-backup/syncthing/etc/freebsd-rc/syncthing

## Purpose
This shell script is a FreeBSD `rc.d` service template for running Syncthing as a daemon. It documents rc.conf knobs and starts Syncthing under a configured user with a pidfile and logfile.

## Important APIs, Types, And Functions
The script uses FreeBSD's `/etc/rc.subr` framework. It sets `name=syncthing`, `rcvar=syncthing_enable`, `start_cmd=syncthing_start`, and defines `syncthing_start` plus `syncthing_cleanup`. Configurable variables include `syncthing_enable`, `syncthing_home`, `syncthing_log_file`, `syncthing_user`, and `syncthing_group`. It invokes `/usr/sbin/daemon` with `-cf -p <pidfile> -u <user>`.

## Control Flow
After loading rc config, default variable values are assigned. The start function announces startup, creates and chowns the pidfile and logfile, then daemonizes `/usr/local/bin/syncthing serve` with `--home` and `--logfile` flags when configured. At the end, `run_rc_command $1` dispatches the requested rc action. `syncthing_cleanup` removes the pidfile if present, though the file does not explicitly wire it as a stop hook in the visible script.

## State And Persistence Behavior
The script creates `/var/run/syncthing.pid` and `/var/log/syncthing.log` by default. Configuration and runtime state are placed under `/usr/local/etc/syncthing` unless overridden. Ownership is set to the configured service user so the daemon can write its pid/log/config data.

## Dependencies And Integration Points
It integrates with FreeBSD rc service management, rc.conf, `/usr/sbin/daemon`, and the Syncthing CLI. The default binary path is `/usr/local/bin/syncthing`, matching FreeBSD package conventions. It maps service-level configuration into Syncthing's `serve` command and file-location flags.

## Risks And Edge Cases
Variable expansions are mostly unquoted in the daemon command and touch/chown lines, so paths with spaces or shell metacharacters are risky. The pidfile and logfile directories must already exist and be writable by root during service startup. The `syncthing_group` default is computed but not used in the start command. Because this is a template, the hard-coded defaults may need packaging-specific adjustments.

## Test Signals
Validation is mainly operational: install the rc script, set `syncthing_enable=YES`, run `service syncthing start`, and check pid/log/config ownership. Shell linting can catch quoting issues, but the meaningful signal is FreeBSD service startup and clean shutdown behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/etc/freebsd-rc/syncthing -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/etc/linux-desktop/syncthing-start.desktop -->
# sources/sync-backup/syncthing/etc/linux-desktop/syncthing-start.desktop

## Purpose
This desktop entry starts the Syncthing daemon from a Linux desktop session. It is intended for graphical autostart/menu integration rather than system service management.

## Important APIs, Types, And Functions
The file follows the freedesktop `.desktop` entry format. Important keys are `Name=Start Syncthing`, `GenericName=File synchronization`, `Exec=syncthing serve --no-browser --logfile=default`, `Icon=syncthing`, `Terminal=false`, `Type=Application`, `Keywords=synchronization;daemon;`, and `Categories=Network;FileTransfer;P2P`.

## Control Flow
There is no internal control flow. A desktop environment or autostart manager reads the entry and executes the `Exec` command when the user launches it or when it is installed as an autostart item. The command starts Syncthing in serve mode, disables automatic browser opening, and uses Syncthing's default logfile handling.

## State And Persistence Behavior
The desktop file itself persists no runtime state. The launched Syncthing process uses the user's normal home/config/data locations and writes logs according to `--logfile=default`. Because it runs in the user's desktop session, it inherits user environment and permissions.

## Dependencies And Integration Points
The entry depends on `syncthing` being in the desktop session's PATH and on the icon theme/package providing a `syncthing` icon. It complements service templates under `etc/linux-systemd`, `linux-runit`, and `linux-upstart` for users who prefer session startup.

## Risks And Edge Cases
If PATH does not include the Syncthing binary, launch fails silently or with a desktop-specific error. Multiple autostart mechanisms can accidentally start duplicate Syncthing processes. `--no-browser` prevents an unwanted browser window, but users still need separate UI access via the browser command or web URL.

## Test Signals
Desktop-file validation tools can verify syntax. Manual testing should install or open the desktop entry in a Linux desktop session and confirm Syncthing starts in the background without opening a browser.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/etc/linux-desktop/syncthing-start.desktop -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/etc/linux-desktop/syncthing-ui.desktop -->
# sources/sync-backup/syncthing/etc/linux-desktop/syncthing-ui.desktop

## Purpose
This desktop entry opens the Syncthing Web UI from a Linux desktop environment. It assumes the Syncthing daemon is already running.

## Important APIs, Types, And Functions
The file uses standard `.desktop` keys. `Name=Syncthing Web UI`, `GenericName=File synchronization UI`, `Exec=syncthing browser`, `Icon=syncthing`, `Terminal=false`, `Type=Application`, `Keywords=synchronization;interface;`, and `Categories=Network;FileTransfer;P2P` define how desktop launchers present and execute it.

## Control Flow
There is no logic in the file. A desktop launcher executes `syncthing browser`, which delegates to Syncthing's command-line browser-opening path and ultimately the platform-specific `openURL` helper after resolving the GUI URL.

## State And Persistence Behavior
The desktop file does not store state. It may cause the Syncthing command to read local configuration to determine the GUI URL and then launch the user's default browser. It does not start the daemon itself.

## Dependencies And Integration Points
It depends on a working `syncthing` CLI in PATH, a running Syncthing instance, and desktop/browser integration. It pairs with `syncthing-start.desktop`, where one entry starts the background process and this one opens the interface.

## Risks And Edge Cases
If Syncthing is not running, `syncthing browser` may fail or open a URL that is unreachable. Headless or misconfigured browser environments can fail in the platform opener. As with the start desktop entry, PATH assumptions are packaging-sensitive.

## Test Signals
Syntax can be checked with `desktop-file-validate`. Functional testing should launch the entry from a desktop menu and confirm it opens the configured Syncthing Web UI.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/etc/linux-desktop/syncthing-ui.desktop -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/etc/linux-runit/log/run -->
# sources/sync-backup/syncthing/etc/linux-runit/log/run

## Purpose
This short shell script is the runit log service for Syncthing. It receives stdout/stderr from the main runit service and forwards log lines to syslog via `logger`.

## Important APIs, Types, And Functions
The script consists of a POSIX shell shebang and `exec logger -t syncthing`. The `-t` tag marks syslog entries with `syncthing`.

## Control Flow
When runit starts the log service, the script immediately replaces the shell with `logger`. It reads from standard input as supplied by runit's logging pipeline and writes to the system logging facility.

## State And Persistence Behavior
The script itself persists no files. Persistence is delegated to the system logger configuration, which may write to journald, syslog files, or another backend depending on the distribution.

## Dependencies And Integration Points
It integrates with runit's paired service directory layout, where `etc/linux-runit/run` starts Syncthing and redirects stderr to stdout. It depends on a `logger` command compatible with `-t`.

## Risks And Edge Cases
If `logger` is unavailable or syslog is not running, runit log capture may fail. Because this script does not use `svlogd`, log retention and rotation are entirely outside this service directory. Very high log volume can stress syslog rather than a runit-managed log directory.

## Test Signals
Operational testing should start the runit service and confirm Syncthing output appears in syslog with the `syncthing` tag. Shell syntax is minimal and should be portable across `/bin/sh`.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/etc/linux-runit/log/run -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/etc/linux-runit/run -->
# sources/sync-backup/syncthing/etc/linux-runit/run

## Purpose
This runit service script starts Syncthing under a configured non-root user. It is a simple template for systems using runit instead of systemd or other init systems.

## Important APIs, Types, And Functions
The script sets `USERNAME=jb`, `HOME="/home/$USERNAME"`, and `SYNCTHING="$HOME/bin/syncthing"`, then runs `exec 2>&1` followed by `exec chpst -u "$USERNAME" "$SYNCTHING" serve --logflags 0`. `chpst` is runit's privilege-change utility.

## Control Flow
On service start, the shell exports user-specific environment, redirects stderr to stdout for the paired log service, and replaces itself with Syncthing running as the configured user. Runit supervises the process and restarts according to service configuration.

## State And Persistence Behavior
Syncthing runs with `HOME=/home/jb` by default and therefore uses that user's normal config, database, and default folder locations unless the binary or config says otherwise. Logs go to stdout/stderr and then to the runit log service.

## Dependencies And Integration Points
It depends on runit, `chpst`, a real user named `jb` unless customized, and a Syncthing binary at `/home/jb/bin/syncthing`. It integrates with `etc/linux-runit/log/run` for logging and with Syncthing's `serve` command. `--logflags 0` adjusts Syncthing log formatting for supervisor-managed logs.

## Risks And Edge Cases
The template contains hard-coded example user and binary paths, so using it unmodified is likely wrong for packaged installs. If `HOME` and `USERNAME` diverge from system account metadata, Syncthing may read or write unexpected locations. There is no explicit `STNORESTART` or `--no-restart`; supervisor and Syncthing monitor behavior should be checked to avoid double supervision in a deployment.

## Test Signals
Functional validation is starting the runit service with customized variables and confirming the process runs as the intended user, logs through the paired logger, and restarts correctly under runit supervision.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/etc/linux-runit/run -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/etc/linux-sysctl/30-syncthing.conf -->
# sources/sync-backup/syncthing/etc/linux-sysctl/30-syncthing.conf

## Purpose
This sysctl configuration raises Linux maximum socket receive and send buffer sizes to support better QUIC performance. It is a deployment tuning file, not Syncthing application logic.

## Important APIs, Types, And Functions
The file sets `net.core.rmem_max = 7340032` and `net.core.wmem_max = 7340032`, with a comment linking the rationale to QUIC UDP buffer-size guidance. The value is 7 MiB.

## Control Flow
There is no executable flow. Linux sysctl tooling reads the file, usually from `/etc/sysctl.d/`, and applies the kernel parameters at boot or when `sysctl --system` is run.

## State And Persistence Behavior
The file persists desired kernel networking defaults. Applied values change kernel runtime state until reboot or later sysctl changes; installation in sysctl.d makes them reapply across boots.

## Dependencies And Integration Points
It integrates with Linux kernel networking and QUIC libraries used by Syncthing's transport stack. Larger UDP buffers reduce packet loss risk for high-throughput QUIC connections. It is distribution/package integration material.

## Risks And Edge Cases
Raising global max buffer sizes affects the whole system, not only Syncthing. Administrators may reject package-installed sysctl changes or need different values for constrained systems. The file sets maxima, not per-socket buffers directly; application/socket behavior still determines actual allocation.

## Test Signals
Validation consists of applying the sysctl config and checking `sysctl net.core.rmem_max net.core.wmem_max`. Performance testing should look for reduced QUIC buffer warnings and improved transfer stability on high-throughput links.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/etc/linux-sysctl/30-syncthing.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/etc/linux-systemd/system/syncthing@.service -->
# sources/sync-backup/syncthing/etc/linux-systemd/system/syncthing@.service

## Purpose
This system-level systemd template runs Syncthing as a named user instance (`syncthing@<user>.service`). It includes extensive default hardening intended to reduce damage if the Syncthing process is compromised while still allowing normal file synchronization with user-specific permissions.

## Important APIs, Types, And Functions
The unit has `[Unit]`, `[Service]`, and `[Install]` sections. Core service settings include `User=%i`, log-format environment variables for syslog-friendly output, `ExecStart=/usr/bin/syncthing serve --no-browser --no-restart`, `Restart=on-failure`, `SuccessExitStatus=3 4`, and `RestartForceExitStatus=3 4`. Hardening directives include `ProtectSystem=full`, multiple `ProtectKernel*` options, `NoNewPrivileges=true`, `RestrictSUIDSGID=true`, `MemoryDenyWriteExecute=true`, `RestrictNamespaces=true`, `RestrictAddressFamilies=AF_INET AF_INET6 AF_NETLINK AF_UNIX`, capability bounding, `PrivateTmp=disconnected`, `PrivateDevices=true`, `PrivatePIDs=true`, `ProtectProc=invisible`, `ProcSubset=pid`, `SystemCallFilter=@system-service`, `SystemCallErrorNumber=EPERM`, `UMask=7027`, and `InaccessiblePaths=-/nonexistent`.

## Control Flow
Systemd starts the unit after `network.target`, as the instance user named by `%i`. Syncthing is run in foreground `serve` mode with browser opening and internal restart disabled, leaving restart supervision to systemd. Exit statuses 3 and 4 are treated as successful and also force restart, matching Syncthing's special restart/upgrade exit semantics. On failure, systemd restarts after one second, bounded by `StartLimitIntervalSec=60` and `StartLimitBurst=4`.

## State And Persistence Behavior
Syncthing state is stored in the target user's normal home/config locations unless overridden by drop-ins or environment. The unit itself does not define `StateDirectory`; it relies on user ownership and normal filesystem access. Hardening makes `/usr`, `/boot`, `/efi`, and `/etc` read-only and hides or restricts many kernel/system interfaces. The unit's `UMask=7027` restricts world-readable creation by default while still allowing Syncthing to explicitly chmod synchronized files.

## Dependencies And Integration Points
This is a packaging/deployment integration point for systemd systems. It integrates with journald through Syncthing log-format environment variables, systemd restart semantics, systemd sandboxing features, and optional drop-in overrides for ownership synchronization or custom shared paths. Comments point users to `systemd-analyze security` and drop-in locations.

## Risks And Edge Cases
The hardening is intentionally best-effort and may be ignored by old systemd/kernel combinations. Some options can break advanced features: `MemoryDenyWriteExecute` can affect external tools if executed in-process context, `NoExecPaths` examples are commented because external file versioning may need arbitrary binaries, and capability settings require careful drop-ins for `syncOwnership`. `ProtectSystem=full` is safe for many cases, but stricter optional settings require explicit `ReadWritePaths`. `RestrictAddressFamilies` must continue allowing the address families Syncthing needs, including AF_NETLINK for interface discovery.

## Test Signals
Operational tests should run `systemctl start syncthing@USER.service`, inspect `journalctl --unit`, confirm restarts on Syncthing restart/upgrade exit codes, and run `systemd-analyze security`. Feature tests should cover normal syncing, discovery, QUIC/TCP connectivity, optional ownership sync when configured, and external versioning if users enable extra hardening.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/etc/linux-systemd/system/syncthing@.service -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/etc/linux-systemd/user/syncthing.service -->
# sources/sync-backup/syncthing/etc/linux-systemd/user/syncthing.service

## Purpose
This user-level systemd unit runs Syncthing inside a user's systemd session. It is simpler than the system-wide template and targets per-user autostart with moderate hardening.

## Important APIs, Types, And Functions
The unit defines `Description`, `Documentation`, `StartLimitIntervalSec=60`, `StartLimitBurst=4`, log-format environment variables, `ExecStart=/usr/bin/syncthing serve --no-browser --no-restart`, `Restart=on-failure`, `RestartSec=1`, `SuccessExitStatus=3 4`, `RestartForceExitStatus=3 4`, and hardening directives `SystemCallArchitectures=native`, `MemoryDenyWriteExecute=true`, and `NoNewPrivileges=true`. It installs into `WantedBy=default.target`.

## Control Flow
When enabled for a user, systemd starts Syncthing as part of the user's default target. Syncthing remains in foreground serve mode and delegates restart handling to systemd. Special exit statuses used for restart/upgrade are configured so systemd restarts rather than treating them as ordinary failures.

## State And Persistence Behavior
The process uses the invoking user's home directory and normal Syncthing state locations. Logs go to the user journal with formatting controlled by `STLOG...` environment variables. There is no pidfile or explicit state directory in the unit.

## Dependencies And Integration Points
It integrates with systemd user services, desktop/session startup, journald, and Syncthing's `serve` command. Compared with the system unit, it avoids `User=` because user managers already run as the target user.

## Risks And Edge Cases
User services require a working systemd user manager and may stop at logout unless lingering or desktop session behavior keeps them alive. The hardening is intentionally lighter than the system unit, so security posture differs between install modes. The hard-coded `/usr/bin/syncthing` path must match packaging. Optional ownership sync capabilities are commented as a hint but are generally more complex in user units.

## Test Signals
Validation should enable and start the unit with `systemctl --user`, inspect `journalctl --user-unit syncthing.service`, and confirm automatic restart on Syncthing restart exit codes. Desktop logout/login behavior should be tested according to distribution expectations.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/etc/linux-systemd/user/syncthing.service -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/etc/linux-upstart/system/syncthing.conf -->
# sources/sync-backup/syncthing/etc/linux-upstart/system/syncthing.conf

## Purpose
This Upstart system job template runs Syncthing as a system-managed service for a configured user. It targets older Linux distributions using Upstart.

## Important APIs, Types, And Functions
The job uses Upstart stanzas: `description`, `start on`, `stop on`, `env`, `setuid`, `setgid`, `exec`, and `respawn`. It sets `STNORESTART=yes`, `HOME=/home/$USER`, runs as `$USER`, executes `/usr/local/bin/syncthing`, and respawns on failure.

## Control Flow
Upstart starts the job when local filesystems are available and a non-loopback network device comes up. It stops outside runlevels 2-5. The service runs Syncthing directly; `STNORESTART=yes` disables Syncthing's own monitor restart behavior so Upstart owns respawn behavior.

## State And Persistence Behavior
Syncthing state is tied to `HOME=/home/$USER` and the configured Unix user. The job itself has no logfile path; logging depends on Upstart's handling of job stdout/stderr and Syncthing defaults.

## Dependencies And Integration Points
It integrates with Upstart event names, Linux runlevels, user/group privileges, and the Syncthing binary at `/usr/local/bin/syncthing`. It is an alternative to systemd/runit templates.

## Risks And Edge Cases
`$USER` must be provided by job configuration or environment; if not, `HOME`, `setuid`, and `setgid` are invalid or surprising. The `exec` command does not include modern `serve` subcommand flags, so behavior depends on Syncthing CLI compatibility with legacy invocation. Upstart itself is legacy on most current Linux distributions.

## Test Signals
Testing requires an Upstart system: configure `USER`, start the job, confirm process ownership, verify respawn on crash, and confirm logs/state land under the intended user home.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/etc/linux-upstart/system/syncthing.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/etc/linux-upstart/user/syncthing.conf -->
# sources/sync-backup/syncthing/etc/linux-upstart/user/syncthing.conf

## Purpose
This Upstart user-session job starts Syncthing when a desktop session starts and stops it when the desktop session ends. It is intended for older desktop environments with Upstart user jobs.

## Important APIs, Types, And Functions
The job defines `env SYNCTHING_EXE="/usr/local/bin"`, `description`, `start on desktop-start`, `stop on desktop-end`, `env STNORESTART=yes`, `respawn`, and an `exec $SYNCTHING_EXE --no-browser` command. The comments describe the executable location and supervisor relationship.

## Control Flow
Upstart launches the job on the `desktop-start` event and stops it on `desktop-end`. `STNORESTART=yes` tells Syncthing not to manage its own restart loop, while `respawn` lets Upstart restart failed processes. Browser opening is disabled.

## State And Persistence Behavior
The job runs in the user's session context and uses that user's environment and default Syncthing locations. It persists no job-specific files. Logs are handled by Upstart/session logging.

## Dependencies And Integration Points
It depends on Upstart user-session events and a Syncthing executable configured by `SYNCTHING_EXE`. It is conceptually similar to the Linux desktop autostart file but uses Upstart supervision and respawn behavior.

## Risks And Edge Cases
The variable name/comment says executable location, but the default value is a directory and the `exec` line uses `$SYNCTHING_EXE --no-browser`, which appears inconsistent unless customized to a full binary path. The command also omits the modern `serve` subcommand. Upstart user sessions are legacy and distribution-specific, so events may not fire on modern desktops.

## Test Signals
Functional testing should occur on an Upstart desktop session: trigger desktop-start, confirm Syncthing runs without opening a browser, verify respawn, and confirm desktop-end stops the process. The executable variable should be customized and tested explicitly.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/etc/linux-upstart/user/syncthing.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/etc/solaris-smf/syncthing.xml -->
# sources/sync-backup/syncthing/etc/solaris-smf/syncthing.xml

## Purpose
This XML file is a Solaris Service Management Facility manifest for running Syncthing as `site/syncthing`. It defines service dependencies, credentials, start/stop methods, and SMF metadata.

## Important APIs, Types, And Functions
The manifest uses the SMF service bundle DTD. It declares a single-instance service with a default enabled instance, dependencies on `svc:/milestone/network:default` and `svc:/system/filesystem/local`, method credentials `user="jb" group="other"`, a start method executing `/home/jb/bin/syncthing`, a stop method `:kill`, and framework properties `duration=child` plus `ignore_error=core,signal`.

## Control Flow
SMF imports the manifest and starts the default instance once network and local filesystem dependencies are satisfied. The start method runs Syncthing with `HOME=/home/jb` and `STNORESTART=1` in the method environment. SMF tracks the child process and uses `:kill` for stop.

## State And Persistence Behavior
Syncthing state is under `/home/jb` by default. The manifest persists service configuration in the SMF repository after import. Runtime logs and restarts are governed by SMF and Syncthing defaults.

## Dependencies And Integration Points
It integrates with Solaris SMF, service dependencies, method credentials, and Syncthing's binary/environment. `STNORESTART=1` delegates supervision to SMF. The unsupported perfstats Go file also treats Solaris specially, so this platform has distinct runtime support considerations.

## Risks And Edge Cases
The manifest is strongly example-specific: user `jb`, group `other`, binary path `/home/jb/bin/syncthing`, and home directory all need customization. XML whitespace includes a visibly misaligned `HOME` envvar line but remains structurally valid. If SMF duration or restart semantics do not match Syncthing's foreground behavior, supervision may be unreliable.

## Test Signals
Validation should import the manifest with SMF tools, inspect service properties, start/stop the service, and confirm the process runs as the intended user with the intended home directory. XML validation against the SMF DTD can catch structural errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/etc/solaris-smf/syncthing.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-ar.json -->
# sources/sync-backup/syncthing/gui/default/assets/lang/lang-ar.json

## Purpose
This JSON file provides Arabic translations for the default Syncthing web GUI. It maps English source strings used by Angular `translate` directives and filters to Arabic UI strings, with one nested `theme.name` object for theme display names.

## Important APIs, Types, And Functions
The file is data consumed by `angular-translate` through `useStaticFilesLoader({prefix: 'assets/lang/lang-', suffix: '.json'})`. It contains 558 top-level keys, no empty string values, and one object-valued key: `theme` with `name.black`, `name.dark`, `name.default`, and `name.light`. Arabic is included in `valid-langs.js`, so it is advertised to the locale service.

## Control Flow
At runtime the GUI selects a language key such as `ar`, requests `assets/lang/lang-ar.json`, and merges these translations with fallback language `en`. Template placeholders in English keys like `{%name%}` correspond to Angular translate values, while translated values use Angular interpolation markers such as `{{name}}`.

## State And Persistence Behavior
The file persists generated translation data in the source tree. It stores no user state. The nearby `README.txt` says files in this directory are autogenerated from Weblate and should not be manually edited.

## Dependencies And Integration Points
It integrates with Syncthing's Angular GUI templates, `valid-langs.js`, `prettyprint.js`, Weblate translation automation, and any code extracting source strings from templates. It must preserve JSON validity, exact English keys, interpolation variables, and nested object shape expected by theme rendering.

## Risks And Edge Cases
Arabic is right-to-left, so UI layout can expose directionality and punctuation issues. Several translated placeholder values use `{{...}}`, which is expected by angular-translate, but placeholder name drift would break runtime substitution. Translation strings may include quotes and punctuation around interpolations, so escaping and bidirectional rendering should be checked. Since the file is generated, manual local fixes risk being overwritten.

## Test Signals
`jq` parses the file successfully. GUI testing should switch to Arabic, confirm it appears as an available language, inspect dialogs with interpolated values, and verify theme names and right-to-left rendering are acceptable. Translation CI should compare keys against the English source catalog.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-ar.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-az.json -->
# sources/sync-backup/syncthing/gui/default/assets/lang/lang-az.json

## Purpose
This JSON file is the Azerbaijani translation asset placeholder for the Syncthing web GUI. In the current source it is an empty JSON object, so it provides no translated strings.

## Important APIs, Types, And Functions
The file is valid JSON with zero keys. It has no `theme` object and no string mappings. The same `angular-translate` static loader could load it if the `az` language key were selected, but `az` is not listed in the observed `valid-langs.js`, so normal GUI locale selection does not advertise it.

## Control Flow
If loaded directly or by a custom locale setting, the translation table contributes no keys. Angular-translate would fall back to English for missing keys because the GUI config sets `fallbackLanguage('en')`. Under normal UI flow, the language list excludes `az`, so the file is effectively dormant.

## State And Persistence Behavior
The file persists an empty translation catalog generated or retained in the language assets directory. It stores no user state. Its presence may indicate an incomplete Weblate language or a language intentionally not yet enabled.

## Dependencies And Integration Points
It shares the same naming convention as other `lang-<locale>.json` files and can be addressed by the static loader. Its practical integration is limited because `valid-langs.js` and `prettyprint.js` do not include Azerbaijani in the inspected source.

## Risks And Edge Cases
The main risk is accidental enablement: adding `az` to `valid-langs.js` without adding translations would produce an English UI under an Azerbaijani language choice. Automation that assumes every language file has keys or a `theme` object must handle this empty object. Since the file is autogenerated, deleting or editing it manually may conflict with translation import tooling.

## Test Signals
`jq` confirms the file parses and has zero keys. Useful validation is checking that `az` remains absent from `valid-langs.js` until translations are populated, or adding coverage that enabled languages have a minimum key count.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-az.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-be.json -->
# sources/sync-backup/syncthing/gui/default/assets/lang/lang-be.json

## Purpose
This JSON file provides Belarusian translations for part of the Syncthing web GUI. It maps English source strings to Belarusian strings, but has much lower coverage than the fully enabled language files in this subset.

## Important APIs, Types, And Functions
The file is a flat JSON object with 197 top-level keys, no empty string values, and no object-valued `theme` key. It follows the same English-key lookup model used by `angular-translate`. Belarusian is not present in the inspected `valid-langs.js`, so the normal locale selector does not advertise it.

## Control Flow
If the GUI loads language key `be`, these entries would satisfy matching translation lookups and fallback English would handle missing strings. Under the normal configured locale list, users cannot select `be`, so this file is currently a dormant or not-yet-enabled translation catalog.

## State And Persistence Behavior
The file persists generated translation content and no user state. The language asset README says these files are auto-generated from Weblate, so source-of-truth updates should happen through translation tooling.

## Dependencies And Integration Points
It depends on exact English source keys matching GUI templates and code. Placeholder-bearing entries use Angular interpolation syntax such as `{{name}}` and `{{count}}`. Because it is not in `valid-langs.js` or `prettyprint.js`, enabling it also requires updating language metadata.

## Risks And Edge Cases
Partial coverage means enabling this language would produce a mixed Belarusian/English UI. Absence of the nested `theme` translations may leave theme names in fallback language. Some entries remain visibly English, such as the observed `Upgrade To {{version}}`, which signals incomplete translation quality. Placeholder preservation must be checked before enabling.

## Test Signals
`jq` confirms valid JSON and 197 keys. Translation validation should compare key coverage against `lang-en.json`, check placeholder variable parity, and verify `be` stays absent from `valid-langs.js` until coverage and quality are acceptable.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-be.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-bg.json -->
# sources/sync-backup/syncthing/gui/default/assets/lang/lang-bg.json

## Purpose
This JSON file provides Bulgarian translations for the Syncthing web GUI. It is a full enabled language asset mapping English GUI strings to Bulgarian strings.

## Important APIs, Types, And Functions
The file contains 558 top-level keys, no empty string values, and one object-valued `theme` key containing Bulgarian theme names for black, dark, default, and light. It is consumed by `angular-translate` via the static language file loader. Bulgarian `bg` is present in `valid-langs.js` and `prettyprint.js`, so it is available through normal language selection.

## Control Flow
When the selected locale is `bg`, the GUI requests `assets/lang/lang-bg.json`. Translation directives and filters look up English source keys in this object, interpolate values through Angular syntax such as `{{foldertype}}`, and fall back to English for any missing key.

## State And Persistence Behavior
The file is generated translation data and stores no runtime state. It is loaded by the browser as a static asset and cached according to normal web asset behavior.

## Dependencies And Integration Points
It integrates with Angular templates, source string extraction, language metadata files, and Weblate automation. The nested `theme.name` object is an integration point for theme display labels rather than ordinary sentence translation. Placeholder-heavy strings must preserve variable names from templates.

## Risks And Edge Cases
Bulgarian text length can differ significantly from English and may stress compact UI elements. Placeholder or quote mismatches can break interpolation or produce awkward modal text. Because this is generated, manual edits are fragile. Full key count matching does not guarantee quality; some translated strings may still contain terminology or grammar issues.

## Test Signals
`jq` validates the file and shows 558 keys. GUI testing should switch to Bulgarian, inspect common settings/device/folder dialogs, verify placeholder substitutions, and check theme labels. Automated checks should compare key and placeholder parity with the English catalog.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-bg.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-ca.json -->
# sources/sync-backup/syncthing/gui/default/assets/lang/lang-ca.json

## Purpose
This JSON file provides Catalan translations for the Syncthing web GUI. It maps English GUI source strings to Catalan strings and includes localized theme names.

## Important APIs, Types, And Functions
The file contains 551 top-level keys, no empty string values, and one nested `theme.name` object with Catalan names for black, dark, default, and light themes. It is loaded by Angular's static translation file loader as `assets/lang/lang-ca.json`. Catalan `ca` is present in `valid-langs.js` and has a display name in `prettyprint.js`.

## Control Flow
When the selected locale is `ca`, the GUI loads this JSON file, uses English strings from templates as lookup keys, interpolates Angular values such as `{{device}}`, `{{folder}}`, and `{{version}}`, and falls back to English for missing entries. Catalan also has a related `ca@valencia` file in the language directory, but this file covers the base `ca` locale.

## State And Persistence Behavior
The file is generated static translation data and stores no user state. Browser caching can retain old translations until assets refresh. The language directory README states that Weblate is the upstream source.

## Dependencies And Integration Points
It integrates with GUI templates, Angular translate, valid language metadata, pretty-printed language names, and theme selection UI. It must maintain exact source keys and interpolation variable names to stay compatible with templates.

## Risks And Edge Cases
The key count is slightly lower than Arabic/Bulgarian in this subset, so a few strings may fall back to English. Some strings include invisible or special punctuation around interpolations, which should be checked in rendered modals. Text expansion can affect buttons and table headings. Manual changes are likely overwritten by translation automation.

## Test Signals
`jq` validates the file and reports 551 keys. GUI checks should select Catalan, exercise settings/folder/device dialogs, verify interpolation-heavy prompts, and confirm fallback behavior for any missing strings. Automated checks should compare keys and placeholders against `lang-en.json`.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/gui/default/assets/lang/lang-ca.json -->
